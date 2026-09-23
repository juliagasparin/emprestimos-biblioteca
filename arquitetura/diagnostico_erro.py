import psycopg2

try:
    # Testando conexão com timeout curto para não travar
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="password",
        dbname="biblioteca",
        connect_timeout=3
    )
    print("Conexão bem-sucedida!")
except psycopg2.OperationalError as e:
    print("--- CONEXÃO RECUSADA PELO POSTGRES ---")
    # Imprime a representação segura do erro sem decodificação estrita de UTF-8
    print(repr(e))
except Exception as e:
    print(f"Outro erro: {type(e).__name__}: {repr(e)}")