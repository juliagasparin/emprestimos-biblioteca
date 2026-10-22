# Cenário 1: detalhamento e evidências
Commit base: 9278e33

Arquivo de consulta. Resposta ao cenário está em `cenario-1-diagnostico.md`. Aqui ficam o que foi rodado, em que ordem, o que cada saída mostrou e o que cada evidência sustenta ou não.

Fontes: os transcripts `cenario-1-completo.txt` (15, 16 e 19/10) e `cenario-1-fechamento.txt` (20/10, duas sessões). Quando uma informação não está nesses transcripts, o texto diz de onde ela vem.

## Índice

1. Arquivos de evidência
2. Sessões gravadas
3. Ambiente
4. Notas de processo
5. Rodada de 15/10 (Partes 0 a 3)
6. Rodada de 16/10 (Partes 4 a 6)
7. Rodada de 19/10 (Partes 6 refeita, 7, 8 e 9)
8. Fechamento de 20/10, manhã (Blocos 0 a 6)
9. Complemento de 20/10, tarde
10. O que cada evidência sustenta
11. Achados laterais
12. Situação final das limitações

---

## 1. Arquivos de evidência

Todos em `docs/diagnostico/evidencias/`.

| Arquivo | O que é |
|---|---|
| `cenario-1-completo.txt` | Transcript de 15, 16 e 19/10 (três sessões no mesmo arquivo) |
| `cenario-1-saidas-complementares.txt` | Saídas copiadas do console em 19/10, anteriores ao `Start-Transcript` (nota e) |
| `api-completo-sem-dbname.out.log` e `.err.log` | Logs da API de 15/10, subida sem `DB_NAME` na sessão |
| `api-completo-com-dbname.out.log` e `.err.log` | Logs da API de 16/10 (PID 18092), subida com `DB_NAME=biblioteca_diag` |
| `frontend.out.log` e `.err.log` | Logs do frontend subido em 16/10 (citados no transcript; não foram abertos) |
| `Captura_de_tela_2026-10-19_085554.png` | Print da tela do frontend |
| `cenario-1-fechamento.txt` | Transcript de 20/10 (duas sessões no mesmo arquivo) |
| `pglog-fechamento.txt` | Trecho do log do Postgres a partir do offset 8637 (49 linhas) |
| `api-fechamento.out.log` e `.err.log` | Logs da API de 20/10 (PID 7748) |
| `pytest-cenario-1.txt` | Saída do pytest de `test_criar_emprestimo.py` (20/10, tarde) |

## 2. Sessões gravadas

Horários do cabeçalho de cada transcript.

| Data | Início | Fim | PID do PowerShell | Arquivo | O que cobre |
|---|---|---|---|---|---|
| 15/10 | 19:09:20 | 20:30:36 | 14704 | completo | Partes 0 a 3 |
| 16/10 | 13:58:13 | 15:13:54 | 14704 | completo | Partes 4 a 6 (a 6 ficou incompleta) |
| 19/10 | 08:42:33 | 09:34:49 | 9836 | completo | Parte 6 refeita e Partes 7 a 9 |
| 20/10 | 09:08:50 | 09:31:39 | 4128 | fechamento | Blocos 0 a 6 |
| 20/10 | 14:07:44 | 15:07:27 | 4128 | fechamento | Complemento da tarde |

## 3. Ambiente

- Windows, PowerShell 5.1.26100.9711, PostgreSQL 18 (`psql.exe` em `C:\Program Files\PostgreSQL\18\bin`), Redis em `localhost:6379`.
- Commit `9278e33` e Python 3.14.7: constam no transcript de 20/10. No transcript de 15/10 os comandos `git rev-parse`, `git status --short` e `python --version` foram executados sem `Out-Host` e a saída não aparece.
- `git status --short` em 20/10: só `?? docs/` (as evidências). Nenhum arquivo de código estava modificado.
- Pytest 9.1.1 (plugin anyio 4.14.2), visto na saída de 20/10, tarde.
- Banco `biblioteca_diag`: criado a partir do `biblioteca_schema.sql` antes do primeiro transcript (DROP e CREATE DATABASE, depois `-f biblioteca_schema.sql`), fora de qualquer transcript. O `\dt` de 15/10 lista 7 tabelas: autores, emprestimos, exemplares, livro_autor, livros, reservas, usuarios.
- `.env` (valores mostrados pelo transcript): `DB_NAME=emprestimo`, `DB_USER=postgres`, `DB_HOST=localhost`, `DB_PORT=5432`, `REDIS_HOST=localhost`, `REDIS_PORT=6379`. `DB_PASSWORD` existe na linha 3, com valor oculto.

## 4. Notas de processo

- **(a) Datas.** As Partes 4 e 5 são de 16/10, não de 15/10. Entre o fim da Parte 3 (15/10, até 20:30) e o início da Parte 4 (16/10, 13:58).
- **(b) Sessões.** Os transcripts de 15 e 16/10 têm o mesmo PID do PowerShell (14704). O de 19/10 tem outro (9836) e não mostra onde `$api`, `$psql`, `Ver-Redis` e `Esperar-Porta` foram definidos. As duas sessões de 20/10 têm o PID 4128.
- **(c) API de 16/10.** A API de PID 18092 (subida em 16/10) ainda escutava a porta 8000 em 19/10 (Parte 9). O `StartTime` não foi registrado. Um indício: o `api-completo-com-dbname.err.log` tem última escrita em 16/10 às 14:09:24, compatível com a subida nessa janela.
- **(d) Parte 6.** Foi refeita em 19/10 depois que o console travou. O print é dessa rodada.
- **(e) Antes do transcript de 19/10.** Foram executados e vistos, mas existem só no console (arquivo de saídas complementares): consulta direta ao `biblioteca_diag` com `exemplares = 2` para o livro 1; Redis sem a chave (DBSIZE 3, TTL -2) e, depois da consulta na tela, com a chave (DBSIZE 4).
- **(f) 20/10.** Houve duas sessões no mesmo dia, no mesmo PowerShell (PID 4128) e no mesmo arquivo de transcript. Na manhã o ambiente foi reconstruído do zero (funções e variáveis redefinidas, sem herdar nada de 15, 16 e 19/10). À tarde foram redefinidas só as funções `Sql`, `Ver-Linhas` e `Buscar`.
- **(g) API de 20/10.** Processo novo, PID 7748, `StartTime` 20/10 09:27:22. A porta 8000 estava livre antes de subir, então a API de 16/10 já não estava no ar.
- **(h) log_statement.** Ligado só no `biblioteca_diag` e só durante o experimento. Revertido com `RESET log_statement`. A `pg_db_role_setting` terminou vazia.
- **(i) Log do Postgres.** O prefixo é `%t` (só data e hora). Não tem banco, usuário nem PID. A atribuição do banco é por escopo da configuração e por controle, não pelo texto das linhas.
- **(j) Filtro do Bloco 5.** A tela exibiu só do primeiro ao último marcador. As 49 linhas estão em `pglog-fechamento.txt`.
- **(k) Busca por `DISPONIVEL`.** O comando `Buscar` de 20/10 não usa `-CaseSensitive`, por isso traz também `Indisponivel`, `indisponivel` e `disponivel`. A de 19/10 usava `-CaseSensitive`. O `git grep` (que diferencia maiúsculas) mostra a linha única.
- **(l) Texto digitado.** Na Pausa 2 de 19/10, o texto `Total=2; Disponiveis=0; Em estoque=Não` foi digitado por mim a partir do que vi na tela. O transcript registra o que foi digitado, não capturou a tela.
- **(m) Erro aparente.** No INSERT rejeitado de 20/10, o bloco `NativeCommandError` é o PowerShell embrulhando o stderr do `psql` (por causa do `2>&1`). O erro do banco é a linha `ERRO: a nova linha ... viola a restrição de verificação "ck_status_exemplar_valido"`.
- **(n) Acentos.** Nas saídas do `psql` de 20/10 (por exemplo `\d exemplares`) e na exibição do `pytest.ini` os acentos aparecem corrompidos, mesmo com `[Console]::OutputEncoding` em UTF-8. Observado; a causa não foi verificada.

## 5. Rodada de 15/10 (Partes 0 a 3)

**Parte 0: ambiente.** Data (quinta-feira, 15/10, 19:09:50). `PGPASSWORD definida: True`, `DB_PASSWORD definida na sessão: False`, `DB_PASSWORD presente no .env (valor oculto)`. Funções `Ver-Redis` (mostra DBSIZE, chaves `disponibilidade:*`, TTL e valor da chave do livro 1) e `Esperar-Porta` definidas.

**Parte 1: banco.** `\dt` lista 7 tabelas. Inserido 1 livro (id 1, "Dom Casmurro") e 2 exemplares (`PAT-001` e `PAT-002`, status `ATIVO`).

```
SELECT id, livro_id, status FROM exemplares;
 id | livro_id | status
  1 |        1 | ATIVO
  2 |        1 | ATIVO

SELECT COUNT(*) AS emprestimos FROM emprestimos;
 0
```

Consulta de referência (exemplares `ATIVO` sem empréstimo em aberto, `devolvido_em IS NULL`):

```
 livro_id | disponiveis
        1 |           2
```

**Parte 2: Redis inicial.** `DBSIZE 3`, nenhuma chave `disponibilidade:*`, `TTL -2`, valor `None`. As três chaves existentes são `_kombu.binding.celery`, `_kombu.binding.celery.pidbox` e `_kombu.binding.celeryev`.

**Parte 3: API sem `DB_NAME` na sessão.**
- `DB_NAME=[]`. Nada escutando na porta 8000.
- `api/main.py` lê `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `REDIS_HOST` e `REDIS_PORT` com `os.getenv`, e carrega o `.env` com `load_dotenv` (linha 8).
- No banco `emprestimo`, `SELECT COUNT(*) FROM exemplares WHERE livro_id = 1` devolve `1`.
- API subida (PID 14472), porta 8000 escutando após 1 s. Redis antes da chamada: sem chave.
- `GET /disponibilidade/1` devolve `{"livro_id":1,"total":1,"disponiveis":0,"em_estoque":false}`.
- Redis depois: DBSIZE 4, chave criada, TTL 58, mesmo valor.

Leitura: sem `DB_NAME` na sessão, a API usou o `DB_NAME=emprestimo` do `.env` e devolveu `total: 1`. É inferência pelo total (o `emprestimo` tem 1 exemplar e o `biblioteca_diag` tem 2).

## 6. Rodada de 16/10 (Partes 4 a 6)

**Parte 4: TTL.** `Start-Sleep 65` e depois `Ver-Redis`: DBSIZE 3, sem a chave, TTL -2. A chave criada em 15/10 (com `total: 1`) já tinha expirado.

**Parte 5: API com `DB_NAME=biblioteca_diag`.**
- `Stop-Process -Id 14472` falhou com "Não é possível localizar um processo". O comentário no transcript explica que a API anterior foi encerrada com o fechamento da sessão do terminal. A porta 8000 estava livre (confirmado por `Get-NetTCPConnection`).
- `$env:DB_NAME = "biblioteca_diag"` e nova API (PID 18092), porta escutando após 0 s.
- Redis antes: sem chave. `GET /disponibilidade/1` devolve `{"livro_id":1,"total":2,"disponiveis":0,"em_estoque":false}`.
- Redis depois: DBSIZE 4, chave criada, TTL 51, mesmo valor.
- 5a, `pg_stat_activity`: mostra só a conexão do próprio `psql` (pid 7860, banco `postgres`). Inconclusivo para provar o banco da API. Uma explicação provável, não testada: `obter_conexao` fecha a conexão ao fim de cada requisição.

**Parte 6: frontend (interrompida).**
- `/openapi.json` lista uma única rota: `['/disponibilidade/{livro_id}']`.
- O frontend chama a rota em `frontend/src/App.tsx`, linha 28: `fetch(\`http://localhost:8000/disponibilidade/${livroIdInput}\`)`.
- Porta 5173 não estava escutando. Frontend subido com `npm.cmd run dev` e logs em `frontend.out.log` e `frontend.err.log`. Porta escutando após 2 s. A sessão terminou aqui (a parte foi refeita em 19/10).

## 7. Rodada de 19/10 (Partes 6 refeita, 7, 8 e 9)

**Parte 6 refeita.** Mesmas rotas e mesma chamada na linha 28 do `App.tsx`. Frontend subido em janela própria (`cmd /k ... npm run dev`), porta 5173 escutando após 0 s.
- Pausa 1: consulta do livro 1 na página. Redis logo depois: DBSIZE 4, chave `disponibilidade:livro:1`, TTL 53, valor `{"livro_id": 1, "total": 2, "disponiveis": 0, "em_estoque": false}`.
- Pausa 2: texto digitado a partir da tela: `Total=2; Disponiveis=0; Em estoque=Não` (nota l).
- Print: `Captura_de_tela_2026-10-19_085554.png` (barra de endereço em `localhost:5173`, campo com `1`, cartão "Status do Livro #1", Total de exemplares 2, Disponíveis para empréstimo 0, Em estoque Não ❌). O horário está só no nome do arquivo.

**Parte 7: código-fonte.**
- Linhas do `repositorios_postgres.py` com `disponiveis|DISPONIVEL|esta_disponivel`: 33, 43, 45, 50, 51, 67, 78 e 79.
- Linhas 26 a 54 (`buscar_disponibilidade`): o SELECT conta `COUNT(*) AS total` e `COUNT(*) FILTER (WHERE status = 'DISPONIVEL') AS disponiveis` da tabela `exemplares` para o `livro_id`, e devolve `em_estoque: disponiveis > 0`.
- Linhas 67 a 80 (`esta_disponivel`): `SELECT NOT EXISTS (SELECT 1 FROM emprestimos WHERE exemplar_id = %s AND devolvido_em IS NULL)`.
- Encoding do arquivo: lido como ANSI (Windows-1252) mostra `disponÃ­veis`; lido como UTF-8 mostra `disponíveis`. O arquivo está em UTF-8 (inferido pelo contraste).
- SQL rodada no `biblioteca_diag` equivalente à do repositório (não idêntica): `total = 2`, `disponiveis = 0`.

**Parte 8: schema.**
- `biblioteca_schema.sql` com "status": linha 45 (`status VARCHAR(20) NOT NULL DEFAULT 'ATIVO'`), 47 e 48 (`ck_status_exemplar_valido`, `status IN ('ATIVO', 'BAIXADO', 'PERDIDO')`), 57, 60, 61 (`ck_status_reserva_valido`), 68 e 93.
- Busca por `DISPONIVEL` com `-CaseSensitive` em `.py`, `.sql`, `.md`, `.js`, `.jsx`, `.yml` e `.yaml` (fora de `node_modules`, `.git`, venv e `docs\diagnostico`): uma única ocorrência, `repositorios_postgres.py:33`.

**Parte 9: logs e encerramento.**
- `api-completo-com-dbname.err.log`: 202 bytes, última escrita 16/10 14:09:24. Conteúdo: processo 18092 iniciado, "Application startup complete", "Uvicorn running on http://127.0.0.1:8000".
- `api-completo-com-dbname.out.log`: 545 bytes, última escrita 19/10 08:52:57. Tem 8 requisições, todas `200 OK`: 5 de `GET /disponibilidade/1` e 3 de `GET /openapi.json`, de rodadas diferentes e sem horário por linha.
- Antes de encerrar, a porta 8000 era escutada pelo processo 18092.
- `Stop-Process -Id $api.Id` executou sem a mensagem de `$api` indefinida, e a porta 8000 ficou livre depois. Isso é compatível com `$api` apontar para a API que estava no ar. O valor de `$api` não foi impresso.
- `PGPASSWORD` removida da sessão e `Stop-Transcript`.

## 8. Fechamento de 20/10, manhã (Blocos 0 a 6)

**Bloco 0: iniciação.** Pasta, encoding UTF-8, `Start-Transcript`, data (20/10, 09:09:06), commit `9278e33`, `?? docs/`, Python 3.14.7. Senha lida via `SecureString`. Funções `Sql`, `Ver-Redis`, `Limpar-Redis`, `Esperar-Porta`, `Ver-Linhas` e `Buscar` definidas.

**Bloco 1: restrição de status.**
- `biblioteca_schema.sql`, linhas 41 a 50: `CREATE TABLE exemplares` contém `status VARCHAR(20) NOT NULL DEFAULT 'ATIVO'` e `CONSTRAINT ck_status_exemplar_valido CHECK (status IN ('ATIVO', 'BAIXADO', 'PERDIDO'))`.
- `\d exemplares` no `biblioteca_diag` lista a mesma restrição.
- `pg_constraint` devolve uma única linha, com `tabela = exemplares`.

**Bloco 2: rota e métodos (evidência A, estática).**
- `api/main.py`, linhas 51 a 58: a rota `/disponibilidade/{livro_id}` cria `RepositorioExemplarPostgres(conexao)`, passa-o ao `RepositorioExemplarCache(repo_postgres, redis_client)` e este a `ConsultarDisponibilidade`, e chama `executar(livro_id)`. As linhas 60 e 61 devolvem 404 se `total == 0`.
- `consultar_disponibilidade.py`, linha 10: `executar` só repassa a chamada a `buscar_disponibilidade` do repositório recebido.
- `esta_disponivel` tem definições em `dominio/repositorios.py:33`, `repositorios_postgres.py:67`, `repositorio_exemplares_cache.py:46 e 47` (só delega) e `teste/test_criar_emprestimo.py:25`. Nenhum arquivo do caminho da rota chama `esta_disponivel`.
- `invalidar_disponibilidade` é chamado em `criar_emprestimo.py:73` e `devolver_exemplar.py:27`.

**Bloco 3: cache e configuração do log.**
- `repositorio_exemplares_cache.py`, linhas 17 a 35: tenta o Redis primeiro (linhas 21 a 23); no miss, chama `repositorio_real.buscar_disponibilidade` (linha 26); grava com `setex` e TTL padrão de 60 s (linhas 9 e 29).
- Postgres: `logging_collector = on`, `log_directory = log`, `data_directory = C:/Program Files/PostgreSQL/18/data`, `log_line_prefix = %t`, `log_timezone = America/Sao_Paulo`, `log_statement = none`. Arquivo de log atual: `log/postgresql-2026-10-15_031827.log`.

**Bloco 4: experimento.**
- `ALTER DATABASE biblioteca_diag SET log_statement = 'all'`. `pg_db_role_setting` mostra a configuração só nesse banco. Offset do log antes das chamadas: 8637.
- `DB_NAME=biblioteca_diag`, porta 8000 livre, API subida (PID 7748, `StartTime` 09:27:22), porta escutando após 4 s.
- Três chamadas a `GET /disponibilidade/1`, cada uma precedida de um `SELECT 'MARCADOR_n_...'` no `biblioteca_diag`:

| Chamada | Redis antes | Resposta | Redis depois | SELECT no log |
|---|---|---|---|---|
| 1 (`MARCADOR_1`, 09:27:32) | `DEL` -> 0, DBSIZE 3, sem chave, TTL -2 | `{"livro_id":1,"total":2,"disponiveis":0,"em_estoque":false}` | DBSIZE 4, chave criada, TTL 58 | sim, 09:27:34 |
| 2 (`MARCADOR_2`, 09:27:37) | chave existente | mesmo JSON | DBSIZE 4, mesmo valor, TTL 55 | nenhum até `MARCADOR_3` (09:27:44) |
| 3 (`MARCADOR_3`, 09:27:44) | `DEL` -> 1, DBSIZE 3, sem chave | mesmo JSON | DBSIZE 4, chave recriada, TTL 58 | sim, 09:27:44 |

- Controle no banco `emprestimo`: `SELECT 'CONTROLE_emprestimo_nao_deve_aparecer'`. Marcador final `MARCADOR_4_fim` (09:27:47).

**Bloco 5: log do Postgres (evidência B, execução).** Em cada uma das chamadas 1 e 3 aparece `BEGIN` seguido de:

```sql
SELECT
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'DISPONIVEL') AS disponiveis
FROM exemplares
WHERE livro_id = $1;      -- Parameters: $1 = '1'
```

Contagem de `CONTROLE_emprestimo` no log: 0. Das 49 linhas lidas, os marcadores estão nas posições 0, 20, 22 e 42 (`MARCADOR_1`, `MARCADOR_2`, `MARCADOR_3`, `MARCADOR_4_fim`).

**Bloco 6: desfazer e encerrar.**
- `ALTER DATABASE biblioteca_diag RESET log_statement`. `pg_db_role_setting` com `LEFT JOIN` devolve 0 linhas.
- API parada, porta 8000 sem escuta.
- `api-fechamento.out.log`: 3 requisições `GET /disponibilidade/1`, todas `200 OK`. `api-fechamento.err.log`: processo 7748 iniciado e Uvicorn em `127.0.0.1:8000`.
- `PGPASSWORD` e `DB_NAME` removidas da sessão.

**Conclusões do fechamento da manhã.**
- **Origem da resposta.** Nas chamadas 1 e 3 a chave não existia e o Postgres executou o SELECT. Na chamada 2 o TTL passou de 58 para 55 (a chave não foi recriada), a resposta foi idêntica e o log não registrou SELECT. A resposta da chamada 2 veio do cache.
- **Por que a tela mostra `Disponíveis = 0`.** A única SQL de disponibilidade que rodou usa `status = 'DISPONIVEL'`, valor que o schema não permite. O resultado `disponiveis = 0` vem da resposta da API; a mesma consulta rodada direto no banco em 19/10 também deu 0.
- **Banco usado pela API.** O `log_statement = 'all'` está só no `biblioteca_diag` e o controle no `emprestimo` tem 0 ocorrências no log. Logo, os SELECTs registrados vieram de sessões no `biblioteca_diag`. A API abre uma conexão nova a cada requisição (`obter_conexao` chama `psycopg.connect`), então todas as chamadas pegaram a configuração já ligada. É argumento por escopo da configuração, não pelo texto do log.
- **Ressalva.** O log não tem PID nem `application_name`, então não identifica quem enviou o SELECT. A atribuição à API se apoia em três coisas: o SELECT aparece cerca de 2 s depois de cada marcador, no instante do `curl`; o `api-fechamento.out.log` tem exatamente 3 requisições; e a porta 8000 estava livre antes de subir a API. Não é um identificador do cliente.

## 9. Complemento de 20/10, tarde

Sessão de 14:07 a 15:07, mesmo commit `9278e33`, `?? docs/`, Python 3.14.7.

**Definição de "disponível" no domínio e na documentação.**
- `dominio/repositorios.py`, linhas 27 a 47: `esta_disponivel` é abstrato e sem docstring. `buscar_disponibilidade` tem a docstring "Retorna a contagem total e disponíveis para o livro." e não define o critério.
- Busca por "dispon" nos `.md`: o `README.md` tem, na linha 106, o título "Decisão: disponibilidade derivada, não armazenada", e na linha 108 o início da frase "Em vez de uma coluna `disponivel`, a disponibilidade de um exemplar é calculada pela..." (a busca mostra só a linha 108, e o restante da frase não foi exibido). Também aparecem as seções da Etapa 8 (React) e da Parte 2 (cache, Redis, TTL de 60 s).
- `esta_disponivel` em `repositorios_postgres.py` (linhas 67 a 79) é a única implementação que traduz "disponível" em regra: exemplar sem empréstimo em aberto.

**Como o frontend rotula o resultado** (`frontend/src/App.tsx`, linhas 40 a 90): mostra `resultado.total` como "Total de exemplares", `resultado.disponiveis` como "Disponíveis para empréstimo" e `resultado.em_estoque` como "Sim ✅" ou "Não ❌". Não recalcula nada: exibe o que a API devolve.

**Busca ampliada por `DISPONIVEL`.**
- Extensões buscadas: `*.py *.sql *.md *.js *.jsx *.ts *.tsx *.yml *.yaml *.json *.html *.css *.toml *.cfg *.ini *.txt`. Sem `-CaseSensitive` (nota k), por isso aparecem também `ExemplarIndisponivelError` (`criar_emprestimo.py`, `test_criar_emprestimo.py`), `testar_integracao_fallback_indisponivel` (`teste_integracao_prazo_remoto.py`) e `disponivel` (README e `esta_disponivel`).
- `git grep -n -I "DISPONIVEL"` (arquivos versionados, qualquer extensão, diferencia maiúsculas): uma única linha, `arquitetura/infraestrutura/repositorios_postgres.py:33`.

**Origem dos `_kombu.*` no Redis.** Busca por `celery|kombu` nos `.py`: `celery_app.py` (`from celery import Celery`, `app = Celery(`, `from celery.schedules import crontab`, host e porta do Redis) e `infraestrutura/tasks.py` (`from celery_app import app`). Confirma que o projeto usa Celery; a ligação direta das chaves `_kombu.*` com ele continua sendo inferência pelos nomes.

**Rejeição de `'DISPONIVEL'` pelo schema.** INSERT de teste no `biblioteca_diag`, com id 999 explícito para não consumir a sequência:

```
INSERT INTO exemplares (id, livro_id, codigo_patrimonio, status)
VALUES (999, 1, 'PAT-TESTE-REJEICAO', 'DISPONIVEL');
ERRO: a nova linha da relação "exemplares" viola a restrição de verificação "ck_status_exemplar_valido"
DETALHE: Registro que falhou contém (999, 1, PAT-TESTE-REJEICAO, DISPONIVEL, 2026-10-20).
```

Conferência depois: `SELECT COUNT(*) FROM exemplares WHERE livro_id = 1` continua em 2 (`total_depois_da_rejeicao = 2`).

**Histórico no git.**

| Consulta | Resultado |
|---|---|
| `git log --follow -- biblioteca_schema.sql` | `223dfc5` (2026-08-12), "refactor: reestrutura projeto para Clean Architecture com testes unitarios" |
| `git log --all -S"DISPONIVEL" -- repositorios_postgres.py` | `089c5b9` (2026-09-23), "Etapa 7 - Processamento Assíncrono" |
| `git blame -L 33,33 repositorios_postgres.py` | linha 33 de `089c5b9`, 2026-09-23 10:41:05 -0300 |
| `git blame -L 67,79 repositorios_postgres.py` | `esta_disponivel` de `223dfc5` (2026-08-12), marcado com `^` |
| `git blame -L 45,48 biblioteca_schema.sql` | linhas 45 a 48 de `223dfc5` (2026-08-12), marcado com `^` |

O diff do `089c5b9` não foi aberto, então não se sabe o que a linha 33 era antes. O significado do `^` no `blame` (commit de fronteira) não foi verificado neste repositório.

**Testes.**
- `testar_cache_fluxo.py` fica em `arquitetura/` (fora de `arquitetura/teste`). Lido por inteiro (76 linhas). Usa `psycopg` e `redis` reais (`RepositorioExemplarPostgres`, `RepositorioExemplarCache` com TTL 60, `ConsultarDisponibilidade`). Para o livro 1 faz quatro passos (1ª consulta, 2ª consulta, invalidação e consulta após invalidar), imprime o resultado e o tempo de cada um e termina com "TESTE CONCLUÍDO COM SUCESSO". Não tem `assert` nem valor esperado. A função se chama `rodar_teste`.
- `test_criar_emprestimo.py`, linhas 1 a 60: o comentário inicial fala em "repositórios falsos". `RepositorioExemplarFake` (linhas 18 a 32) devolve `True` em `esta_disponivel` e `None` em `buscar_disponibilidade`; `invalidar_disponibilidade` não faz nada. `RepositorioReservaFake` começa na linha 40.
- Busca por "disponi" em todos os `.py`: nenhuma chamada de teste a `buscar_disponibilidade` real. As ocorrências nos testes são o fake (`test_criar_emprestimo.py:25, 28, 31`), `ExemplarIndisponivelError` e o script manual.
- Arquivos com nome `test_*.py` ou `*_test.py`: só `test_criar_emprestimo.py` (a saída do transcript trunca o nome).
- `arquitetura/pytest.ini`: `python_files = test_*.py testar_*.py teste_integracao_*.py`, `python_functions = test_* testar_*`, `testpaths = arquitetura/teste`, e os marcadores `unitario` e `integracao`.
- Variáveis na sessão: `DB_NAME` vazia (o `.env` tem `DB_NAME=emprestimo`), `DB_PASSWORD`, `DB_PASS` e `DATABASE_URL` não definidas.
- `PYTHONPATH` apontado para `arquitetura` só nesta sessão. Pytest rodado só em `test_criar_emprestimo.py` (caminho explícito):

```
collected 7 items
test_criar_emprestimo_sem_reserva_funciona PASSED
test_criar_emprestimo_com_reserva_coerente_funciona PASSED
test_criar_emprestimo_com_reserva_de_outro_usuario_falha PASSED
test_criar_emprestimo_com_reserva_de_outro_livro_falha PASSED
test_criar_emprestimo_com_reserva_cancelada_falha PASSED
test_criar_emprestimo_com_reserva_ja_atendida_falha PASSED
test_criar_emprestimo_exemplar_ja_emprestado_falha PASSED
7 passed in 0.11s
```

O pytest completo (sem caminho) não foi rodado.

**Comparação das duas definições no mesmo banco** (`biblioteca_diag`, livro 1):

```
 por_status | por_emprestimo_aberto
          0 |                     2
```

`por_status` é `status = 'DISPONIVEL'` (regra do `buscar_disponibilidade`). `por_emprestimo_aberto` é `status = 'ATIVO'` e sem empréstimo em aberto (regra de `esta_disponivel`).

## 10. O que cada evidência sustenta

| Afirmação | Evidência | Tipo |
|---|---|---|
| Tela, API e Redis mostram Total 2, Disponíveis 0 | Print, JSON da API, valor no Redis (16, 19 e 20/10) | Observado, em rodadas diferentes |
| O número esperado é 2 | Consulta de referência (15/10), `por_emprestimo_aberto = 2`, `esta_disponivel`, README (título da seção) | Regra assumida, com apoio no código e na documentação |
| O filtro `status = 'DISPONIVEL'` está no código | Linha 33 do `repositorios_postgres.py` | Observado |
| O schema não aceita `DISPONIVEL` | `CREATE TABLE`, `\d`, `pg_constraint` e INSERT rejeitado | Observado |
| `DISPONIVEL` só aparece nessa linha | `git grep` e busca com `-CaseSensitive` | Observado (arquivos versionados e extensões listadas) |
| A rota chega a `buscar_disponibilidade` | `api/main.py:51-58`, `consultar_disponibilidade.py:10` e o SELECT no log durante a chamada | Código lido e execução observada |
| A chamada 2 veio do cache | TTL 58 -> 55, resposta idêntica, sem SELECT no log | Observado |
| A API usou o `biblioteca_diag` | `total = 2`, `log_statement` só nesse banco, controle com 0 ocorrências | Inferência por escopo e por controle |
| Quem enviou o SELECT foi a API | Tempo do SELECT (~2 s após cada marcador), 3 requisições no `out.log`, porta livre antes | Indício, não identificador |
| Sem `DB_NAME` a API usa o `.env` (`emprestimo`) | `total: 1` em 15/10 e `DB_NAME=emprestimo` no `.env` | Inferência pelo total |
| A linha 33 entrou no `089c5b9` | `git log -S` e `git blame` | Observado |
| Nenhum teste verifica o número de disponíveis | Busca por "disponi", leitura de `testar_cache_fluxo.py` e do fake | Observado nos arquivos lidos |

## 11. Achados laterais

- **Banco padrão da API.** Sem `DB_NAME` na sessão, a API usa o `DB_NAME=emprestimo` do `.env` (15/10).
- **Dois bancos com dados diferentes.** `emprestimo` tem 1 exemplar para o livro 1 e `biblioteca_diag` tem 2.
- **Duas definições de "disponível".** Por status (`buscar_disponibilidade`, 0 no mesmo banco) e por ausência de empréstimo em aberto (`esta_disponivel`, 2). O README fala em disponibilidade "derivada, não armazenada".
- **Valores de `DB_NAME` e variáveis de senha nos scripts.** Os `.py` usam padrões diferentes quando `DB_NAME` não está definido: `biblioteca` (`arquitetura/main.py`, `testar_cache_fluxo.py`, `diagnostico_erro.py`) e `emprestimo` (`infraestrutura/tasks.py`, `teste/testar_expiracao_manual.py`). A API não tem padrão (`os.getenv("DB_NAME")` sem segundo argumento).
- **`testar_expiracao_manual.py`.** Em `arquitetura/teste/`, tem função `testar_fluxo_expiracao` (casa com `python_functions = testar_*` e fica dentro de `testpaths`). Nas linhas 7 a 10 lê `DB_PASSWORD` ou `DB_PASS` e levanta `ValueError` se não existirem, e isso ocorre no nível do módulo. A conexão (`psycopg2.connect`) fica dentro da função (linha 20). Na sessão de 20/10, nenhuma das variáveis de senha estava definida. O pytest completo não foi rodado, então não se observou o que acontece na coleta.
- **`api/main.py`.** Todas as exceções que não são `HTTPException` viram 500 com `detail=str(e)` (linhas 66 e 67).

## 12. Situação final das limitações

Numeração do primeiro relatório.

| Limitação | Situação | Evidência |
|---|---|---|
| 1. Origem da resposta (cache ou banco) | Fechada para a rodada de 20/10 | Chamadas 1 e 3 com SELECT no log; chamada 2 sem SELECT e TTL 58 -> 55 |
| 2. Banco usado pela API | Fechada por escopo da configuração | `log_statement` só no `biblioteca_diag`; controle no `emprestimo` com 0 ocorrências |
| 3. Rota e método | Fechada | Evidência A (código) e B (SQL no log durante a chamada) |
| 4. Schema e tabela `exemplares` | Fechada | `CREATE TABLE` (linhas 41 a 50), `\d exemplares`, `pg_constraint`, INSERT rejeitado |
| 5. Print sem relógio, banco ou origem | Aberta | O horário (19/10, 08:55:54) está só no nome do arquivo |
| 6. Rodadas e sessões diferentes | Aberta | Dados de 15, 16, 19 e 20/10 em sessões distintas |
| 7. Inferências marcadas | Reduzida | SQL real no log; definição de "disponível" em `esta_disponivel` e no README; `Celery` confirmado em `celery_app.py`. Seguem inferências: `_kombu.*` como chaves do Celery pelos nomes, quem enviou o SELECT, banco da API pelo total |
| 8. Escopo da busca por `DISPONIVEL` | Fechada | Busca ampliada e `git grep` |
