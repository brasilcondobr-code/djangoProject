#!/bin/bash

# Script de restauração do BrasilCondo (módulo 01. Backups — backupmodule).
#
# Restaura um backup .tar.gz gerado pelo backup_module.sh:
#   - dump do motor Python (backup_engine.py): DROP SCHEMA + `manage.py
#     migrate` (recria o schema) + load dos dados + ajuste de sequências;
#   - dump via Docker (pg_dump): mesmo fluxo do restore.sh original (psql
#     dentro do container `db`).
#
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

# Aceita caminho relativo (interpretado dentro de BACKUP_ROOT) ou absoluto.
if [ ! -f "${BACKUP_FILE}" ] && [ -f "${BACKUP_ROOT}/${BACKUP_FILE}" ]; then
    BACKUP_FILE="${BACKUP_ROOT}/${BACKUP_FILE}"
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "❌ Erro: Arquivo '${BACKUP_FILE}' não encontrado."
    exit 1
fi

# Carrega variáveis de ambiente
if [ -f "${PROJECT_ROOT}/dotenv_files/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/dotenv_files/.env"
    set +a
elif [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-brasilio}"

log() { echo "🔧 ${1}"; }

# Detecta um interpretador Python com psycopg2 + Django
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

docker_available() {
    command -v docker >/dev/null 2>&1 || return 1
    docker compose ps >/dev/null 2>&1 || return 1
    return 0
}

fail() {
    log "❌ ${1}"
    exit 1
}

BACKUP_DIR=$(mktemp -d)
trap 'rm -rf "${BACKUP_DIR}"' EXIT

log "Iniciando restauração do sistema BrasilCondo"
log "Arquivo de backup: ${BACKUP_FILE}"

# --- 1. Verificar integridade e extrair ---
log "1. Verificando integridade do arquivo de backup..."
if ! tar -xzf "${BACKUP_FILE}" -C "${BACKUP_DIR}" 2>/dev/null; then
    fail "Falha ao extrair o arquivo de backup."
fi
log "✅ Backup extraído com sucesso."

EXTRACTED_FOLDER=$(ls "${BACKUP_DIR}" | head -n 1)
if [ -z "${EXTRACTED_FOLDER}" ]; then
    fail "Nenhuma pasta encontrada dentro do backup extraído."
fi
BACKUP_PATH="${BACKUP_DIR}/${EXTRACTED_FOLDER}"
if [ ! -f "${BACKUP_PATH}/db_dump.sql" ]; then
    fail "'db_dump.sql' não encontrado dentro do backup."
fi
log "Pasta de backup identificada: ${BACKUP_PATH}"

# --- 2. Restaurar Banco de Dados ---
log "2. Restaurando Banco de Dados..."

if grep -q "backup_engine.py" "${BACKUP_PATH}/db_dump.sql"; then
    # Dump gerado pelo motor Python: schema via migrations + dados via COPY.
    PYTHON_BIN="$(detect_python)" || \
        fail "Este backup exige Python+psycopg2 (dump do motor Python)."
    log "   - Dump do motor Python detectado (schema via migrations)."

    log "   - Recriando schema public..."
    "${PYTHON_BIN}" "${SCRIPT_DIR}/backup_engine.py" drop-schema || \
        fail "Falha ao recriar o schema public."

    log "   - Aplicando migrations (schema canônico)..."
    ( cd "${PROJECT_ROOT}" && "${PYTHON_BIN}" manage.py migrate --noinput ) || \
        fail "Falha ao aplicar as migrations."

    log "   - Carregando dados..."
    "${PYTHON_BIN}" "${SCRIPT_DIR}/backup_engine.py" load "${BACKUP_PATH}/db_dump.sql" || \
        fail "Falha ao restaurar os dados."

    log "   - Ajustando sequências..."
    "${PYTHON_BIN}" "${SCRIPT_DIR}/backup_engine.py" fix-sequences || \
        fail "Falha ao ajustar as sequências."
    log "✅ Banco de dados restaurado."
else
    # Dump via Docker (pg_dump) — mesmo fluxo do restore.sh original.
    if ! docker_available; then
        fail "Este backup foi gerado via Docker (pg_dump) e exige Docker para restaurar."
    fi
    log "   - Dump pg_dump detectado (restauração via container db)."
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" \
        -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" >/dev/null 2>&1 || \
        fail "Falha ao recriar o schema public."
    cat "${BACKUP_PATH}/db_dump.sql" | \
        docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" >/dev/null 2>&1 || \
        fail "Falha ao restaurar o dump."
    log "✅ Banco de dados restaurado."
fi

# --- 3. Restaurar Mídia ---
log "3. Restaurando arquivos de mídia..."
if [ -d "${BACKUP_PATH}/media" ]; then
    if docker_available; then
        if docker compose cp "${BACKUP_PATH}/media/." web:/app/media/ 2>/dev/null; then
            log "✅ Mídia restaurada (via container)."
        else
            log "⚠️  Não foi possível copiar mídia via Docker. Tentando cópia local..."
            cp -r "${BACKUP_PATH}/media/." "${PROJECT_ROOT}/media/" 2>/dev/null && \
                log "⚠️  Mídia copiada localmente (fallback)." || \
                log "⚠️  Não foi possível restaurar mídia."
        fi
    else
        if cp -r "${BACKUP_PATH}/media/." "${PROJECT_ROOT}/media/" 2>/dev/null; then
            log "✅ Mídia restaurada."
        else
            log "⚠️  Não foi possível restaurar mídia."
        fi
    fi
else
    log "⚠️  Pasta de mídia não encontrada no backup. Pular restauração de mídia."
fi

# --- 4. Aviso sobre .env ---
log "4. Verificando arquivo .env do backup..."
if [ -f "${BACKUP_PATH}/.env_backup" ]; then
    log "⚙️  Arquivo .env encontrado no backup."
    log "   (O script não sobrescreve o .env atual automaticamente por segurança)"
else
    log "⚠️  Arquivo .env não encontrado no backup."
fi

log "=========================================="
log "✅ Restauração Concluída com Sucesso!"
log "=========================================="

exit 0