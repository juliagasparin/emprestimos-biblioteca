import os
import time
import redis
import psycopg

from infraestrutura.repositorios_postgres import RepositorioExemplarPostgres
from infraestrutura.repositorio_exemplares_cache import RepositorioExemplarCache
from aplicacao.consultar_disponibilidade import ConsultarDisponibilidade


def rodar_teste():
    print("--- INICIANDO TESTE MANUAL DE CACHE E INVALIDAÇÃO ---")

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "postgres")
    db_name = os.getenv("DB_NAME", "biblioteca")
    
    db_password = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS")
    if not db_password:
        raise ValueError("Erro de Configuração: A variável de ambiente DB_PASSWORD é obrigatória para este teste.")

    conn_string = f"host={db_host} port={db_port} user={db_user} password={db_password} dbname={db_name}"
    conexao_pg = psycopg.connect(conn_string)

    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
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

    print("\n[1] Realizando 1ª consulta (Deve ir ao Banco):")
    inicio = time.time()
    res1 = consultar.executar(livro_id_teste)
    fim = time.time()
    print(f"Resultado: {res1}")
    print(f"Tempo decorrido: {fim - inicio:.4f}s")

    print("\n[2] Realizando 2ª consulta seguida (Deve vir do Cache Redis):")
    inicio = time.time()
    res2 = consultar.executar(livro_id_teste)
    fim = time.time()
    print(f"Resultado: {res2}")
    print(f"Tempo decorrido: {fim - inicio:.4f}s")

    print("\n[3] Invalidando o cache do livro...")
    repo_cache.invalidar_disponibilidade(livro_id_teste)
    print("Cache invalidado com sucesso!")

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