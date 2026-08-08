## Objective
- Entregar módulo **"23. Status da Assembleia"** (`AssemblyStatus`) no app `parameters`, seguindo os padrões do projeto (model + forms.py + validators + repositório + service + admin + migration + testes).
- Contexto concluído: módulo Tarefas e módulo **"22. Tipos de Votações"** (`VotingType`) entregues.

## Important Details
- Projeto: Django 5.0 + Jazzmin + PostgreSQL (Docker, user `usr_postgres`, db `db_postgres`, senha `4802%postgres`) + CKEditor (apenas `TaskForm`).
- **pytest**: instalado *dentro* do container web a cada sessão (some no restart). **Versão que funciona: `pytest==9.1.1` + `pytest-django==4.12.0`** (4.13.0 quebra com `AttributeError: ... '_pre_setup_ran_eagerly'`). Rodar com `--create-db`.
- Padrões do app `parameters`: models com `app_label='parameters'`, `db_table='parameters_*'`, `verbose_name` numerado (ex. `'23. Status da Assembleia'`), `ordering=['description']`; forms centralizados em `forms.py` (arquivo único de ~430 linhas, sem subdiretório); arquitetura Repository + Service (`voting_type_service.py` é o template); validators em `validators/parameters_validator.py`. NÃO usar `Lower()` no banco — descrição case-insensitive é verificada no form/repository via `description__iexact` com `exclude(pk=...)`.
- **Django 5.0**: `ModelForm._post_clean` roda `instance.validate_constraints()`; constraints com `UniqueConstraint.condition=Q(...)` produzem erro `<constraint_name> restrição foi violada` no `__all__` do form — para mensagem amigável usar `violation_error_message` no próprio `UniqueConstraint` (a migração resultante remove/cria as constraints • gera migration `0030`).
- Concorrência: garantia definitiva nas constraints no banco (`unique_running_assembly_status`, `unique_complete_assembly_status`); service captura `IntegrityError` → `ValueError` amigável; admin `save_model` em `transaction.atomic()` captura `IntegrityError` → `forms.ValidationError` (Django 5 display).
- Estados entre flags NÃO são mutuamente exclusivos (não foram pedidas `CheckConstraint` — decisão documentada; múltiplos `is_pending=True` permitidos).

## Work State
### Completed
- **Módulo Tarefas (10)**: Task/TaskHistory, inline add-only, `save_formset`, actions bulk (status/completação), TaskService. Migrations `0024`/`0025`. **47 passed**.
- **Módulo 22 VotingType**: model/form/repository/service/admin, migration `0028_votingtype`. Migration cleaner + `parameters.0027` (fix colunas) + `0026` (Meta options). Suíte voting **44 passed** no início da sessão.
- **Módulo 23 AssemblyStatus**:
  - `models/assembly_status.py`: description (unique, 255), is_pending=True, is_running=False, is_complete=False, is_active=True, created_at/updated_at; constraints parciais running/complete com `violation_error_message`.
  - `validators/parameters_validator.py`: `validate_assembly_status`.
  - `forms.py`: `AssemblyStatusForm` (placeholders, help_texts, checkboxes, case-insensitive). – `repositories/assembly_status_repository.py`: CRUD + `description_exists/running_exists/complete_exists`.
  - `services/assembly_status_service.py`: normalize, validate_status_flags, create/update/delete/toggle_active, IntegrityError→friendly, transaction.atomic, logging sem dados sensíveis.
  - `admin.py`: `AssemblyStatusAdmin` (form, list_display, list_filter, search, ordering, readonly audit, list_per_page=25, export_as_csv, `save_model` com IntegrityError handling). Foi também **reparada a `VotingTypeAdmin`** (perdera `ordering` e fieldsets durante edições).
  - Testes `test_assembly_status_{model,form,service,admin}.py`.
  - Migrations: `0029_assemblystatus_and_more` (CreateModel + constraints) e `0030_...constraints...` (recreate ao adicionar `violation_error_message`), aplicadas.
  - **Suíte parameters completa: 95 passed** (voting+assembly+restante). `makemigrations --check --dry-run parameters`: No changes detected.

### Active
- (nenhum — módulo entregue)

### Blocked
- Falhas pré-existentes em `administrative` NO relacionadas a hoje: Documents (testes criam `Condominium.objects.create(name=...)` sem `address` obrigatório → NotNullViolation), Meters (`MeterType` usa `description` não `name`), Patrimony (test DB órfão `test_db_postgres`, já removido). `makemigrations` global — ainda em dívida (avançar `administrative` em outra passada).

## Next Move
1. (ime vazio — produção pronta). Opções: correlativos talks em try unsolved `administrative` (441 pre-existent), ou via web validar o admin no browse manual, ou iniciar próximo módulo da lista replicando o template.
2. Em futuras sessões, reinstalar no container web: `pip install "pytest==9.1.1" "pytest-django==4.12.0"`.

## Relevant Files
- `domains/parameters/models/assembly_status.py`: model + constraints parciais
- `domains/parameters/models/__init__.py`: +AssemblyStatus
- `domains/parameters/forms.py`: AssemblyStatusForm (ao final)
- `domains/parameters/services/assembly_status_service.py`: service
- `domains/parameters/repositories/assembly_status_repository.py`: repository
- `domains/parameters/validators/parameters_validator.py`: +validate_assembly_status
- `domains/parameters/admin.py`: AssemblyStatusAdmin + VotingTypeAdmin restaurada (ordering+fieldsets)
- `domains/parameters/migrations/0029_assemblystatus_and_more.py` e `0030_...constraints`: migrations aplicadas
- `domains/parameters/tests/test_assembly_status_{model,form,admin,service}.py`: testes
- `domains/parameters/tests/test_voting_type_*.py`: referência da suíte