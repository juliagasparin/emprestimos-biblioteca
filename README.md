# Sistema de Empréstimo de Biblioteca

Sistema de gestão de biblioteca construído incrementalmente como projeto de
portfólio: parte de um schema relacional em PostgreSQL e evolui, etapa por etapa,
até uma arquitetura com camadas desacopladas (Clean Architecture/DDD), um serviço
extraído como microsserviço, processamento assíncrono com cache, e uma interface
web em React consumindo a API. Cada etapa abaixo documenta o problema, a decisão
tomada — incluindo alternativas descartadas — e a validação local com dados reais.

**Stack:** PostgreSQL · Python · TypeScript · FastAPI · Celery · Redis · React · Vite · Pytest · Vitest

## Índice

- [Modelo de dados](#modelo-de-dados)
- [Etapa 3 — Arquitetura e DDD (Python)](#etapa-3--arquitetura-e-ddd-python)
- [Etapa 4 — Design Patterns (Strategy)](#etapa-4--design-patterns-strategy)
- [Etapa 5 — TypeScript](#etapa-5--typescript)
- [Etapa 6 — Microsserviços](#etapa-6--microsserviços)
- [Etapa 7 — Processamento Assíncrono e Cache](#etapa-7--processamento-assíncrono-e-cache)
- [Etapa 8 — React (Fatia 1: Disponibilidade)](#etapa-8--react-fatia-1-disponibilidade)

## Modelo de dados

```mermaid
erDiagram
    USUARIOS ||--o{ EMPRESTIMOS : realiza
    USUARIOS ||--o{ RESERVAS : faz
    LIVROS ||--o{ EXEMPLARES : possui
    LIVROS ||--o{ RESERVAS : "é reservado em"
    LIVROS }o--o{ AUTORES : escrito_por
    EXEMPLARES ||--o{ EMPRESTIMOS : "é emprestado em"
    RESERVAS ||--o| EMPRESTIMOS : origina

    USUARIOS {
        int id PK
        string nome
        string email
    }
    LIVROS {
        int id PK
        string titulo
        string isbn
    }
    AUTORES {
        int id PK
        string nome
    }
    EXEMPLARES {
        int id PK
        int livro_id FK
        string status
    }
    RESERVAS {
        int id PK
        int livro_id FK
        int usuario_id FK
        string status
    }
    EMPRESTIMOS {
        int id PK
        int exemplar_id FK
        int usuario_id FK
        int reserva_id FK
        timestamp devolvido_em
    }
```

### Regras garantidas pelo schema

- Um exemplar tem no máximo um empréstimo em aberto por vez (índice único parcial).
- Exemplar perdido/danificado muda de status — nunca é excluído, preservando histórico.
- Um usuário não pode ter duas reservas ativas do mesmo título.
- Livros, usuários e exemplares com histórico não podem ser excluídos (`ON DELETE RESTRICT`).

### Decisão: disponibilidade derivada, não armazenada

Em vez de uma coluna `disponivel`, a disponibilidade de um exemplar é calculada pela
ausência de um empréstimo aberto:

```sql
CREATE UNIQUE INDEX uk_exemplar_emprestado
    ON emprestimos(exemplar_id)
    WHERE devolvido_em IS NULL;
```

`emprestimos.reserva_id` (opcional) registra quando um empréstimo veio de uma
reserva atendida.

### Limitação conhecida (schema)

O schema não garante que `emprestimos.reserva_id` aponte para uma reserva do mesmo
usuário e do mesmo livro — PostgreSQL não permite `CHECK` entre tabelas. Essa
validação fica na camada de aplicação, não em um trigger: é uma regra do fluxo de
negócio "atender reserva", não uma regra de integridade de dado.

> **Resolvida na Etapa 3** — ver seção abaixo, garantida em código no construtor da
> entidade `Emprestimo`.

**Testado localmente:** constraints validadas com dados reais via `psql` — reserva
duplicada, empréstimo de exemplar já emprestado e devolução retroativa bloqueados;
o cenário da limitação conhecida foi reproduzido de propósito e confirmou a lacuna.

```bash
psql -U seu_usuario -d seu_banco -f biblioteca_schema.sql
```

---

# Etapa 3 — Arquitetura e DDD (Python)

Camada de aplicação em Python sobre o schema acima, seguindo Clean Architecture: o
domínio não depende de nada externo (nem de banco, nem de framework); as
dependências externas (Postgres) ficam isoladas numa camada própria.

## Estrutura

```
arquitetura/
├── dominio/
│   ├── usuario.py           # Entidade Usuario
│   ├── livro.py              # Entidade Livro
│   ├── exemplar.py           # Entidade Exemplar
│   ├── reserva.py            # Entidade Reserva
│   ├── emprestimo.py         # Entidade Emprestimo + invariante central
│   └── repositorios.py       # Interfaces abstratas (contratos)
├── aplicacao/
│   └── criar_emprestimo.py   # Caso de uso: orquestra repositórios + domínio
├── infraestrutura/
│   └── repositorios_postgres.py  # Implementação real dos contratos, com SQL
└── teste/
    └── test_criar_emprestimo.py  # Prova automatizada da invariante
```


A seta de dependência aponta sempre para dentro: `infraestrutura` e `aplicacao`
dependem de `dominio`; `dominio` não depende de nada.

## Invariante central

A limitação da Etapa 2 é resolvida no construtor de `Emprestimo`
(`dominio/emprestimo.py`): se a reserva não pertencer ao mesmo `usuario_id` e
`livro_id` do empréstimo, ou não estiver `PENDENTE`/`AGUARDANDO_RETIRADA`, a criação
do objeto falha com `ValueError` — o empréstimo inconsistente nunca chega a ser
persistido.

**Testado localmente:** 7 testes (`pytest testes/ -v`) cobrindo criação com/sem
reserva, reserva de outro usuário, outro livro, cancelada, já atendida, e exemplar
já emprestado. Todos passando.

---

# Etapa 4 — Design Patterns (Strategy)

**Problema:** `CriarEmprestimo` calculava o prazo com um `int` fixo. Qualquer regra
nova viraria `if/else` acumulado dentro do caso de uso, misturando lógica de negócio
com orquestração.

**Solução:** `dominio/politica_prazo.py` define a interface `PoliticaPrazo` com duas
implementações — `PrazoPadrao` (14 dias fixos) e `PrazoComFilaDeReserva` (7 dias
quando existe reserva pendente de outro usuário para o mesmo livro). `CriarEmprestimo`
recebe a estratégia por injeção de dependência e não sabe qual está em uso.

**Por que "fila de reserva" e não "tipo de usuário":** o domínio não tem conceito de
categoria de usuário hoje — aplicar Strategy em cima de um campo inexistente seria
especulação. A fila de reserva já é regra real, modelada desde a Etapa 2.

**Dependência gerada:** exigiu um método novo no contrato do repositório —
`RepositorioReserva.existe_reserva_pendente_para_livro` — implementado em SQL na
infraestrutura e como fake em memória nos testes.

**Testado localmente:** 9 testes (os 7 da Etapa 3 + prazo encurta com fila / prazo
padrão sem fila). Todos passando — a troca de estratégia não quebrou a invariante da
Etapa 3.

---

# Etapa 5 — TypeScript

Portei `PoliticaPrazo`/`PrazoPadrao` para `politica-prazo-ts/` (mesmo repositório),
provando que a lógica de domínio não depende da linguagem — 2 testes Vitest (padrão
e valor customizado), ambos passando. Limitação assumida: `PrazoComFilaDeReserva`
(que depende do repositório de reservas) ficou de fora — portá-la exigiria replicar
esse contrato em TS, escopo de uma integração real entre os dois lados, não desta
prova de conceito. Módulo ainda não integrado ao restante do sistema Python.

---

# Etapa 6 — Microsserviços

**Por que isolamos esse serviço:** o cálculo de prazo tem potencial de evolução e
escala próprios (integrações externas, novas políticas por categoria de livro) sem
exigir deploy do sistema principal.

**Como funciona:**
- [`servico-prazo/`](./servico-prazo) — FastAPI, expõe `POST /calcular-prazo`, retorna
  7 ou 14 dias conforme reservas pendentes. Subpasta deste repositório, mesmo padrão
  da Etapa 5.
- `infraestrutura/politica_prazo_remota.py` — `PrazoComFilaDeReservaRemota`, mesma
  interface `PoliticaPrazo`, consulta o microsserviço via `requests`.
- **Fallback de resiliência** — timeout de 2s; se o serviço remoto falhar, o sistema
  recorre automaticamente à política local `PrazoComFilaDeReserva`, sem interromper
  o fluxo de empréstimo.

### Testado localmente

Testes em [`teste/teste_integracao_prazo_remoto.py`](./teste/teste_integracao_prazo_remoto.py):
o caminho feliz valida a comunicação real entre os dois serviços; o cenário de
fallback é provado com o microsserviço mockado (falha de conexão simulada),
confirmando por execução de código — não só por inspeção de log — que a política
local assume o cálculo quando o serviço remoto está indisponível.

```bash
# terminal 1
cd servico-prazo && uvicorn main:app --reload --port 8001
# terminal 2 (raiz do projeto)
uvicorn main:app --reload --port 8000
```

Com os dois serviços ativos, o sistema principal consulta automaticamente
`http://localhost:8001/calcular-prazo`. O comportamento de fallback está coberto por
teste automatizado — não precisa derrubar o serviço manualmente para observá-lo.

---

# Etapa 7 — Processamento Assíncrono e Cache

## Parte 1 — Jobs em segundo plano (Celery + Redis)

**Problema:** reservas `AGUARDANDO_RETIRADA` vencidas precisam mudar de status
automaticamente, sem depender de consulta manual.

**Solução:** Celery como fila/worker, Redis como broker, Celery Beat como agendador.
O caso de uso (`aplicacao/expirar_reservas_pendentes.py`) permanece puro — não sabe
que existe fila; `infraestrutura/tasks.py` instancia o repositório real e o executa;
`celery_app.py` agenda via `crontab(minute=0)`, varredura a cada hora.

**Por que Celery e não algo mais simples (ex. `APScheduler`):** o roadmap pede
processamento assíncrono via fila/worker, não só agendamento. Celery + Redis cobre os
dois casos com a mesma infraestrutura que a Parte 2 (cache) já precisaria, evitando
duas dependências novas para dois problemas relacionados.

**Testado localmente:** worker com `--pool=solo` (Windows), task disparada via
`.delay()`; reserva de teste mudou de `AGUARDANDO_RETIRADA` para `EXPIRADA`,
confirmado via `psql`.

## Parte 2 — Cache de disponibilidade (Redis, Cache-Aside)

**Problema:** a consulta de disponibilidade por livro é chamada com alta frequência
e muda pouco.

**Solução — decorator de cache sobre o repositório.** `RepositorioExemplarCache`
implementa a mesma interface `RepositorioExemplar` do repositório Postgres e decide
internamente: cache hit retorna do Redis; cache miss consulta o Postgres e grava no
Redis com `SETEX` (TTL 60s). O caso de uso `ConsultarDisponibilidade` não muda — a
troca "com cache"/"sem cache" acontece só no bootstrap (`main.py`).

**TTL curto + invalidação explícita são complementares, não redundantes:** a
invalidação (chamada logo após persistir empréstimo/devolução) garante que o cache
reflita a realidade no instante exato da mudança. O TTL de 60s é a rede de segurança
para os casos em que a invalidação falha ou é contornada — sem ele, um cache não
invalidado ficaria desatualizado indefinidamente.

### Sem vazamento de infraestrutura

`CriarEmprestimo` e `DevolverExemplar` não conhecem Redis — chamam
`self._repo_exemplar.invalidar_disponibilidade(livro_id)`, um método da própria
interface `RepositorioExemplar`. Quem decide *como* invalidar (deletar a chave no
Redis) é `RepositorioExemplarCache`, o mesmo decorator que decide como servir
leitura. Caso de uso e cache continuam desacoplados nos dois sentidos.

### Testado localmente

`testar_cache_fluxo.py`: 1ª consulta ~2.05s (Postgres) → 2ª consulta ~0.0012s
(Redis) → empréstimo dispara invalidação (chave removida) → consulta seguinte volta
a ser miss, confirmando dado atualizado em vez de cache velho.

## Ajustes de ambiente (Windows)

`UnicodeDecodeError` do `psycopg2` na comunicação do worker Celery com o Postgres —
variáveis de ambiente do terminal em CP1252. Resolvido migrando para `psycopg` (v3).
Mesma categoria de problema da Etapa 1 (barra invertida no `\i` do psql): ambiente
Windows exige atenção redobrada a encoding em qualquer ponto de integração com
texto/credenciais.

```bash
celery -A celery_app worker --beat --loglevel=info --pool=solo
python testar_cache_fluxo.py
```

## ⚠️ Limitações Conhecidas (Concorrência e Cache)

Duas limitações inerentes à concorrência de threads/requisições sob a arquitetura
atual:

### 1. Race de Invalidação (*Stale Cache Write*)
- **O que acontece:** corrida temporal entre a leitura de dados desatualizados do
  banco e a escrita posterior (`SETEX`) no Redis.
- **Como foi reproduzida:** script de reprodução com múltiplas threads
  (`reproduzir_race_cache.py`) — Thread A lê no Postgres (cache miss) e sofre atraso
  antes de gravar no Redis; no meio do intervalo, Thread B altera o estoque e invalida
  o cache; ao retomar, Thread A grava o dado já obsoleto de volta no Redis.
- **Mitigação pelo TTL:** dano limitado a no máximo 60s de inconsistência.
- **Solução real (direção):** versionamento otimista/timestamp de gravação, ou
  transações atômicas via lock distribuído (ex: Redlock).

### 2. Cache Stampede (*Thundering Herd*)
- **O que acontece:** ao expirar o TTL de um livro popular, dezenas de requisições
  simultâneas sofrem cache miss em conjunto e disparam a mesma query pesada ao
  Postgres ao mesmo tempo.
- **Solução real (direção):** lock de preenchimento (`SET NX` do Redis) ou
  antecipação probabilística de expiração (*XFetch*).

---

# Etapa 8 — React (Fatia 1: Disponibilidade)

### Problema
Conectar o backend FastAPI existente a uma interface web em React/Vite para permitir a consulta interativa da disponibilidade de exemplares de um livro, garantindo a gestão adequada de estados da UI e a privacidade de dados sensíveis.

### Solução
- **Separação Monorepo:** Organização do projeto em pasta dedicada `frontend/` com React, TypeScript e Vite, mantendo a API isolada na pasta `api/`.
- **Gestão de Segredos:** Credenciais de banco de dados e Redis carregadas via variáveis de ambiente (`.env`, `python-dotenv`), evitando segredos no código.
- **Contrato de Dados Rígido:** Tipagem estrita no frontend alinhada ao payload do endpoint (`GET /disponibilidade/{livro_id}`):
  ```typescript
  interface Disponibilidade {
    livro_id: number;
    total: number;
    disponiveis: number;
    em_estoque: boolean;
  }
  ```
- **Gestão de Estados na UI:** Implementação de `useState` manual para controlo independente de carregamento (`loading`), dados do resultado (`resultado`) e mensagens de erro (`erro`).
- **Fetch Nativo:** Utilização do `fetch` padrão do navegador, sem bibliotecas externas de data-fetching (como TanStack Query), mantendo a simplicidade e o foco no gerenciamento manual de estados.

### Testado localmente
Consulta com ID existente (200, dados corretos renderizados), ID inexistente (404, mensagem amigável) e falha de rede com backend desligado (`Failed to fetch` capturado, sem quebrar a interface).
