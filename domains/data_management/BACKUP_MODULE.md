# Módulo 01. Backups (`backupmodule`) — BrasilCondo

App: `data_management` (Gestão de Dados) · Django 5 · PostgreSQL · Jazzmin · Celery/RabbitMQ/Flower (preparado)

---

## 1. Funcionalidades

CRUD completo do registro de backup no Django Admin/Jazzmin, com:

- **Action “Executar Backup”** — executa `scripts/backup_module.sh` (configurável), marca
  `file_url` com o `.tar.gz` gerado e transiciona o status
  (`Pendente`/`Falha` → `Em Execução` → `Concluído`/`Falha`).
- **Action “Fazer Download”** — baixa o arquivo de UM registro (streaming, validação
  de caminho no backend). Também existe URL dedicada dentro do Admin:
  `/admin/data_management/backupmodule/<id>/download/`.
- **Action “Executar Restaurar”** — exige exatamente UM registro concluído com
  arquivo válido e executa `scripts/restore_module.sh <arquivo>` (configurável).

### Formulário

- Aba **Principal**: `title`, `dateTime` (calendário), `file_url` (somente leitura),
  `description`, `is_active`.
- Aba **Auditoria**: `status` (somente leitura), `created_at`, `updated_at`.
- Campos técnicos (`file_url`, `status`, `created_at`, `updated_at`) **não estão no
  ModelForm**: POSTs adulterados são ignorados pelo Django (segurança não depende de
  `readonly` no HTML).
- Unicidade `title` + `dateTime` validada no form e por `UniqueConstraint`
  (`unique_backup_title_datetime`) no banco.

## 2. Configuração

Adicione (já feito em `project/settings.py`):

```python
BACKUP_ROOT = BASE_DIR / 'backups'                              # diretório permitido
BACKUP_SCRIPT_PATH = os.environ.get('BACKUP_SCRIPT_PATH', str(BASE_DIR / 'scripts' / 'backup_module.sh'))
BACKUP_RESTORE_SCRIPT_PATH = os.environ.get('BACKUP_RESTORE_SCRIPT_PATH', str(BASE_DIR / 'scripts' / 'restore_module.sh'))
BACKUP_EXECUTION_TIMEOUT_SECONDS = int(os.environ.get('BACKUP_EXECUTION_TIMEOUT_SECONDS', 300))
BACKUP_RESTORE_TIMEOUT_SECONDS = int(os.environ.get('BACKUP_RESTORE_TIMEOUT_SECONDS', 600))
```

### Migrations

```bash
python manage.py makemigrations data_management
python manage.py migrate data_management
```

### Docker / ambiente de execução

Os scripts do módulo (`scripts/backup_module.sh` e `scripts/restore_module.sh` —
**não** confundir com os originais `scripts/backup.sh`/`restore.sh`, usados como
referência e intocados) são **ambiente-agnósticos** e escolhem o mecanismo
disponível:

1. **Docker** (execução manual no host): `pg_dump` via container `db` + mídia via
   `docker compose cp` — mesmo fluxo dos scripts originais;
2. **Motor Python** (container `web`, onde não há `pg_dump`/`docker`):
   `scripts/backup_engine.py` (psycopg2) gera um dump de dados via `COPY`;
   na restauração o schema é recriado por `manage.py migrate` (fonte canônica),
   os dados são aplicados com FKs/triggers suspensos e as sequências são
   ajustadas automaticamente.

O artefato é um `.tar.gz` com `db_dump.sql` + `media/` + `.env_backup`, gravado em
`BACKUP_ROOT` com o nome `backup_<timestamp>.tar.gz` (o caminho relativo
`backups/backup_<ts>.tar.gz` é o que fica em `file_url`).

## 3. Estrutura implementada (Service Layer / Clean Architecture)

```
domains/data_management/
├── models/data_management_models.py        # BackupModule (+ TextChoices Status)
├── forms.py                                # BackupModuleForm (validações backend)
├── admin.py                                # BackupModuleAdmin + Actions + URL download
├── exceptions/                             # BackupException e derivadas
└── services/
    ├── backup_validation_service.py        # datas, caminhos, arquivos, scripts
    ├── backup_command_executor.py          # BackupCommandExecutor (subprocess seguro)
    ├── backup_service.py                   # transições de estado atômicas + logging
    ├── backup_execution_service.py         # orquestra backup.sh
    ├── backup_restore_service.py           # orquestra restore.sh (1 registro)
    └── backup_download_service.py          # valida e abre arquivo p/ streaming
```

Regras de segurança aplicadas: sem `os.system`, comandos em lista (sem shell),
path traversal bloqueado (resolução + contenção em `BACKUP_ROOT`), extensão
`.tar.gz`, arquivo regular/legível, URLs externas rejeitadas, execução/restore
impedidos por transição de estado atômica (anti-concorrência), restore bloqueado
enquanto houver outro restore em andamento, sem stack traces para o usuário e
logging estruturado sem segredos/caminhos sensíveis.

## 4. Decisões técnicas registradas

| Tema | Decisão |
|---|---|
| `dateTime` | Mantido **`DateField`** com o nome `dateTime` (requisito + convenção camelCase do projeto). A precisão de horário fica no nome do arquivo gerado. |
| `file_url` vazio antes do 1º backup | `CharField(255, null=False, blank=True, default='')` — string vazia = “ainda não executado”. |
| Unicidade | `UniqueConstraint(fields=['title','dateTime'], name='unique_backup_title_datetime')`. |
| `status` | `TextChoices` com `max_length=50`, padrão `Pendente`, transições centralizadas no service (update atômico). |
| Execução | Síncrona nesta versão; Service Layer desacoplado via `BackupCommandExecutor` (troca futura por Celery sem tocar no Admin). |
| Download | Validação backend + Action e view `/download/` no Admin (auth/permissões existentes; sem endpoint público). |
| Anti-concorrência | `UPDATE ... WHERE status IN (...)` condicional; falha de corrida vira exceção amigável. |
| Logs | Eventos estruturados `backup_*` no logger `data_management.backup` (console). Sem senhas/tokens/conteúdo de arquivos. |

## 5. Testes

```bash
pytest domains/data_management/tests
```

Cobrem model, form, validações, executor, execução/restore/download (com executor
fake — nenhum script real roda), Admin/Actions, view de download e páginas Jazzmin.
Segurança testada: path traversal, arquivos fora do diretório, download indisponível,
restore múltiplo bloqueado, permissões 403/404, POST adulterado ignorado.

## 6. Limitações conhecidas

1. **Restore é destrutivo**: a restauração recria o schema (`DROP SCHEMA public
   CASCADE` + `migrate`) e substitui os dados. O módulo exige registro `Concluído`
   e arquivo válido, mas **não** pede uma segunda confirmação explícita no Admin —
   para produção, adicionar etapa intermediária de confirmação (a ser feito).
2. **Dump do motor Python não é compatível com o `restore.sh` original**: o
   `db_dump.sql` do motor contém apenas dados (`COPY`); o schema vem das
   migrations. Backups gerados via Docker (`pg_dump`) são restaurados pelo
   caminho Docker do script. A restauração detecta o formato automaticamente.
3. **Tabelas fora do schema do projeto** (órfãs, sem modelo/migration) são
   preservadas no dump, mas não podem ser recarregadas após o restore (aviso
   listado durante a restauração). Ex.: `administrative_notification`,
   `data_management_auditmodule`/`data_management_restoremodule` (históricas).
4. **Bloqueio global de restores** é verificado + transição atômica por registro;
   serialização estrita entre registros diferentes será reforçada com lock
   (advisory lock) quando a execução for migrada para fila única.
5. Falha pré-existente fora do escopo: teste de `system/ConnectedUser`
   (`test_connected_user_admin_is_read_only`).

## 7. Próximos passos sugeridos (Celery/RabbitMQ/Flower)

- Tarefas idempotentes `execute_backup_task(backup_id)` e `restore_backup_task(...)`
  chamando os mesmos services; status persistido já permite acompanhamento no Flower.
- Retry controlado com `autoretry_for`, `max_retries` e timeouts; execução
  concorrente já é bloqueada pela transição de estado no banco.
- Tarefas futuras naturais: limpeza de backups antigos, verificação de integridade,
  compactação/upload para provider externo, auditoria e notificações.
