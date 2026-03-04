#!/bin/bash

# Encerra o script imediatamente se qualquer comando falhar.
set -e

if [ -z "$1" ]; then
    echo "❌ Erro: Você deve especificar o arquivo de backup (.tar.gz)."
    echo "Uso: ./scripts/restore.sh backups/backup_2026-03-04_15-57-22.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Erro: Arquivo '$BACKUP_FILE' não encontrado."
    exit 1
fi

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

echo "🔍 Verificando containers..."
# Verifica se os containers estão rodando
if ! docker compose ps | grep -q "$DB_CONTAINER"; then
    echo "❌ Erro: Os containers não estão rodando. Execute 'docker compose up -d' primeiro."
    exit 1
fi

# Detecta automaticamente o usuário e banco configurados no container
DETECTED_USER=$(docker compose exec -T $DB_CONTAINER printenv POSTGRES_USER | tr -d '\r')
DETECTED_DB=$(docker compose exec -T $DB_CONTAINER printenv POSTGRES_DB | tr -d '\r')

# Usa os valores detectados ou define padrões se falhar
DB_USER=${DETECTED_USER:-postgres}
DB_NAME=${DETECTED_DB:-brasilio}

echo "=========================================="
echo "Iniciando Restauração"
echo "Arquivo: $BACKUP_FILE"
echo "Banco: $DB_NAME | Usuário: $DB_USER"
echo "=========================================="

echo "⚠️  ATENÇÃO: O banco de dados atual será TOTALMENTE SUBSTITUÍDO!"
read -p "Tem certeza que deseja continuar? (s/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "🚫 Restauração cancelada."
    exit 1
fi

# Cria diretório temporário
TEMP_DIR=$(mktemp -d)
echo "📂 Extraindo backup para $TEMP_DIR..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# O backup cria uma pasta com o timestamp dentro do tar. Vamos encontrá-la.
EXTRACTED_FOLDER=$(ls "$TEMP_DIR" | head -n 1)
BACKUP_PATH="$TEMP_DIR/$EXTRACTED_FOLDER"

if [ ! -f "$BACKUP_PATH/db_dump.sql" ]; then
    echo "❌ Erro: 'db_dump.sql' não encontrado dentro do backup."
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 1. Restaurar Banco de Dados
echo "♻️  Restaurando Banco de Dados..."
# Dropa o schema public e recria para garantir que não haja conflitos de tabelas existentes
docker compose exec -T $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" > /dev/null
# Restaura o dump
cat "$BACKUP_PATH/db_dump.sql" | docker compose exec -T $DB_CONTAINER psql -U $DB_USER -d $DB_NAME > /dev/null
echo "✅ Banco de dados restaurado."

# 2. Restaurar Mídia
if [ -d "$BACKUP_PATH/media" ]; then
    echo "📂 Restaurando arquivos de mídia..."
    # Copia o conteúdo da pasta media do backup para o container
    docker compose cp "$BACKUP_PATH/media/." $APP_CONTAINER:/app/media/
    echo "✅ Mídia restaurada."
else
    echo "⚠️  Pasta de mídia não encontrada no backup."
fi

# 3. Aviso sobre .env
if [ -f "$BACKUP_PATH/.env_backup" ]; then
    echo "⚙️  Arquivo .env encontrado no backup."
    echo "   (O script não sobrescreve o .env atual automaticamente por segurança)"
fi

# Limpeza
rm -rf "$TEMP_DIR"

echo "=========================================="
echo "✅ Restauração Concluída com Sucesso!"
echo "=========================================="
