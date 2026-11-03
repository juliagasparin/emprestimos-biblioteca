# Cenário 3: Ciclo de vida do empréstimo
Commit base: 9278e33

Evidências: `evidencias/cenario-3/cenario-3-parte-1.txt` - preparação, leitura do código, seed, execução a–d e estado final.
            `evidencias/cenario-3/cenario-3-parte-2.txt` - leitura complementar.
            Seed e script: `seed-cenario-3.sql` e `cenario-3-script.py`, em `docs/diagnostico/`. 
            Os "Blocos" citados abaixo são os do transcript.


## Método (o que o script faz)

- Usa `CriarEmprestimo`, `DevolverExemplar` e `PrazoComFilaDeReserva` com os repositórios Postgres de verdade, no banco `biblioteca_diag`.
- O cache é aquecido antes do passo (a).
- A reserva da Carla é criada pelo script no passo (c), não pelo seed.
- O script escreve no banco: INSERT em `reservas` (linha 77), DELETE em `emprestimos` do exemplar 3 (linha 90) e UPDATE para `PENDENTE` (linha 91). A mensagem "reserva voltou a PENDENTE" é imprecisa: o status nunca mudou, então o UPDATE não alterou nada.
- Não houve smoke test separado. Há o `SELECT current_database()` (Bloco 1) e o Redis (Blocos 5 e 7); imports e conexão só aparecem implicitamente na execução do script.

## Resposta ao cenário 3

### (a) Ana pega o exemplar 1 atendendo a reserva 1

**O que aconteceu.** Aceito, prazo de 14 dias. A reserva 1 continuou `PENDENTE` (Bloco 6, "apos (a)"; Bloco 7).
**Está certo?** Não. O esperado era `ATENDIDA`.
**Por quê.** `executar` só lê a reserva (linhas 51–54) e `salvar` só faz INSERT em `emprestimos` (linhas 202–223). Nenhuma linha do projeto escreve `ATENDIDA` (Bloco 4) e não há triggers (Bloco 3).
**Histórico.** As linhas 39–54 de `criar_emprestimo.py` vêm de `223dfc5` (12/08/2026) (`git blame`, Parte 2). O blame cobre só essas linhas; que nunca houve etapa de atualização da reserva é inferido do código atual, não de um diff. Na época: aceitei o código sem compreender por completo.
**(b) Categoria:** código da IA aceito sem ler. O comentário de abertura de `criar_emprestimo.py` ("Busca exemplar, busca reserva, monta o Emprestimo e salva") já descreve um fluxo sem etapa que atualize a reserva; ler o arquivo mostraria isso. Fator contribuinte: os 7 testes de `test_criar_emprestimo.py` usam fakes e nenhum teste da pasta confere o status da reserva depois do empréstimo (Parte 2, Bloco 2).

### (b) Bruno pega o exemplar 2, sem reserva

**O que aconteceu.** Aceito, prazo de 7 dias. O esperado era 14, porque ele não tem reserva e não há fila.
**Por quê.** A política pergunta se existe reserva `PENDENTE` ou `AGUARDANDO_RETIRADA` de outro usuário para o livro (`politica_prazo.py` 40–43; query em `repositorios_postgres.py` 131–147). Encontra a reserva da Ana, que segue `PENDENTE` por causa do (a). A política faz o que foi programada; a causa é o (a).
**Reforço (não prova sozinho):** no c4, livro 2 sem reserva de ninguém, o prazo foi 14; no c3, livro 1, foi 7.
**Histórico.** A causa é o (a), então vale o histórico do (a). Não fiz blame da política nem da query.
**(b) Categoria:** faltou rodar e olhar o resultado. A política com fila só é exercitada em `teste_integracao_prazo_remoto.py`, e ali o repositório é um fake que devolve um booleano fixo, sem considerar usuário, livro nem status; `test_criar_emprestimo.py` usa `PrazoPadrao`. Nenhum teste faz a sequência a→b contra o banco, então o efeito da reserva da Ana ainda `PENDENTE` sobre o prazo do Bruno nunca aparece.

### (c) Carla: reserva do livro 1, exemplar 3 é do livro 2

| Combo | Parâmetros | Resultado | Correto? |
|---|---|---|---|
| c1 | reserva 2, `livro_id=1` | ACEITO, 7 dias | Não, deveria recusar |
| c2 | reserva 2, `livro_id=2` | RECUSADO (reserva é do livro 1) | Sim |
| c3 | sem reserva, `livro_id=1` | ACEITO, 7 dias | Não, o exemplar não é do livro 1 |
| c4 | sem reserva, `livro_id=2` | ACEITO, 14 dias | Sim, empréstimo coerente (não usa a reserva) |

**O sistema deveria aceitar em algum caso?** Só no c4.
**Por quê.** `executar` carrega o exemplar só para ver se está `ATIVO` (linhas 39–43) e nunca compara `exemplar.livro_id` com `livro_id`. O `Emprestimo` só compara a reserva com o `livro_id` informado (linhas 48–63). O `livro_id` nem é gravado (a tabela `emprestimos` não tem essa coluna, Bloco 3).
**Histórico.** As linhas 39–43, que só checam o status do exemplar, vêm de `223dfc5` (12/08/2026) (`git blame`, Parte 2). Não fiz blame do `emprestimo.py`. Não me recordo o que foi feito na época.
**(b) Categoria:** código da IA aceito sem ler. A assinatura de `executar` recebe `exemplar_id` e `livro_id` como parâmetros independentes e as linhas 39–43 só checam o status do exemplar; ler isso mostraria que nada os compara. Fator contribuinte: `test_criar_emprestimo.py` faz o que diz (cobre usuário, livro e status da reserva), mas em todos os testes o exemplar tem o mesmo `livro_id` do parâmetro (10), então a regra exemplar↔livro nunca foi especificada nem testada.

### (d) Devolução do empréstimo da Ana

**O que aconteceu.** `AttributeError: 'RepositorioEmprestimoPostgres' object has no attribute 'buscar_por_id'`. `devolvido_em` continua vazio (Bloco 7).
**Está certo?** Não. O esperado era gravar `devolvido_em` e invalidar o cache.
**Por quê.** `DevolverExemplar` chama `buscar_por_id` (linha 17) e `marcar_como_devolvido` (linha 22) no repositório de empréstimos. Nem a interface nem o repositório Postgres têm esses métodos; só `salvar` e `existe_emprestimo_ativo_para_exemplar`. Nenhum teste menciona devolução.
**Histórico.** As linhas 13–27 de `devolver_exemplar.py` vêm de `089c5b9` (23/09/2026, "Etapa 7 - Processamento Assíncrono"), que não menciona devolução no título (`git blame`, Parte 2). Não fiz blame dos repositórios, então não sei se esses dois métodos já existiram em algum momento.
**(b) Categoria:** código da IA aceito sem ler. `DevolverExemplar` chama `buscar_por_id` e `marcar_como_devolvido` no repositório de empréstimos; comparar com a interface `RepositorioEmprestimo` (só `salvar` e `existe_emprestimo_ativo_para_exemplar`) mostraria que não existem. Fator contribuinte: nenhum teste em `arquitetura\teste` menciona devolução (Parte 2, Bloco 1).

### Quem é responsável por cada mudança de status da reserva

| Mudança | Responsável no código |
|---|---|
| Criação (`PENDENTE`) | Só o DEFAULT do banco. Nenhum código cria reservas |
| `PENDENTE` → `AGUARDANDO_RETIRADA` (e `notificado_em`) | Ninguém |
| → `ATENDIDA` | Ninguém |
| → `CANCELADA` | Ninguém |
| `AGUARDANDO_RETIRADA` → `EXPIRADA` | `marcar_como_expirada` (único UPDATE em `reservas`, `repositorios_postgres.py` 171–181). A regra vem de `Reserva.esta_expirada`, quem orquestra é `expirar_reservas_pendentes` e quem dispara é a task Celery em `tasks.py` (janela de 48 h) |

Só `EXPIRADA` tem dono, e ela depende de reservas em `AGUARDANDO_RETIRADA`, que nada no projeto produz.

## O que não provei

- A causa do (b) é inferida do código e do estado do Bloco 6; uma consulta direta no `psql` (livro 1, usuário 2) confirmaria, mas não foi rodada.
- A matriz do (c) não tem controle com exemplar disponível do livro 1, porque os dois estavam emprestados.
- A devolução falhou antes de gravar e de invalidar o cache, então "não existe `marcar_como_devolvido`" vem da busca textual e a invalidação na devolução não foi observada.
- A afirmação sobre testes vale para `test_criar_emprestimo.py`, para `teste_integracao_prazo_remoto.py` (lido, não executado) e para as buscas por texto em `arquitetura\teste`. A busca fora dos `.py` cobre só as extensões listadas.

## Achados para depois (sem corrigir)

1. Nada marca a reserva como `ATENDIDA` ao criar o empréstimo.
2. `CriarEmprestimo` não valida `exemplar.livro_id == livro_id`, e o `livro_id` não é persistido.
3. O repositório de empréstimos não tem `buscar_por_id` nem `marcar_como_devolvido`, e `DevolverExemplar` não tem testes.
4. Nenhum código cria reservas nem produz `AGUARDANDO_RETIRADA` ou `CANCELADA`.
5. A invalidação do cache usa o `livro_id` do parâmetro, não o do exemplar (inferido, não observado no Redis).
6. O `.pyc` versionado aparece como modificado no git.

## Onde usei a IA e o que conferi com meus próprios olhos

**Onde usei:** Sugeri a ordem de execução,o Claude refinou e atuou como guia, eu rodava os comandos e enviava a saída, observação e conclusão; ele não deu diagnósticos prontos, apontou inconsistências na minha organização (Bloco 6 classificado como "matriz e reset" e ausência de smoke test) e avaliou minha análise. A IA ajudou a escrever o seed e alguns comandos que eu ainda não conhecia.

**O que conferi eu mesma:** Executei todos os comandos e li as saídas dos Blocos 1–7 e da Parte 2; conferi no código as linhas citadas em cada diagnóstico; conferi o estado do banco e do Redis antes e depois da execução.
