## Objective
- Entregar módulos numerados do app `parameters` via Django Admin/Jazzmin, seguindo os padrões do projeto (model + forms.py + validators + repositório + service + admin + migration + testes):
  - **"24. Opções de Pautas"** (`TopicOption`) — entregue agora.
  - **"23. Status da Assembleia"** (`AssemblyStatus`) — entregue sessão passada.
  - **"22. Tipos de Votações"** (`VotingType`) e módulo Tarefas — anteriores.

## Important Details
- Projeto: Django 5.0 + Jazzmin + PostgreSQL (Docker, user `usr_postgres`, db `db_postgres`, senha `4802%postgres`) + CKEditor (apenas `TaskForm`).
- **pytest**: some do container a cada restart → reinstalar por sessão com `pip install "pytest==9.1.1" "pytest-django==4.12.0"` (4.13.0 quebra com `AttributeError: ... '_pre_setup_ran_eagerly'`). Rodar com `--create-db`.
- Padrões do app `parameters`: `app_label='parameters'`, `db_table='parameters_*'`, `verbose_name` numerado (ex. `'24. Opção de Pauta'`), `ordering=['description']`; forms TODOS no arquivo único `forms.py` (≈460 linhas); arquitetura Repository + Service (template `voting_type_service.py`); validators em `validators/parameters_validator.py`. NÃO usar `Lower()`/CIText — descrição case-insensitive via `description__iexact` + `exclude(pk=...)` (form e repository).
- **Django 5.0**: constraints com `UniqueConstraint.condition=Q(...)` produzem mensagem padrão no `__all__` do form → usar `violation_error_message` no constraint (gera migration de recreate constraint, ex. `0030`).
- Concorrência (AssemblyStatus): constraints no banco como garantia; service captura `IntegrityError`→`ValueError` amigável; admin `save_model` em `transaction.atomic()`→`forms.ValidationError`.
- PostgreSQL `icontains` não é accent-insensitive: em testes de search usar termo SEM acento que case com substring (ex. `'anual'`), não usar form que diferencie só por acento.
- Admin: `ExportCsvMixin` padrão; slices `.get_queryset`. Cuidado ao editar `admin.py` — edição com oldString ambíguo já removeu atributos de `VotingTypeAdmin` (rever `ordering`/`fieldsets` ao final).

## Work State
### Completed
- **24. TopicOption** (AGORA): `models/topic_options.py` (description unique 255 + is_active + created_at/updated_at), `+validate_topic_option`, `TopicOptionForm`, `TopicOptionRepository`, `TopicOptionService`, `TopicOptionAdmin` (list_display/search/list_filter/readonly/list_per_page/export_as_csv), migration `0031_topicoption` criada+aplicada. Testes: model/form/admin. **Suíte parameters 127 passed** (95+32). `makemigrations --check --dry-run`: No changes detected.
- **23. AssemblyStatus** (sessão passada): flags is_pending/running/complete/active + constraints parciais running/complete com `violation_error_message`; migrations `0029`+`0030` aplicadas; service+repo+form+admin; votação também restaurada (ordering+fieldsets).
- **22. VotingType** + **Módulo Tarefas (10)**: entregues; suit tasks **47 passed**.
- Testes em `parameters`: **127 passed** (model/form/admin/service de todos os módulos-numberados).

### Active
- (nenhum — os três módulos numerados entregues e verdes)

### Blocked
- Falhas pré-existentes em `administrative` (não tocadas): Documents (`Condominium.objects.create` sem `address` obrigatório), Meters (`MeterType` usa `description` não `name`), Patrimony (test DB órfão já removido).

## Next Move
1. Próximo módulo numerado da lista (ex. 25...): replicar template VotingType/TopicOption (model → __init__ → validator → forms.py → repo → service → admin → migration → 3-4 arquivos de teste; rodar com do `--create-db`).
2. Se for mexer em `administrative`, corrigir primeiro fixtures pré-existentes (Documents/Meters/Patrimony).
3. Em toda sessão nova: reinstalar pytest pinado no container web antes de rodar testes.

## Relevant Files
- `domains/parameters/models/topic_options.py`: model TopicOption
- `domains/parameters/models/__init__.py`: importa VotingType, AssemblyStatus, TopicOption
- `domains/parameters/forms.py`: VotingTypeForm, AssemblyStatusForm, TopicOptionForm (final do arquivo)
- `domains/parameters/admin.py`: VotingTypeAdmin, AssemblyStatusAdmin (save_model c/ IntegrityError), TopicOptionAdmin
- `domains/parameters/repositories/{voting_type,assembly_status,topic_options}_repository.py`
- `domains/parameters/services/{voting_type,assembly_status,topic_options}_service.py`
- `domains/parameters/validators/parameters_validator.py`: validate_voting_type/validate_assembly_status/validate_topic_option
- `domains/parameters/migrations/0028_votingtype, 0029_assemblystatus..., 0030_...constraints, 0031_topicoption`: aplicadas
- `domains/parameters/tests/test_{voting_type,assembly_status,topic_options}_{model,form,admin,service}.py`
- Pré-existentes de referência: `domains/parameters/models/types_condominium.py`