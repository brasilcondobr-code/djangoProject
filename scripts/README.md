# Manutenção de banco — `scripts/vacuum.sh`

Script de manutenção periódica para recuperar espaço físico das tabelas do app
`data_management` (e de qualquer prefixo configurável) no banco dev, eliminando
o bloat deixado por experimentos (EXPLAIN com datasets sintéticos descartados
via `ROLLBACK`), `UPDATE`s frequentes e exclusões.

Seguindo o padrão de `scripts/backup.sh` e `scripts/restore.sh`, o script
detecta automaticamente o usuário e o banco a partir do container `db` do
`docker compose` — não é preciso informar credenciais.

## Requisitos

- Containers rodando (`docker compose up -d`).
- `bash`, `docker`/`docker compose` disponíveis no host.
- Somente para uso em ambiente **dev** com o modo `full` (ver “Modos”).

## Uso

```bash
# VACUUM FULL + ANALYZE nas tabelas data_management_* (padrão, recomendado no dev)
./scripts/vacuum.sh

# Modo plain (VACUUM comum, bloqueia menos — indicado para produção)
./scripts/vacuum.sh --mode plain

# Diagnóstico: lista tabelas com desperdício acima do threshold (NÃO executa VACUUM)
./scripts/vacuum.sh --check
./scripts/vacuum.sh --check --threshold 30    # threshold em % (padrão 20)
./scripts/vacuum.sh --check --min-size 5      # ignora tabelas < 5 MB (padrão 1)

# Prefixo diferente de tabelas
./scripts/vacuum.sh --prefix data_management

# Tabelas específicas
./scripts/vacuum.sh --tables "data_management_scheduledtaskmodule data_management_backupmodule"

# Ajuda
./scripts/vacuum.sh --help
```

No modo manutenção, o script imprime, ao final, um relatório com o tamanho de
cada tabela **antes → depois** e o espaço recuperado (por tabela e total).

### Modo `--check` (diagnóstico de bloat)

Lista somente as tabelas cujo **desperdício** (percentual do arquivo que o
`VACUUM FULL` recuperaria) é `>= threshold` e cujo tamanho é `>= min-size`:

- **bloat** — tuples mortos (atualizações/exclusões ainda não varridos);
- **livres** — páginas alocadas mas vazias (ex.: dados inseridos e descartados
  via `ROLLBACK`, como os experimentos de EXPLAIN);
- **desperdício** = bloat + livres (o que o FULL devolve ao sistema).

A medição usa a extensão **`pgstattuple`** (`pgstattuple_approx`, amostral e
sem locks), criada automaticamente no banco; se não houver permissão para
criar a extensão, o script cai na heurística de `pg_stat_user_tables`
(`n_dead_tup`, sem a coluna “livres”) e avisa qual fonte foi usada.

**Códigos de saída do `--check`:** `0` = nenhuma tabela acima do threshold;
`2` = há tabelas com desperdício relevante (útil para agendamento condicional).
O relatório ainda sugere o comando exato de `--mode full` para as tabelas
apontadas.

## Agendamento periódico (cron)

Exemplo — manutenção semanal do bloat no dev, domingo às 3h:

```cron
0 3 * * 0  cd /home/delll/Projects/djangoProject && ./scripts/vacuum.sh >> /var/log/vacuum.log 2>&1
```

Se preferir manutenção diária sem bloqueio pesado (tabelas com escrita
constante), use `--mode plain` no agendamento e reserve o `--mode full` para
rodadas manuais quando o `--check` indicar bloat relevante:

```cron
30 3 * * *  cd /home/delll/Projects/djangoProject && ./scripts/vacuum.sh --mode plain >> /var/log/vacuum.log 2>&1
```

Diagnóstico automático seguido de VACUUM condicional (só roda `--mode full`
quando o `--check` apontar desperdício ≥ 20%):

```cron
0 3 * * 0  cd /home/delll/Projects/djangoProject && ./scripts/vacuum.sh --check --threshold 20 || ./scripts/vacuum.sh --mode full >> /var/log/vacuum.log 2>&1
```

> Nota: o `||` também dispara se o `--check` falhar por erro (ex.: container
> parado), então a linha acima pressupõe que o banco está no ar no horário
> agendado; o próprio `--mode full` também valida o container antes de agir.

Na prática, um fluxo mais seguro para produção é: `--check` diário registra o
bloat em log, e o operador decide a janela de manutenção para o `--mode full`
com base no relatório.

## Modos e recomendações

| Modo | Comando | Bloqueio | Recomendado para |
|---|---|---|---|
| `full` | `VACUUM (FULL, ANALYZE)` | `ACCESS EXCLUSIVE` (tabela fica indisponível durante a reescrita) | Dev, rodadas manuais, tabelas pequenas |
| `plain` | `VACUUM (ANALYZE)` | `SHARE UPDATE EXCLUSIVE` (permite leitura/escrita concorrente) | Produção, agendamento periódico |
| `check` | — (somente leitura) | nenhum (`pgstattuple_approx` amostral) | Qualquer ambiente, para decidir quando rodar `full` |

Considerações:

- **`VACUUM FULL` reescreve a tabela e os índices** e toma lock exclusivo:
  somente execute com a aplicação parada ou fora do horário de pico, e nunca em
  produção sem janela de manutenção.
- Para produção, o caminho correto é o **`plain`** (o `autovacuum` do PostgreSQL
  já cobre a maior parte da rotina; o `FULL` só se justifica quando o bloat é
  confirmado e o espaço físico precisa ser devolvido ao sistema operacional).
- O script sempre roda com `ANALYZE`, atualizando as estatísticas do planner
  após a reescrita da tabela.
- Se alguma das tabelas não puder ser bloqueada (conexão ativa), o `VACUUM`
  falha e o script encerra com código de saída diferente de zero — nada é
  executado parcialmente de forma silenciosa.
- O `--check` não altera nada no banco, exceto a criação da extensão
  `pgstattuple` (uma única vez, idempotente) para a medição amostral.