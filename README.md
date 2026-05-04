# Django Project

Este repositório contém uma aplicação Django com PostgreSQL preparada para desenvolvimento usando Docker Compose.

O projeto inclui:
- backend Django em `app/`
- serviço PostgreSQL em Docker Compose
- scripts de backup e restauração em `scripts/`
- volume persistente para dados do banco em `data/postgres`
- configuração de variáveis de ambiente em `dotenv_files/.env`

## 🚀 Tecnologias usadas

- Python 3.12
- Django 5.0.3
- PostgreSQL 16
- Docker / Docker Compose
- django-jazzmin
- psycopg2

## 📁 Estrutura principal

- `docker-compose.yml` - orquestra `web` e `db`
- `Dockerfile` - imagem do container Django
- `scripts/command.sh` - script de inicialização com espera do banco, migrações e servidor
- `scripts/backup.sh` - backup automático de banco e mídia
- `scripts/restore.sh` - restauração a partir de backup gerado
- `dotenv_files/.env` - configurações de ambiente para o container
- `app/project/` - configuração Django
- `app/core`, `app/condominium`, `app/personalities`, `app/residents` - apps Django

## ⚙️ Pré-requisitos

- Docker
- Docker Compose

## 🛠️ Configuração e execução

1. Entre na pasta do projeto:

```bash
cd /home/delll/Projects/djangoProject
```

2. Verifique se `dotenv_files/.env` existe e contém as variáveis necessárias.

3. Inicie os containers:

```bash
docker compose up --build
```

O fluxo de inicialização faz:
- start do PostgreSQL
- espera pelo banco estar disponível
- `makemigrations` e `migrate`
- criação/atualização de superusuário de desenvolvimento
- start do servidor Django em `0.0.0.0:8000`

## 🌐 Acessar a aplicação

- Aplicação: `http://localhost:8000/`
- Admin Django: `http://localhost:8000/admin/`

## 🔐 Criar superusuário

O container `web` pode criar um superusuário automaticamente no `scripts/command.sh`.
Se preferir criar manualmente:

```bash
docker compose exec web python manage.py createsuperuser
```

## 📦 Variáveis de ambiente

Exemplo em `dotenv_files/.env`:

```env
SECRET_KEY=django-insecure-change-me-in-production-please-generate-a-real-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
POSTGRES_DB=db_postgres
POSTGRES_USER=usr_postgres
POSTGRES_PASSWORD=4802%postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

> Em produção, use `DEBUG=False` e atualize `SECRET_KEY` para uma chave realmente secreta.

## 📦 Comandos úteis

### Verificar migrações

```bash
docker compose exec web python manage.py showmigrations --plan
```

### Rodar testes

```bash
docker compose exec web python manage.py test
```

### Parar os containers

```bash
docker compose down
```

## 💾 Backup e restauração

### Backup

```bash
chmod +x scripts/backup.sh
./scripts/backup.sh
```

O backup será salvo em `backups/backup_YYYY-MM-DD_HH-MM-SS.tar.gz`.

### Restauração

```bash
chmod +x scripts/restore.sh
./scripts/restore.sh backups/backup_YYYY-MM-DD_HH-MM-SS.tar.gz
```

O script pedirá confirmação antes de sobrescrever o banco.

## ⚠️ Observações

- O volume do banco é `./data/postgres`.
- Caso haja erro de permissão no Postgres, verifique o dono e as permissões dessa pasta.
- `DEBUG=True` é indicado apenas para desenvolvimento.

## 📌 Resultado

Esse README documenta como iniciar, usar e manter o projeto localmente.
Se quiser, posso também adicionar uma seção de deploy ou instruções específicas para CI/CD.
