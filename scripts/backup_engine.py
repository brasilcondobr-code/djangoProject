#!/usr/bin/env python3
"""
Mecanismo de dump/restore do PostgreSQL para o módulo 01. Backups (data_management).

Motivação: dentro do container `web` não existe `pg_dump`, `psql` nem o CLI do
Docker. Este módulo produz um backup do banco usando apenas `psycopg2` (já
instalado na imagem), conectando diretamente ao PostgreSQL pela rede interna.

Formato do artefato (`db_dump.sql`):
  - dados de todas as tabelas do schema `public` via `COPY ... FROM STDIN`;
  - o SCHEMA NÃO é serializado aqui: ele é recriado na restauração pelas
    migrations do Django (`manage.py migrate`), que são a fonte canônica do
    schema deste projeto;
  - tabelas gerenciadas automaticamente pelo Django são excluídas do dump
    (`django_migrations`, `django_content_type`, `auth_permission`,
    `django_admin_log`) — elas são regeneradas pela migração;
  - após o load, as sequências são corrigidas (`fix-sequences`).

Uso:
  backup_engine.py dump <arquivo.sql>
  backup_engine.py drop-schema
  backup_engine.py load <arquivo.sql>
  backup_engine.py fix-sequences

As credenciais são lidas das variáveis POSTGRES_* (mesmas usadas pelo Django e
carregadas pelos scripts bash do módulo).
"""

import os
import re
import sys
from datetime import datetime, timezone

import psycopg2

# Tabelas de runtime gerenciadas pelo Django: recriadas pela migração.
EXCLUDED_TABLES = frozenset(
    {
        'django_migrations',
        'django_content_type',
        'auth_permission',
        'django_admin_log',
    }
)

# ---------------------------------------------------------------------------
# Tabelas gerenciadas (o que o `manage.py migrate` recria no restore)
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def managed_tables():
    """
    Tabelas que pertencem ao schema do projeto (modelos + M2M automáticas).

    O schema é recriado pelas migrations na restauração; portanto, apenas
    estas tabelas entram no dump. Tabelas órfãs no banco (removidas do
    código, criadas manualmente etc.) são ignoradas com aviso.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    import django

    django.setup()
    from django.apps import apps

    tables = set()
    for model in apps.get_models():
        if not model._meta.managed:
            continue
        tables.add(model._meta.db_table)
        for field in model._meta.local_many_to_many:
            tables.add(field.m2m_db_table())
    return tables


# ---------------------------------------------------------------------------
# Conexão
# ---------------------------------------------------------------------------
def db_params():
    """Lê as credenciais do ambiente (mesmas do dotenv_files/.env)."""
    return {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': int(os.environ.get('POSTGRES_PORT', '5432')),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', ''),
        'dbname': os.environ.get('POSTGRES_DB', 'brasilio'),
    }


def connect():
    return psycopg2.connect(**db_params())


def _public_tables(conn):
    """Lista (ordenada) das tabelas de usuário do schema public."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.relname
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind = 'r'
              AND c.relname NOT LIKE 'pg_%'
            ORDER BY c.relname
            """
        )
        return [row[0] for row in cur.fetchall()]


def _table_columns(conn, table):
    """Colunas de uma tabela, na ordem física (para o COPY)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.attname
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = %s
              AND a.attnum > 0
              AND NOT a.attisdropped
            ORDER BY a.attnum
            """,
            (table,),
        )
        return [row[0] for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# dump
# ---------------------------------------------------------------------------
def cmd_dump(output_path):
    params = db_params()
    conn = connect()
    try:
        all_tables = _public_tables(conn)
        tables = [t for t in all_tables if t not in EXCLUDED_TABLES]
        # Nota informativa (drift): tabelas sem modelo correspondente no código
        # atual. Os dados são preservados no dump; na restauração, a carga só
        # aplica as tabelas que o schema (migrations) recriar.
        managed = managed_tables()
        no_model = sorted(
            t for t in tables
            if t not in managed and t not in EXCLUDED_TABLES
        )
        if no_model:
            print(
                'ℹ️  Tabelas sem modelo no código atual (dados preservados): '
                + ', '.join(no_model)
            )
        header = [
            '-- ============================================================',
            '-- Dump gerado pelo backup_engine.py (módulo 01. Backups)',
            f'-- Gerado em: {datetime.now(timezone.utc).isoformat()}',
            f'-- Banco: {params["dbname"]}',
            '-- Formato: dados via COPY; schema recriado via `manage.py migrate`.',
            '-- ============================================================',
            'SET statement_timeout = 0;',
            '',
        ]
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write('\n'.join(header))
            for table in tables:
                columns = _table_columns(conn, table)
                cols = ', '.join(f'"{c}"' for c in columns)
                stmt = (
                    f'COPY public."{table}" ({cols}) FROM STDIN '
                    'WITH (FORMAT csv);'
                )
                out.write(stmt + '\n')
                with conn.cursor() as cur:
                    cur.copy_expert(
                        f'COPY public."{table}" ({cols}) TO STDOUT '
                        'WITH (FORMAT csv)',
                        out,
                    )
                out.write('\\.\n')
            out.write('\n')
        print(f'✅ Dump gravado: {output_path} ({len(tables)} tabelas)')
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# drop-schema
# ---------------------------------------------------------------------------
def cmd_drop_schema():
    conn = connect()
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute('DROP SCHEMA public CASCADE')
            cur.execute('CREATE SCHEMA public')
        print('✅ Schema public recriado.')
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------
def cmd_load(input_path):
    """
    Aplica um arquivo de dump do backup_engine.py.

    O arquivo é interpretado linha a linha: blocos `COPY ... FROM STDIN;`
    são carregados via copy_expert (Streaming); demais linhas SQL são
    executadas normalmente. O load roda com `session_replication_role =
    replica`, desabilitando temporariamente FKs/triggers (ordem das tabelas
    independe das dependências).
    """
    if not os.path.exists(input_path):
        sys.exit(f'❌ Arquivo de dump não encontrado: {input_path}')

    with open(input_path, 'r', encoding='utf-8') as fh:
        content = fh.read()

    if 'FROM STDIN' not in content:
        sys.exit(
            '❌ O arquivo informado não parece ser um dump do backup_engine '
            '(sem blocos COPY). Backups gerados via Docker (pg_dump) devem '
            'ser restaurados pelo caminho Docker do script de restauração.'
        )

    conn = connect()
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute('SET session_replication_role = replica')
            lines = content.splitlines(keepends=True)
            i = 0
            tables = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                if stripped.startswith('COPY ') and ' FROM STDIN' in line:
                    stmt = line.strip()
                    rows = []
                    i += 1
                    while i < len(lines) and lines[i].strip() != '\\.':
                        rows.append(lines[i])
                        i += 1
                    i += 1  # pula o '\\.'
                    from io import StringIO

                    try:
                        cur.copy_expert(stmt, StringIO(''.join(rows)))
                        tables += 1
                    except psycopg2.errors.UndefinedTable:
                        # Tabela existe no dump mas não foi recriada pelas
                        # migrations (schema antigo/órfão): preserva o dado no
                        # arquivo, mas não é possível aplicá-lo.
                        table_name = stmt.split()[1]
                        print(
                            f'⚠️  Tabela {table_name} não existe no schema '
                            'restaurado; dados mantidos apenas no arquivo.'
                        )
                elif not stripped or stripped.startswith('--'):
                    i += 1  # linha em branco ou comentário
                else:
                    cur.execute(line)
                    i += 1
            cur.execute('SET session_replication_role = DEFAULT')
        print(f'✅ Dados restaurados de: {input_path} ({tables} tabelas)')
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# fix-sequences
# ---------------------------------------------------------------------------
def cmd_fix_sequences():
    """
    Ajusta as sequências para continuar após o maior id existente.

    Cobre tanto colunas `serial` (default nextval) quanto colunas IDENTITY
    (Django 5 gera `GENERATED BY DEFAULT AS IDENTITY` para AutoFields).
    """
    conn = connect()
    try:
        with conn.cursor() as cur:
            # Sequências ligadas a colunas (serial via default nextval OU
            # IDENTITY): a dependência aparece em pg_depend (sequence -> coluna).
            cur.execute(
                """
                SELECT c.relname, a.attname,
                       sn.nspname || '.' || quote_ident(seq.relname)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                JOIN pg_attribute a ON a.attrelid = c.oid
                JOIN pg_depend dep ON dep.refobjid = c.oid
                                  AND dep.refobjsubid = a.attnum
                                  AND dep.classid = 'pg_class'::regclass
                                  AND dep.refclassid = 'pg_class'::regclass
                JOIN pg_class seq ON seq.oid = dep.objid
                JOIN pg_namespace sn ON sn.oid = seq.relnamespace
                WHERE n.nspname = 'public'
                  AND c.relkind = 'r'
                  AND a.attnum > 0
                  AND NOT a.attisdropped
                  AND seq.relkind = 'S'
                  AND dep.deptype IN ('a', 'i')
                """
            )
            rows = cur.fetchall()

        fixed = 0
        for table, column, sequence in rows:
            with conn.cursor() as cur:
                cur.execute(
                    f'SELECT COALESCE(MAX("{column}"), 0) FROM public."{table}"'
                )
                max_value = cur.fetchone()[0]
                if max_value > 0:
                    cur.execute('SELECT setval(%s, %s, true)', (sequence, max_value))
                else:
                    cur.execute('SELECT setval(%s, 1, false)', (sequence,))
            fixed += 1
        print(f'✅ Sequências ajustadas ({fixed}).')
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    command = argv[1]
    if command == 'dump' and len(argv) == 3:
        cmd_dump(argv[2])
    elif command == 'drop-schema':
        cmd_drop_schema()
    elif command == 'load' and len(argv) == 3:
        cmd_load(argv[2])
    elif command == 'fix-sequences':
        cmd_fix_sequences()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))