#!/bin/bash

# Script de backup do BrasilCondo (módulo 01. Backups — backupmodule).
#
# Estratégia de execução (ambiente-agnóstico):
#   1. Docker disponível (host)        -> pg_dump via container `db` (método original);
#   2. Python + psycopg2 disponível    -> backup_engine.py (container `web`, sem pg_dump);
#   3. Nenhum mecanismo                -> falha controlada com mensagem clara.
#
# Compatível com execucao via subprocess.run (lista estruturada, sem shell).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_ROOT="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

# Carrega variáveis de ambiente (dotenv_files/.env primeiro, depois .env)
if [ -f "${PROJECT_ROOT}/dotenv_files/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/dotenv_files/.env"
    set +a
elif [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

log() { echo "🔧 ${1}"; }

# Detecta um interpretador Python com psycopg2 + Django (necessário p/ engine e migrate)
detect_python() {
    for cand in python3 python "${PROJECT_ROOT}/venv/bin/python"; do
        if command -v "$cand" >/dev/null 2>&1 && \
           "$cand" -c "import psycopg2, django" >/dev/null 2>&1; then
            echo "$cand"
            return 0
        fi
    done
    return 1
}

# Docker CLI disponível E containers do projeto no ar?
docker_available() {
    command -v docker >/dev/null 2>&1 || return 1
    docker compose ps >/dev/null 2>&1 || return 1
    return 0
}

# ---------------------------------------------------------------------------
# Seleção do mecanismo de backup do banco
# ---------------------------------------------------------------------------
MODE=""
if docker_available; then
    MODE="docker"
elif PYTHON_BIN="$(detect_python)"; then
    MODE="engine"
else
    log "❌ Nenhum mecanismo de backup disponível (Docker, pg_dump ou Python+psycopg2)."
    exit 1
fi

log "Iniciando backup do sistema BrasilCondo"
log "Timestamp: ${TIMESTAMP}"
log "Mecanismo de banco: ${MODE}"

if [ ! -d "${BACKUP_ROOT}" ]; then
    mkdir -p "${BACKUP_ROOT}"
fi

DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-brasilio}"

# --- 1. Backup do Banco de Dados PostgreSQL ---
log "1. Exportando banco de dados PostgreSQL..."
mkdir -p "${BACKUP_DIR}"

if [ "${MODE}" = "docker" ]; then
    if docker compose exec -T db pg_dump -U "${DB_USER}" "${DB_NAME}" \
        > "${BACKUP_DIR}/db_dump.sql" 2>/dev/null; then
        log "✅ Banco de dados exportado via Docker (pg_dump)."
    else
        log "❌ Falha ao exportar o banco via Docker."
        rm -rf "${BACKUP_DIR}"
        exit 1
    fi
else
    if "${PYTHON_BIN}" "${SCRIPT_DIR}/backup_engine.py" dump "${BACKUP_DIR}/db_dump.sql"; then
        log "✅ Banco de dados exportado (mecanismo Python)."
    else
        log "❌ Falha ao exportar o banco de dados."
        rm -rf "${BACKUP_DIR}"
        exit 1
    fi
fi

# --- 2. Backup de Arquivos de Mídia (Uploads) ---
log "2. Copiando arquivos de mídia..."
if [ "${MODE}" = "docker" ]; then
    if docker compose cp web:/app/media "${BACKUP_DIR}/media" 2>/dev/null; then
        log "✅ Arquivos de mídia copiados."
    else
        log "⚠️  Não foi possível copiar arquivos de mídia. Pasta criada vazia."
        mkdir -p "${BACKUP_DIR}/media"
    fi
else
    if [ -d "${PROJECT_ROOT}/media" ]; then
        cp -r "${PROJECT_ROOT}/media" "${BACKUP_DIR}/media"
        log "✅ Arquivos de mídia copiados."
    else
        mkdir -p "${BACKUP_DIR}/media"
        log "⚠️  Pasta de mídia não encontrada. Pasta criada vazia."
    fi
fi

# --- 3. Backup do arquivo .env (Configurações) ---
log "3. Copiando arquivo de configuração .env..."
if [ -f "${PROJECT_ROOT}/dotenv_files/.env" ]; then
    cp "${PROJECT_ROOT}/dotenv_files/.env" "${BACKUP_DIR}/.env_backup"
    log "⚙️  Arquivo .env copiado."
elif [ -f "${PROJECT_ROOT}/.env" ]; then
    cp "${PROJECT_ROOT}/.env" "${BACKUP_DIR}/.env_backup"
    log "⚙️  Arquivo .env copiado."
else
    log "⚠️  Arquivo .env não encontrado. Pular etapa."
fi

# --- 4. Compactar o backup ---
log "4. Compactando arquivos backup..."
if tar -czf "${BACKUP_ROOT}/backup_${TIMESTAMP}.tar.gz" \
    -C "${BACKUP_ROOT}" "${TIMESTAMP}"; then
    log "✅ Backup compactado: backups/backup_${TIMESTAMP}.tar.gz"
else
    log "❌ Falha ao compactar backup."
    rm -rf "${BACKUP_DIR}"
    exit 1
fi

# Remove a pasta temporária, mantendo apenas o .tar.gz
rm -rf "${BACKUP_DIR}"

log "=========================================="
log "Backup concluído: backups/backup_${TIMESTAMP}.tar.gz"
log "=========================================="

exit 0