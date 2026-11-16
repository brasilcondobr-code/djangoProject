# BrasilCondo — Sistema de Gestão Condominial (djangoProject)

Sistema web de gestão condominial construído em **Django 5.0.3**, operado pelo
**Django Admin com Jazzmin**, com banco **PostgreSQL**, tarefas assíncronas em
**Celery/RabbitMQ** e ambiente completo em **Docker Compose**.

O sistema concentra cadastros, operações e rotinas de um condomínio em um único
back-office: parâmetros, condomínios, moradores, reservas, portaria, financeiro,
comunicação por e-mail, gestão de dados (backup/exportação) e recursos de sistema.

---

## 1. Visão geral

- **Produto:** BrasilCondo
- **Repositório:** `djangoProject`
- **Interface principal:** `/admin/` (Django Admin + Jazzmin)
- **Página inicial:** `/` — página simples de verificação de ambiente
- **Idioma:** Português do Brasil (`pt-br`)
- **Fuso horário:** `America/Sao_Paulo`
- **Banco:** PostgreSQL 16
- **Testes:** `pytest` + `pytest-django`, com SQLite isolado (`project/settings_test.py`)

O código é organizado por **domínio de negócio** em `domains/`, e não por tipo
técnico. Cada app contém seus próprios modelos, admin, formulários, serviços,
repositórios, validadores e testes.

---

## 2. Stack técnica

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework | Django 5.0.3 |
| Admin/UI | django-jazzmin (tema `darkly`) + Bootstrap/FontAwesome |
| Banco | PostgreSQL 16 (`psycopg2`) |
| Assíncrono | Celery + RabbitMQ + django-celery-results |
| Monitoramento de filas | Flower |
| E-mail de desenvolvimento | Mailpit (SMTP + UI web) |
| Rich text | django-ckeditor / ckeditor_uploader |
| Imagens | Pillow |
| HTTP externo | requests |
| Criptografia | cryptography |
| Infra | Docker + Docker Compose |

Versões declaradas em `requirements.txt`.

---

## 3. Arquitetura e organização

### 3.1 Diretórios principais

```text
djangoProject/
├── manage.py
├── docker-compose.yml          # web, db, rabbitmq, celery_worker, celery_beat, flower, mailpit
├── Dockerfile                  # imagem Python 3.12-slim
├── requirements.txt
├── pytest.ini                  # DJANGO_SETTINGS_MODULE=project.settings_test
├── dotenv_files/.env           # variáveis de ambiente (NÃO versionar)
├── data/
│   ├── postgres/               # volume persistente do PostgreSQL
│   └── web/                    # static e media compartilhados
├── backups/                    # backups gerados pelos scripts
├── scripts/                    # inicialização, backup, restauração e engine de backup
├── project/                    # configuração Django (settings, urls, wsgi, celery)
├── core/                       # serviços compartilhados (CPF, SMTP, validações, e-mail de teste)
├── shared/                     # bases de services/repositories/selectors e validadores comuns
├── infrastructure/             # pontos de extensão (celery, email, sms, whatsapp, storage, logging)
├── templates/                  # templates globais (admin, change_form, ações em massa)
├── locale/                     # traduções
├── domains/                    # aplicações de negócio
└── static_collected/           # destino do collectstatic
```

### 3.2 Módulos do sistema (`domains/`)

Os apps são numerados no menu do Admin pela ordem de uso:

| Nº | App (`label`) | Responsabilidade |
|---|---|---|
| 01 | `parameters` — Parâmetros | Cadastros-base: estados, endereços, tipos de condomínio, tipos de documento, tipos de ocorrência, bancos, centros de custo, status, opções de pauta, fundos, operações financeiras etc. |
| 02 | `personalities` — Personalidades | Entidades e setores de negócio (pessoas jurídicas/segmentos) |
| 03 | `condominium` — Condomínio | Condomínios propriamente ditos e colaboradores |
| 04 | `residents` — Moradores | Unidades, moradores, visitantes, veículos, animais, documentos, emergências, imobiliárias |
| 05 | `administrative` — Administrativo | Contas bancárias, patrimônio, medidores, comunicados, documentos, infrações, orçamento, plano de contas, tarefas e votações virtuais |
| 06 | `email_service` — E-mail | Configurações SMTP, perfis de uso, fila de envio e histórico de e-mails |
| 07 | `financial` — Financeiro | Acordos, rateios, transferências, caixa, cobranças, compras, empréstimos, lançamentos, pagamentos, recibos e boletos |
| 08 | `gatehouse` — Portaria | Turnos, transições de serviço, telefones úteis, encomendas, visitantes, ocorrências e malotes |
| 09 | `data_management` — Gestão de Dados | Backups, exportações, importações, integrações, logs e tarefas agendadas |
| 10 | `reservations` — Reservas | Reservas de manutenção, mudanças e locações |
| 12 | `system` — Sistema | Chamados técnicos, logs, rotinas automáticas, treinamentos, tokens de integração e usuários conectados |

> A numeração é definida em `apps.py` (`verbose_name`) e nos `verbose_name` dos modelos.

### 3.3 Camadas internas de cada domínio

Nem todos os apps usam todas as camadas, mas o padrão observado é:

```text
domains/<app>/
├── models/         # entidades e regras de persistência
├── migrations/     # histórico do schema
├── forms.py        # ModelForms com validação amigável
├── admin.py        # CRUD no Django Admin/Jazzmin
├── services/       # regras de negócio (quando há fluxo além do CRUD)
├── repositories/   # acesso a dados (quando há service layer)
├── selectors/      # consultas reutilizáveis
├── validators/     # validações de domínio
├── views.py/urls.py# apenas onde há interface própria (ex.: parâmetros e e-mail)
├── static/         # CSS/JS específicos do app
└── tests/          # testes de modelo, form, admin, service e views
```

---

## 4. Como o sistema funciona — etapas

### Etapa 1 — Inicialização do ambiente

Ao executar `docker compose up`, o serviço `web` usa `scripts/command.sh`, que:

1. aguarda o PostgreSQL aceitar conexões (`nc -z $POSTGRES_HOST $POSTGRES_PORT`);
2. executa `collectstatic --noinput`;
3. aplica as migrations com até **3 tentativas** (proteção contra corrida de inicialização);
4. cria/atualiza o superusuário padrão de desenvolvimento (`ocpcps`, senha definida no
   próprio script — **deve ser trocada em qualquer ambiente real**);
5. inicia o servidor Django em `0.0.0.0:8000`.

Os containers `celery_worker` e `celery_beat` reaproveitam o mesmo `entrypoint`
(aguardam banco e migrations) e então executam o Celery. `flower`, `rabbitmq`,
`db` e `mailpit` sobem como serviços de apoio.

### Etapa 2 — Autenticação e acesso ao Admin

1. Acesse `http://localhost:8000/admin/`.
2. Autentique-se com o superusuário de desenvolvimento ou um usuário criado
   manualmente (`createsuperuser`).
3. O Jazzmin monta o menu lateral com todos os apps/modelos registrados,
   ícones por modelo e tema escuro.
4. O middleware `ConnectedUserMiddleware` registra sessão, IP, user agent e
   última atividade em `system.ConnectedUser` a cada requisição autenticada.
5. Permissões continuam sendo as nativas do Django (`is_staff`, `is_superuser`,
   permissões por modelo/grupo). O CRUD respeita essas permissões.

### Etapa 3 — Cadastros-base (01. Parâmetros)

É o primeiro módulo a ser preenchido, pois alimenta os demais. Exemplos:

- **Localização:** Estados → Endereços
- **Condomínio:** Tipos de Condomínio → Estrutura do Condomínio
- **Pessoas:** Tipos de Morador, Tipos de Visitante/Restrição
- **Financeiro:** Tipos de Conta Bancária, Tipos de Centro de Custo, Status,
  Tipos de Conta Contábil, Grupos/Subgrupos, **Fundos** e **Operações Financeiras**
- **Administrativo:** Tipos de Bem, Categorias, Marcas, Status, Frequência de
  Manutenção, Tipos de Medidor, Tipos de Votação, Status de Assembleia,
  Opções de Pauta, Categorias de Serviço/Telefone
- **Reservas:** Tipos de Locação e Tipos de Manutenção

A maioria desses cadastros é CRUD puro no Admin, com:

- `description`/`name` obrigatório e **único** (constraint no banco);
- `is_active` com padrão `True`;
- `created_at`/`updated_at` automáticos e somente leitura;
- validação amigável no `ModelForm` (trim, duplicidade case-insensitive,
  mensagens em português).

### Etapa 4 — Condomínio, personalidades e moradores

1. **02. Personalidades:** cadastre entidades e setores de negócio.
2. **03. Condomínio:** cadastre o condomínio (tipo, estrutura e endereço) e seus
   colaboradores (com tipo de colaborador).
3. **04. Moradores:** cadastre as unidades condominiais e vincule:
   - moradores (`Resident.unit`);
   - visitantes, veículos, animais, documentos e contatos de emergência
     (`condo_unit`);
   - imobiliárias.

Essas entidades são a base para reservas, portaria, financeiro e ocorrências.

### Etapa 5 — Operação diária

| Módulo | O que é feito |
|---|---|
| **05. Administrativo** | Contas bancárias, patrimônio, medidores, comunicados, documentos, infrações, orçamento, plano de contas, tarefas (com ações em massa) e **votações virtuais** (pautas, participantes e anexos) |
| **07. Financeiro** | Acordos, rateios, transferências, caixa, cobranças, compras, empréstimos, lançamentos, pagamentos, recibos e boletos |
| **08. Portaria** | Turnos e escalas, transições de serviço, telefones úteis, encomendas (com itens/fotos), visitantes, ocorrências e malotes |
| **10. Reservas** | Reservas de manutenção, mudança e locação |

### Etapa 6 — Comunicação e e-mails (06. E-mail + Celery)

Fluxo de envio:

1. Configure um `SMTPConfiguration` (host, porta, TLS/SSL, credenciais) e um
   `UsageProfiles` no Admin.
2. Mensagens entram em `ShippingQueue` (assunto, destinatário, prioridade,
   perfil, status).
3. As ações do Admin permitem **enfileirar envio**, **reprocessar**,
   **cancelar**, **marcar como enviado** e **exportar logs** (esta última ainda
   como placeholder no código).
4. A ação *Realizar envio* enfileira cada item em `process_single_email_task`;
   o processamento em lote usa `process_email_queue_task`. Ambos rodam no
   Celery, com até 3 tentativas e `countdown` de 60 s em caso de erro.
5. `EmailHistory` registra o resultado, tempo de resposta e ID da mensagem no
   provedor.

**Votações virtuais:** o Celery Beat executa a cada 60 segundos a tarefa
`process_pending_virtual_meeting_emails`, que localiza `ScheduledTaskModule`
pendentes com `scheduled_at <= agora`, dispara um envio por agendamento e um
envio individual por destinatário. Status, tentativas, último erro e ID da
tarefa ficam registrados.

Em desenvolvimento, todos os e-mails caem no **Mailpit** (`http://localhost:8025`),
sem sair para a internet.

### Etapa 7 — Gestão de dados (09. Gestão de Dados)

- **01. Backups:** CRUD + ações *Executar Backup*, *Download* e *Restaurar*.
  A lógica fica em `services/` e usa `scripts/backup_module.sh` /
  `scripts/restore_module.sh` / `scripts/backup_engine.py`.
- **02. Exportações:** configuração por condomínio/grupo/módulo/formato
  (CSV/XLSX) + ação *Exportar dados* (enfileirada no Celery via
  `run_export_task`) e *Download do arquivo*.
- **03. Importações** e **04. Integrações:** CRUD administrativo.
- **05. Tarefas Agendadas:** somente leitura no Admin; alimenta o fluxo de
  e-mails das votações virtuais.
- **Logs:** eventos de criação/edição/exclusão/execução são registrados pelos
  services para auditoria.

### Etapa 8 — Sistema (12. Sistema)

- **Chamados técnicos**, **logs do sistema**, **rotinas automáticas**,
  **treinamentos**, **tokens de integração** e **usuários conectados**.
- O endpoint `GET /admin/condo-indicators/` devolve contadores de unidades,
  colaboradores, moradores, veículos, animais e entidades.
- Endpoints de clima em `/admin/weather/`, `/admin/weather-cities/` e
  `/admin/weather-by-ip/` atuam como proxy da API HG Brasil (evitando CORS).

### Etapa 9 — Manutenção e evolução

1. Alterou modelo? `makemigrations` → revise a migration → `migrate`.
2. Rode os testes (`pytest`) antes de commit.
3. Faça backup antes de mudanças estruturais.
4. Use `docker compose logs -f web` (ou `celery_worker`) para diagnosticar.
5. Consulte `project.md` para arquitetura, decisões e roadmap.

---

## 5. Fluxo de dados (resumo)

```text
Navegador
   │
   ▼
Django Admin (Jazzmin) ──► views/forms ──► services ──► repositories/ORM
   │                                                        │
   │                                                        ▼
   │                                                   PostgreSQL
   │
   └── ações assíncronas ──► Celery (RabbitMQ) ──► worker/beat
                                   │                 │
                                   │                 ├─► SMTP (Mailpit em dev)
                                   │                 └─► arquivos de exportação em media/exports
                                   └──► Flower (monitoramento)
```

---

## 6. Execução local

### Pré-requisitos

- Docker e Docker Compose
- (Opcional, para testes no host) Python 3.12 + `venv` com as dependências

### Subir a stack

```bash
cd /home/delll/Projects/djangoProject
docker compose up --build      # primeira execução
docker compose up -d           # execuções seguintes
```

### Verificar

```bash
docker compose ps
docker compose logs -f web
curl -I http://localhost:8000/
```

> Na primeira subida o servidor pode demorar alguns segundos enquanto executa
> `collectstatic` e `migrate`. Se receber “Empty reply from server”, aguarde e
> tente novamente.

### Comandos úteis

```bash
# migrations
docker compose exec web python manage.py showmigrations
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# verificação do projeto
docker compose exec web python manage.py check

# superusuário manual
docker compose exec web python manage.py createsuperuser

# shell Django
docker compose exec web python manage.py shell

# parar tudo (mantém volumes)
docker compose down
```

---

## 7. URLs e portas

| Serviço | URL / porta |
|---|---|
| Aplicação (home) | http://localhost:8000/ |
| Django Admin | http://localhost:8000/admin/ |
| Flower (Celery) | http://localhost:5555/ |
| RabbitMQ (management) | http://localhost:15672/ (5672 para AMQP) |
| Mailpit (UI) | http://localhost:8025/ |
| Mailpit (SMTP) | `localhost:1025` |
| PostgreSQL | `localhost:5432` |

> As portas `1025` e `8025` do Mailpit são as mais sujeitas a conflito com
> outros projetos locais. Se outra stack já as utiliza, pare-a ou remapeie as
> portas no `docker-compose.yml` e no `.env`.

---

## 8. Variáveis de ambiente

Arquivo: `dotenv_files/.env` (não versionar; use como referência o próprio
arquivo do ambiente).

| Variável | Uso |
|---|---|
| `SECRET_KEY` | Chave secreta do Django (obrigatória em produção) |
| `DEBUG` | `True` apenas em desenvolvimento |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Credenciais do banco |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Conexão (`db:5432` no Compose) |
| `HYDRACPF_API_KEY` | Validação de CPF via serviço Hydra |
| `EMAIL_PROVIDER` | Provedor lógico de e-mail |
| `EMAIL_BACKEND` | Backend Django de e-mail |
| `EMAIL_HOST`, `EMAIL_PORT` | Servidor SMTP (Mailpit em dev) |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Segurança do SMTP |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Credenciais SMTP |
| `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL` | Remetentes padrão |
| `CELERY_BROKER_URL` | Broker (padrão `amqp://guest:guest@rabbitmq:5672//`) |
| `CELERY_RESULT_BACKEND` | Resultados (padrão `django-db`) |
| `BACKUP_SCRIPT_PATH`, `BACKUP_RESTORE_SCRIPT_PATH` | Scripts usados pelo módulo de backup |
| `BACKUP_EXECUTION_TIMEOUT_SECONDS`, `BACKUP_RESTORE_TIMEOUT_SECONDS` | Timeouts de backup/restauração |
| `EXPORT_ROOT`, `EXPORT_TASK_TIMEOUT_SECONDS` | Diretório e timeout de exportações |
| `CONNECTED_USER_TIMEOUT`, `CONNECTED_USER_ACTIVITY_UPDATE_INTERVAL`, `CONNECTED_USER_POLL_INTERVAL` | Controle de “usuários conectados” |

---

## 9. Testes

O projeto usa **pytest** com `pytest-django`:

```bash
venv/bin/python -m pytest
```

Configuração (`pytest.ini` + `project/settings_test.py`):

- banco **SQLite** isolado para testes;
- `ALLOWED_HOSTS=['*']`;
- `MEDIA_ROOT` temporário;
- Celery em modo **eager** e broker em memória (sem RabbitMQ);
- descoberta de arquivos `test_*.py` e `tests.py`.

Exemplos:

```bash
# um app
venv/bin/python -m pytest domains/parameters/tests -q

# um arquivo
venv/bin/python -m pytest domains/financial/tests/test_xxx.py -v

# uma classe/teste
venv/bin/python -m pytest domains/parameters/tests -q -k admin
```

> `pytest` não faz parte da imagem Docker (`requirements.txt`); por isso os
> testes são executados no host com a `venv`. O comando antigo
> `manage.py test` usaria o PostgreSQL de desenvolvimento e não é o fluxo
> configurado.

---

## 10. Migrations

- Ficam em `domains/<app>/migrations/`.
- A aplicação aplica migrations automaticamente na subida (`scripts/command.sh`).
- Para criar uma migration:

```bash
docker compose exec web python manage.py makemigrations <app>
docker compose exec web python manage.py migrate <app>
```

- Antes de aplicar em produção, **revise** a migration e faça backup.
- Unicidades devem ser definidas **uma única vez** (`unique=True` **ou**
  `UniqueConstraint`, nunca os dois para a mesma regra).
- O warning `staticfiles.W004` (`/app/domains/gatehouse/static` em
  `STATICFILES_DIRS`) e `ckeditor.W001` são avisos pré-existentes de
  configuração, não erros de migration.

---

## 11. Backup e restauração

### Pelo terminal

```bash
chmod +x scripts/backup.sh scripts/restore.sh

# backup (banco + media + .env) → backups/backup_YYYY-MM-DD_HH-MM-SS.tar.gz
./scripts/backup.sh

# restauração (pede confirmação; SUBSTITUI o banco atual)
./scripts/restore.sh backups/backup_YYYY-MM-DD_HH-MM-SS.tar.gz
```

### Pelo Admin

Em **09. Gestão de Dados → 01. Backups**, use as ações:

- **Executar Backup** — gera o arquivo via `backup_module.sh`;
- **Fazer Download** — baixa o arquivo gerado;
- **Executar Restaurar** — restaura a partir do backup selecionado.

> Backups incluem o `.env`. Armazene-os com acesso restrito.

---

## 12. Tarefas assíncronas

| Componente | Função |
|---|---|
| `celery_worker` | Executa tarefas (e-mails, exportações, agendamentos) |
| `celery_beat` | Dispara tarefas periódicas |
| `rabbitmq` | Broker das mensagens |
| `flower` | Interface de monitoramento em `:5555` |
| `django_celery_results` | Persiste resultados no banco |

Tarefas registradas no código:

- `domains.administrative.tasks.virtual_meeting_email_tasks.process_pending_virtual_meeting_emails`
  (Beat, a cada 60 s);
- `send_virtual_meeting_email` e `send_virtual_meeting_recipient_email`;
- `domains.email_service.tasks.process_email_queue_task` e `process_single_email_task`;
- `domains.data_management.tasks.export_tasks.run_export_task`.

---

## 13. Solução de problemas

| Sintoma | Causa provável / solução |
|---|---|
| `Empty reply from server` logo após `up` | Aplicação ainda executando `collectstatic`/`migrate`. Aguarde e recarregue. |
| `relation "...does not exist"` | Migration pendente: `docker compose exec web python manage.py migrate`. |
| `Bind for 0.0.0.0:1025 failed: port is already allocated` | Outro projeto usa as portas do Mailpit. Pare-o ou remapeie `1025/8025`. |
| `DisallowedHost` / erro de CSRF | Ajuste `ALLOWED_HOSTS` e, se necessário, `CSRF_TRUSTED_ORIGINS` no `.env`. |
| Aviso de “orphan containers” | Container antigo de outro compose. Use `docker compose up -d --remove-orphans` se desejar limpar. |
| Erro de permissão em `data/postgres` | Verifique dono/permissões da pasta (o Postgres precisa escrever nela). |
| CSS/JS desatualizados no Admin | `docker compose exec web python manage.py collectstatic --noinput` e recarregue com cache limpo. |
| Testes falhando por banco | Confirme que está usando `pytest` (SQLite de teste) e não o banco de desenvolvimento. |
| `connection ... /var/run/postgresql/.s.PGSQL.5432` no host | Comandos `manage.py` devem rodar no container (`docker compose exec web ...`). |

---

## 14. Segurança e boas práticas

- **Nunca** versione `dotenv_files/.env` nem backups (contêm segredos).
- Troque a senha do superusuário padrão e a `SECRET_KEY` fora do ambiente local.
- Em produção: `DEBUG=False`, `ALLOWED_HOSTS` restrito e HTTPS.
- O Admin é a interface administrativa: restrinja o acesso por rede/autenticação.
- Valide dados no backend; constraints no banco são a última linha de defesa.
- Faça backup antes de migrations destrutivas ou restaurações.
- Não remova dados de produção para “resolver” duplicidades: trate os registros
  e depois aplique a constraint.

---

## 15. Documentação complementar

- `project.md` — arquitetura, decisões de engenharia, riscos e roadmap.
- `scripts/README.md` — detalhes de manutenção/backup.
- `Instalacao.txt` — anotações de instalação do ambiente.
- Docstrings e comentários nos módulos de `domains/`, `core/` e `shared/`.
