import os
import redis
import psycopg

from infraestrutura.repositorios_postgres import RepositorioExemplarPostgres
from infraestrutura.repositorio_exemplares_cache import RepositorioExemplarCache
from aplicacao.consultar_disponibilidade import ConsultarDisponibilidade


def bootstrap():
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_user = os.getenv("DB_USER", "postgres")
    
    db_password = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS")
    if not db_password:
        raise ValueError("Erro de Configuração: A variável de ambiente DB_PASSWORD é obrigatória.")

    db_name = os.getenv("DB_NAME", "biblioteca")

    conexao_pg = psycopg.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        dbname=db_name
    )

    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        decode_responses=True
    )

    repo_postgres = RepositorioExemplarPostgres(conexao=conexao_pg)
    repo_exemplares_com_cache = RepositorioExemplarCache(
        repositorio_real=repo_postgres,
        redis_client=redis_client,
        ttl=60
    )

    caso_de_uso_consulta = ConsultarDisponibilidade(repo_exemplar=repo_exemplares_com_cache)
    return caso_de_uso_consulta


if __name__ == "__main__":
    consulta = bootstrap()
    resultado = consulta.executar(livro_id=1)
    print("Resultado da consulta:", resultado)