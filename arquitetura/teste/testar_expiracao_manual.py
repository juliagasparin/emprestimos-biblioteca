import os
from datetime import datetime, timedelta
import psycopg2
from infraestrutura.repositorios_postgres import RepositorioReservaPostgres
from aplicacao.expirar_reservas_pendentes import expirar_reservas_pendentes

db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS")
if not db_password:
    raise ValueError("Erro de Configuração: A variável de ambiente DB_PASSWORD é obrigatória.")

db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "emprestimo")

DATABASE_URL = os.getenv("DATABASE_URL") or f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def testar_fluxo_expiracao():
    print("🔌 Conectando ao banco de dados...")
    conexao = psycopg2.connect(DATABASE_URL)
    
    try:
        repositorio = RepositorioReservaPostgres(conexao)
        aguardando = repositorio.buscar_aguardando_retirada()
        print(f"📦 Reservas atualmente 'AGUARDANDO_RETIRADA': {len(aguardando)}")
        
        for r in aguardando:
            print(f"   - Reserva ID: {r.id} | Notificado em: {r.notificado_em}")

        print("\n⏳ Executando o caso de uso 'expirar_reservas_pendentes'...")
        ids_expiradas = expirar_reservas_pendentes(
            repositorio=repositorio,
            janela=timedelta(hours=48),
            agora=datetime.now()
        )
        print(f"✨ Resultado: {len(ids_expiradas)} reserva(s) foram expiradas nesta execução: {ids_expiradas}")

    finally:
        conexao.close()
        print("🔌 Conexão fechada.")

if __name__ == "__main__":
    testar_fluxo_expiracao()