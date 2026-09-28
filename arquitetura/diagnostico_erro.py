import os
import psycopg2

try:
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_user = os.getenv("DB_USER", "postgres")
    
    db_password = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS")
    if not db_password:
        raise ValueError("Erro de Configuração: A variável de ambiente DB_PASSWORD é obrigatória.")

    db_name = os.getenv("DB_NAME", "biblioteca")

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        dbname=db_name,
        connect_timeout=3
    )
    print("Conexão bem-sucedida!")
except psycopg2.OperationalError as e:
    print("--- CONEXÃO RECUSADA PELO POSTGRES ---")
    print(repr(e))
except Exception as e:
    print(f"Outro erro: {type(e).__name__}: {repr(e)}")