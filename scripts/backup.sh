#!/bin/bash

# Encerra o script imediatamente se qualquer comando falhar.
set -e

# Tenta carregar variáveis de ambiente do local correto (dotenv_files)
if [ -f ./dotenv_files/.env ]; then
    set -a
    source ./dotenv_files/.env
    set +a
elif [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Configurações do Banco de Dados
DB_CONTAINER="db"
APP_CONTAINER="web"

# Detecta automaticamente o usuário e banco configurados no container
echo "🔍 Detectando configurações do banco de dados..."
DETECTED_USER=$(docker compose exec -T $DB_CONTAINER printenv POSTGRES_USER | tr -d '\r')
DETECTED_DB=$(docker compose exec -T $DB_CONTAINER printenv POSTGRES_DB | tr -d '\r')

# Usa os valores detectados ou define padrões se falhar
DB_USER=${DETECTED_USER:-postgres}
DB_NAME=${DETECTED_DB:-brasilio}

# Diretório onde os backups serão salvos (cria uma pasta 'backups' na raiz do projeto)
BACKUP_ROOT="./backups"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo "Iniciando Backup: $TIMESTAMP"
echo "Configuração: Banco='$DB_NAME' | Usuário='$DB_USER'"
echo "=========================================="

# 1. Backup do Banco de Dados PostgreSQL
echo "📦 Exportando banco de dados..."
docker compose exec -T $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME > "$BACKUP_DIR/db_dump.sql"
echo "✅ Banco de dados exportado com sucesso."

# 2. Backup de Arquivos de Mídia (Uploads)
echo "📂 Copiando arquivos de mídia..."
docker compose cp $APP_CONTAINER:/app/media "$BACKUP_DIR/media" 2>/dev/null || echo "⚠️  Nenhuma pasta de mídia encontrada ou erro na cópia."

# 3. Backup do arquivo .env (Configurações)
if [ -f ./dotenv_files/.env ]; then
    cp ./dotenv_files/.env "$BACKUP_DIR/.env_backup"
    echo "⚙️  Arquivo .env copiado."
fi

# 4. Compactar o backup
echo "🗜️  Compactando arquivos..."
tar -czf "$BACKUP_ROOT/backup_$TIMESTAMP.tar.gz" -C "$BACKUP_ROOT" "$TIMESTAMP"
rm -rf "$BACKUP_DIR" # Remove a pasta temporária, mantendo apenas o .tar.gz

echo "✅ Backup concluído: backups/backup_$TIMESTAMP.tar.gz"
