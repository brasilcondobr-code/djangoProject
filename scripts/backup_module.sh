#!/bin/bash

# Script de backup do BrasilCondo.
# Executa de forma segura e registra o resultado para o módulo BackupModule.
# Compatível com execucao via subprocess.run (lista estruturada, sem shell).
# Suporta execucao síncrona para desenvolvimento e preparação para futura execucao assíncrona via Celery.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_ROOT="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

# Carrega variáveis de ambiente (tenta dotenv_files primeiro, depois .env)
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

# Função para logar com prefixo
log() {
    echo "🔧 ${1}"
}

log "Iniciando backup do sistema BrasilCondo"
log "Timestamp: ${TIMESTAMP}"

# Verifica se o diretório de backups existe
if [ ! -d "${BACKUP_ROOT}" ]; then
    mkdir -p "${BACKUP_ROOT}"
fi

# --- 1. Backup do Banco de Dados PostgreSQL ---
log "1. Exportando banco de dados PostgreSQL..."

DB_PG_AVAILABLE=false
if command -v docker >/dev/null 2>&1 && [ -n "${POSTGRES_USER:-}" ] && [ -n "${POSTGRES_DB:-}" ]; then
    # Tenta detectar se o container docker está disponível
    DOCKER_STATUS=$(docker ps --filter "name=^(name)|(db)" --format '{{.Status}}' 2>/dev/null | head -1 || true)
    if [ -n "${DOCKER_STATUS}" ]; then
        DB_PG_AVAILABLE=true
    fi
fi

if [ "${DB_PG_AVAILABLE}" = true ]; then
    # Usa pg_dump via container Docker (método original)
    DB_USER="${POSTGRES_USER:-postgres}"
    DB_NAME="${POSTGRES_DB:-brasilio}"

    mkdir -p "${BACKUP_DIR}"
    if docker compose exec -T "db" pg_dump -U "${DB_USER}" "${DB_NAME}" > "${BACKUP_DIR}/db_dump.sql" 2>/dev/null; then
        log "✅ Banco de dados exportado com sucesso."
    else
        log "⚠️  Falha ao exportar banco via Docker. Tentando pg_dump localmente (se disponível)."
        # Fallback: tenta pg_dump localmente se instalado
        if command -v pg_dump >/dev/null 2>&1; then
            pg_dump -U "${DB_USER}" "${DB_NAME}" > "${BACKUP_DIR}/db_dump.sql" 2>/dev/null && \
                log "✅ Banco de dados exportado localmente." || log "❌ Falha na exportação do banco de dados."
        else
            log "⚠️  pg_dump não disponível localmente. Pular backup do banco."
        fi
    fi
else
    log "⚠️  Docker ou variáveis de banco não disponíveis. Pular backup do banco de dados."
fi

# --- 2. Backup de Arquivos de Mídia (Uploads) ---
log "2. Copiando arquivos de mídia..."

APP_CONTAINER="${APP_CONTAINER:-web}"
if [ "${DB_PG_AVAILABLE}" = true ]; then
    if docker compose cp "${APP_CONTAINER}:/app/media" "${BACKUP_DIR}/media" 2>/dev/null; then
        log "✅ Arquivos de mídia copiados."
    else
        log "⚠️  Não foi possível copiar arquivos de mídia. Pasta não encontrada ou container indisponível."
        mkdir -p "${BACKUP_DIR}/media"
    fi
else
    # Se Docker não disponível, apenas marca que não há mídia para backup neste contexto
    mkdir -p "${BACKUP_DIR}/media"
    log "⚠️  Docker não disponível. Pasta de mídia criada vazia."
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

# Cria o arquivo .tar.gz com o timestamp no nome
tar -czf "${BACKUP_ROOT}/backup_${TIMESTAMP}.tar.gz" -C "${BACKUP_ROOT}" "${TIMESTAMP}"
if [ $? -eq 0 ]; then
    log "✅ Backup compactado: ${BACKUP_ROOT}/backup_${TIMESTAMP}.tar.gz"
else
    log "❌ Falha ao compactar backup."
    # Mesmo assim, tenta registrar o que temos
    if [ -d "${BACKUP_DIR}" ]; then
        rm -rf "${BACKUP_DIR}"
    fi
    exit 1
fi

# Remove a pasta temporária, mantendo apenas o .tar.gz
rm -rf "${BACKUP_DIR}"

log "=========================================="
log "Backup concluído: ${BACKUP_ROOT}/backup_${TIMESTAMP}.tar.gz"
log "=========================================="

exit 0