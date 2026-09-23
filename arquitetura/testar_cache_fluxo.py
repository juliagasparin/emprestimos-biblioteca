import os
import time
import redis
import psycopg  # Importando a versão 3 do driver

from infraestrutura.repositorios_postgres import RepositorioExemplarPostgres
from infraestrutura.repositorio_exemplares_cache import RepositorioExemplarCache
from aplicacao.consultar_disponibilidade import ConsultarDisponibilidade


def rodar_teste():
    print("--- INICIANDO TESTE MANUAL DE CACHE E INVALIDAÇÃO ---")

    # Conexão usando psycopg (v3)
    conexao_pg = psycopg.connect(
        "host=localhost port=5432 user=postgres password=postgres@ju dbname=biblioteca"
    )

    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )

    repo_postgres = RepositorioExemplarPostgres(conexao=conexao_pg)
    repo_cache = RepositorioExemplarCache(
        repositorio_real=repo_postgres,
        redis_client=redis_client,
        ttl=60
    )

    consultar = ConsultarDisponibilidade(repo_exemplar=repo_cache)

    livro_id_teste = 1

    # ETAPA A: 1ª Consulta
    print("\n[1] Realizando 1ª consulta (Deve ir ao Banco):")
    inicio = time.time()
    res1 = consultar.executar(livro_id_teste)
    fim = time.time()
    print(f"Resultado: {res1}")
    print(f"Tempo decorrido: {fim - inicio:.4f}s")

    # ETAPA B: 2ª Consulta
    print("\n[2] Realizando 2ª consulta seguida (Deve vir do Cache Redis):")
    inicio = time.time()
    res2 = consultar.executar(livro_id_teste)
    fim = time.time()
    print(f"Resultado: {res2}")
    print(f"Tempo decorrido: {fim - inicio:.4f}s")

    # ETAPA C: Invalidação de Cache
    print("\n[3] Invalidando o cache do livro...")
    repo_cache.invalidar_disponibilidade(livro_id_teste)
    print("Cache invalidado com sucesso!")

    # ETAPA D: Consulta Pós-Invalidação
    print("\n[4] Realizando consulta após invalidação (Deve ir ao Banco novamente):")
    inicio = time.time()
    res3 = consultar.executar(livro_id_teste)
    fim = time.time()
    print(f"Resultado: {res3}")
    print(f"Tempo decorrido: {fim - inicio:.4f}s")

    conexao_pg.close()
    print("\n--- TESTE CONCLUÍDO COM SUCESSO ---")


if __name__ == "__main__":
    rodar_teste()