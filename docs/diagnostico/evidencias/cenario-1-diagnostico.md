# Cenário 1: Disponibilidade na tela
Commit base: 9278e33

Comandos, notas de processo e resultado detalhado de cada bloco: ver `cenario-1-detalhamento.md`. Arquivos brutos em `evidencias/`.

## Resposta ao cenário 1 (resumo)

**O que aparece.** Com 1 livro e 2 exemplares ativos e nenhum empréstimo, a tela mostra: Total de exemplares: 2, Disponíveis para empréstimo: 0, Em estoque: Não. A API e o Redis devolvem o mesmo valor.

![Tela do frontend: livro 1 com Total 2, Disponíveis 0, Em estoque Não](evidencias/Captura_de_tela_2026-10-19_085554.png)

*Print de 19/10/2026 08:55:54 (horário do nome do arquivo). A imagem em si não mostra relógio nem banco usado.*

**Está certo?** Não. O número esperado é 2 disponíveis. No mesmo banco, a contagem por `status = 'DISPONIVEL'` (a do código) dá 0, e a contagem por exemplar `ATIVO` sem empréstimo em aberto é 2. Considerei a segunda a correta porque é a regra de `esta_disponivel` (repositorios_postgres.py, linhas 67 a 79) e porque o README tem a seção "Decisão: disponibilidade derivada, não armazenada".

**Por que acontece.** `buscar_disponibilidade` (repositorios_postgres.py, linha 33) conta como disponível só o exemplar com `status = 'DISPONIVEL'`. O schema só aceita `ATIVO`, `BAIXADO` e `PERDIDO` (`ck_status_exemplar_valido`), e um INSERT com `'DISPONIVEL'` foi rejeitado pelo banco. O filtro nunca casa, e `disponiveis` é sempre 0.

**Como provei.**
- O log do Postgres mostra esse SELECT (com `status = 'DISPONIVEL'` e `$1 = '1'`) executado nas chamadas 1 e 3, quando a chave do Redis não existia.
- Na chamada 2 não há SELECT no log, e o TTL caiu de 58 para 55: a resposta veio do cache.
- `git grep` encontra `DISPONIVEL` em uma única linha dos arquivos versionados.

**O que não provei.** O print mostra o que a tela exibiu, mas a imagem não traz relógio, banco usado nem origem da resposta (cache ou banco). O horário (19/10, 08:55:54) vem só do nome do arquivo. Quem prova a origem da resposta é o log do Postgres de 20/10, de outra rodada. Os valores do print coincidem com o JSON da API e com o Redis, mas isso é coincidência de valores, não um registro da mesma execução.

## (b) Como isso chegou até a revisão e o que teria evitado

**Resposta curta.** Não existe nenhuma verificação com um número esperado para a disponibilidade. As duas coisas que parecem cobrir esse caminho deixam o filtro errado passar, cada uma por um motivo diferente.

**1. Os testes unitários usam um fake que não passa pela regra.**
`RepositorioExemplarFake` (test_criar_emprestimo.py, linhas 18 a 32) devolve `True` em `esta_disponivel` e `None` em `buscar_disponibilidade`. Os 7 testes de `test_criar_emprestimo.py` passam (`7 passed`), mas testam `CriarEmprestimo`. Pela busca por "disponi" em todos os `.py`, nenhum teste chama `buscar_disponibilidade` de verdade.

**2. O script `testar_cache_fluxo.py` usa banco e Redis reais, mas não verifica nada.**
Ele imprime `res1`, `res2` e `res3` e termina com "TESTE CONCLUÍDO COM SUCESSO", sem nenhum `assert` e sem comparar com um valor esperado. Mostra que o cache funciona (consulta, cache e invalidação), mas a mensagem de sucesso não depende do resultado. Pelo `pytest.ini` (`testpaths = arquitetura/teste`, e a função se chama `rodar_teste`), ele também não entra na coleta do pytest; isso é inferência pela configuração, não rodei o pytest completo.

**Execução na época do desenvolvimento.** Rodei esse script durante o desenvolvimento, com um banco que tinha 2 livros cadastrados, 1 exemplar cada, sem reservas e sem empréstimos. A única saída de que me lembro é a mensagem final, "TESTE CONCLUÍDO COM SUCESSO", e foi com base nela que considerei o fluxo correto. Não guardei a saída daquela execução, então não tenho evidência do que o script mostrou.
Nesta análise não rodei o script de novo; o que afirmo sobre ele vem da leitura do código.

**O que o histórico mostra.** A linha 33 vem do commit `089c5b9` (23/09), "Etapa 7 - Processamento Assíncrono", cujo título não fala de disponibilidade. O schema e `esta_disponivel` são de `223dfc5` (12/08). Não abri o diff do `089c5b9`, então não sei o que a linha era antes.

**Verificação que teria pegado.** Um teste de integração contra um banco criado pelo `biblioteca_schema.sql`, com 2 exemplares `ATIVO` e 0 empréstimos, que exija `disponiveis == 2`. Mesmo no script manual, um `assert` sobre esse valor bastava.

**Por que não aconteceu.** Ninguém tinha definido o valor esperado de `disponiveis`, e a validação da Etapa 7 observou apenas tempos, não o conteúdo da resposta. Na época, relatei "Ciclo testado e validado com sucesso no terminal" (cerca de 2,05 s no banco, 0,0012 s no cache e chave removida), sem colar a saída completa. Por isso, o campo `disponiveis` nunca apareceu na conversa, e o Claude da época apenas concluiu, a partir dos números que eu informei, que o padrão de cache funcionava. A decisão de considerar o ciclo validado foi minha.

Tempo de resposta e status HTTP seriam os mesmos com a contagem errada, então essas medidas não podiam revelar o problema. Além disso, o `biblioteca_schema.sql` nunca foi colado na conversa, e a SQL com `'DISPONIVEL'` não foi comparada com os status válidos do schema (`ATIVO`, `BAIXADO`, `PERDIDO`).

## Onde usei a IA e o que conferi com meus próprios olhos

**Onde usei:** Depois de cadastrar um livro com 2 exemplares e nenhum empréstimo, consultei-o na tela e, a partir do resultado, usei o Claude como apoio para estruturar a investigação. O processo foi iterativo: eu executava os comandos, registrava o que observava e formulava minhas hipóteses. O Claude questionava essas hipóteses e apontava dúvidas que eu ainda não tinha considerado, o que me levou a buscar mais evidências antes de concluir. Quando algum comando ou consulta fugia do que eu dominava (PowerShell, `psql`, Redis), pedi explicação e ajuda para escrevê-lo. Em todos os casos, conferi as entradas e as saídas antes de aceitar o resultado. Quando discordei de uma interpretação do Claude, buscamos uma abordagem alternativa em vez de aceitá-la.

**O que conferi eu mesma:** o print da tela, o `\d exemplares` e o `pg_constraint`, o log do Postgres (SELECT com `DISPONIVEL`, ausência de SELECT na chamada 2), o INSERT rejeitado, o `git grep`, o `git blame`, o pytest (`7 passed`) e a comparação das duas contagens no mesmo banco (0 por status, 2 por empréstimo em aberto).
