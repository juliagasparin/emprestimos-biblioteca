import redis
import psycopg2

from infraestrutura.repositorios_postgres import RepositorioExemplarPostgres
from infraestrutura.repositorio_exemplares_cache import RepositorioExemplarCache
from aplicacao.consultar_disponibilidade import ConsultarDisponibilidade


def bootstrap():
    # 1. Conexão com o banco PostgreSQL (Ajuste os parâmetros se necessário)
    conexao_pg = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="password",
        dbname="biblioteca"
    )

    # 2. Conexão com o Redis
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )

    # 3. Instanciação do repositório base do PostgreSQL
    repo_postgres = RepositorioExemplarPostgres(conexao=conexao_pg)

    # 4. PASSO 6: Envolve o repositório PostgreSQL com o Decorator de Cache
    repo_exemplares_com_cache = RepositorioExemplarCache(
        repositorio_real=repo_postgres,
        redis_client=redis_client,
        ttl=60
    )

    # 5. Injeção do repositório com Cache no Caso de Uso de Consulta
    caso_de_uso_consulta = ConsultarDisponibilidade(repo_exemplar=repo_exemplares_com_cache)

    return caso_de_uso_consulta


if __name__ == "__main__":
    consulta = bootstrap()
    # Exemplo de execução para testar a busca do livro com ID 1
    resultado = consulta.executar(livro_id=1)
    print("Resultado da consulta:", resultado)