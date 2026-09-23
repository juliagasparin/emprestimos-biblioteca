import os
import psycopg2
from datetime import timedelta

from celery_app import app
from aplicacao.expirar_reservas_pendentes import expirar_reservas_pendentes
from infraestrutura.repositorios_postgres import RepositorioReservaPostgres


@app.task(name="tarefas.expirar_reservas")
def task_expirar_reservas():
    print("Iniciando varredura de reservas pendentes expiradas...")

    # Obtém a senha da variável de ambiente ou usa o valor padrão 'postgres@ju'
    senha = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS") or "postgres@ju"
    
    # Corrige eventuais caracteres desalinhados trazidos pelo terminal do Windows
    if isinstance(senha, str):
        try:
            senha = senha.encode('latin1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    conexao = psycopg2.connect(
        dbname="emprestimo",
        user="postgres",
        password="postgres@ju",
        host="localhost",
        port="5432"
    )
    try:
        repositorio = RepositorioReservaPostgres(conexao)
        ids_expirados = expirar_reservas_pendentes(repositorio, janela=timedelta(hours=48))
        print(f"Varredura concluída. Reservas expiradas: {ids_expirados}")
        return ids_expirados
    finally:
        conexao.close()