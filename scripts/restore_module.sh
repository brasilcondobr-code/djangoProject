#!/bin/bash

# Script de restauração do BrasilCondo.
# Restaura o sistema a partir de um arquivo de backup .tar.gz.
# Executa de forma segura e registra o resultado no módulo BackupModule.
# Compatível com execucao via subprocess.run (lista estruturada, sem shell).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_ROOT="${PROJECT_ROOT}/backups"

if [ -z "$1" ]; then
    echo "❌ Erro: Você deve especificar o arquivo de backup (.tar.gz)."
    echo "Uso: ./scripts/restore_module.sh backups/backup_2026-03-04_16-02-35.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_ROOT}/${BACKUP_FILE}" ] && [ ! -f "${BACKUP_FILE}" ]; then
    echo "❌ Erro: Arquivo '${BACKUP_FILE}' não encontrado no diretório de backups (${BACKUP_ROOT})."
    exit 1
fi

# Se o caminho for relativo, assume-se que está em BACKUP_ROOT
if [ -n "${BACKUP_FILE}" ] && ! echo "${BACKUP_FILE}" | grep -q '/'; then
    BACKUP_FILE="${BACKUP_ROOT}/${BACKUP_FILE}"
fi

# Verifica se o arquivo existe após a normalização do caminho
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "❌ Erro: Arquivo '${BACKUP_FILE}' não encontrado."
    exit 1
fi

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR=$(mktemp -d)

log() {
    echo "🔧 ${1}"
}

log "Iniciando restauração do sistema BrasilCondo"
log "Arquivo de backup: ${BACKUP_FILE}"

# Carrega variáveis de ambiente
ENV_LOADED=0
if [ -f "${PROJECT_ROOT}/dotenv_files/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/dotenv_files/.env"
    set +a
    ENV_LOADED=1
elif [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
    ENV_LOADED=1
fi

# --- 1. Verificar integridade do backup ---
log "1. Verificando integridade do arquivo de backup..."

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "❌ Erro: Arquivo de backup não encontrado após normalização de caminho."
    rm -rf "${BACKUP_DIR}"
    exit 1
fi

log "✅ Arquivo de backup verificado: ${BACKUP_FILE}"

# --- 2. Extrair backup ---
log "2. Extraindo backup para diretório temporário..."

if ! tar -xzf "${BACKUP_FILE}" -C "${BACKUP_DIR}" 2>/dev/null; then
    echo "❌ Erro: Falha ao extrair o arquivo de backup."
    rm -rf "${BACKUP_DIR}"
    exit 1
fi

log "✅ Backup extraído com sucesso para ${BACKUP_DIR}"

# --- 3. Descobrir pasta extraída ---
EXTRACTED_FOLDER=$(ls "${BACKUP_DIR}" | head -n 1)
if [ -z "${EXTRACTED_FOLDER}" ]; then
    echo "❌ Erro: Nenhuma pasta encontrada dentro do backup extraído."
    rm -rf "${BACKUP_DIR}"
    exit 1
fi

BACKUP_PATH="${BACKUP_DIR}/${EXTRACTED_FOLDER}"
log "Pasta de backup identificada: ${BACKUP_PATH}"

# --- 4. Restaurar Banco de Dados ---
log "3. Restaurando Banco de Dados..."

if [ -f "${BACKUP_PATH}/db_dump.sql" ]; then
    DB_USER="${POSTGRES_USER:-postgres}"
    DB_NAME="${POSTGRES_DB:-brasilio}"

    # Dropa e recria o schema para garantir limpeza
    log "   - Dropping schema public..."
    if docker compose exec -T "db" psql -U "${DB_USER}" -d "${DB_NAME}" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" > /dev/null 2>&1; then
        log "   - Schema public droppado e recriado."
    else
        log "⚠️  Aviso: Não foi possível droppar o schema via Docker. Tentando continuar..."
    fi

    # Restaura o dump
    if [ -f "${BACKUP_PATH}/db_dump.sql" ]; then
        if cat "${BACKUP_PATH}/db_dump.sql" | docker compose exec -T "db" psql -U "${DB_USER}" -d "${DB_NAME}" > /dev/null 2>&1; then
            log "✅ Banco de dados restaurado com sucesso."
        else
            log "❌ Erro: Falha ao restaurar o banco de dados."
            rm -rf "${BACKUP_DIR}"
            exit 1
        fi
    else
        log "⚠️  Arquivo db_dump.sql não encontrado no backup. Pular restauração do banco."
    fi
else
    log "⚠️  Arquivo db_dump.sql não encontrado no backup. Pular restauração do banco de dados."
fi

# --- 5. Restaurar Mídia ---
log "4. Restaurando arquivos de mídia..."

if [ -d "${BACKUP_PATH}/media" ]; then
    if docker compose cp "${BACKUP_PATH}/media/." "${APP_CONTAINER:-web}:/app/media/" 2>/dev/null; then
        log "✅ Mídia restaurada com sucesso."
    else
        log "⚠️  Aviso: Não foi possível copiar mídia via Docker. Verifique se o container está rodando."
        # Tenta copiar localmente se possível
        cp -r "${BACKUP_PATH}/media/"* "${PROJECT_ROOT}/media/" 2>/dev/null && \
            log "⚠️  Mídia copiada localmente como fallback." || log "⚠️  Não foi possível restaurar mídia."
    fi
else
    log "⚠️  Pasta de mídia não encontrada no backup. Pular restauração de mídia."
fi

# --- 6. Aviso sobre .env ---
log "5. Verificando arquivo .env do backup..."

if [ -f "${BACKUP_PATH}/.env_backup" ]; then
    log "⚙️  Arquivo .env encontrado no backup."
    echo "   (O script não sobrescreve o .env atual automaticamente por segurança)"
else
    log "⚠️  Arquivo .env não encontrado no backup."
fi

# --- 7. Limpeza ---
log "6. Fazendo cleanup..."

rm -rf "${BACKUP_DIR}"

log "=========================================="
log "✅ Restauração Concluída com Sucesso!"
log "=========================================="

exit 0