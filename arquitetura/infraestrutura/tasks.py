import os
import psycopg2
from datetime import timedelta

from celery_app import app
from aplicacao.expirar_reservas_pendentes import expirar_reservas_pendentes
from infraestrutura.repositorios_postgres import RepositorioReservaPostgres


@app.task(name="tarefas.expirar_reservas")
def task_expirar_reservas():
    print("Iniciando varredura de reservas pendentes expiradas...")

    # Exige obrigatoriamente a senha pelas variáveis de ambiente (sem fallback inseguro)
    senha = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS") or os.getenv("POSTGRES_PASSWORD")
    if not senha:
        raise ValueError("Erro de Configuração: A variável de ambiente DB_PASSWORD (ou equivalente) é obrigatória.")
    
    # Corrige eventuais caracteres desalinhados trazidos pelo terminal do Windows
    if isinstance(senha, str):
        try:
            senha = senha.encode('latin1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    # Captura os parâmetros de conexão via variáveis de ambiente com fallbacks locais
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "emprestimo")
    db_user = os.getenv("DB_USER", "postgres")
    db_port = os.getenv("DB_PORT", "5432")

    conexao = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=senha,
        host=db_host,
        port=db_port
    )
    try:
        repositorio = RepositorioReservaPostgres(conexao)
        ids_expirados = expirar_reservas_pendentes(repositorio, janela=timedelta(hours=48))
        print(f"Varredura concluída. Reservas expiradas: {ids_expirados}")
        return ids_expirados
    finally:
        conexao.close()