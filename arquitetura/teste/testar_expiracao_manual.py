from datetime import datetime, timedelta
import psycopg2
from infraestrutura.repositorios_postgres import RepositorioReservaPostgres
from aplicacao.expirar_reservas_pendentes import expirar_reservas_pendentes

# ATENÇÃO: Ajuste a string de conexão para o seu banco local de testes/desenvolvimento
DATABASE_URL = "postgresql://seu_usuario:sua_senha@localhost:5432/seu_banco"

def testar_fluxo_expiracao():
    print("🔌 Conectando ao banco de dados...")
    conexao = psycopg2.connect(DATABASE_URL)
    
    try:
        repositorio = RepositorioReservaPostgres(conexao)
        
        # 1. Vamos buscar se já existe alguma reserva aguardando retirada para inspecionar
        aguardando = repositorio.buscar_aguardando_retirada()
        print(f"📦 Reservas atualmente 'AGUARDANDO_RETIRADA': {len(aguardando)}")
        
        for r in aguardando:
            print(f"   - Reserva ID: {r.id} | Notificado em: {r.notificado_em}")

        # 2. Executando o caso de uso com uma janela de teste (ex: 48 horas)
        print("\n⏳ Executando o caso de uso 'expirar_reservas_pendentes'...")
        ids_expiradas = expirar_reservas_pendentes(
            repositorio=repositorio,
            janela=timedelta(hours=48),
            agora=datetime.now() # Opcional: você pode forçar uma data futura aqui se quiser simular o tempo passando
        )
        
        print(f"✨ Resultado: {len(ids_expiradas)} reserva(s) foram expiradas nesta execução: {ids_expiradas}")

    finally:
        conexao.close()
        print("🔌 Conexão fechada.")

if __name__ == "__main__":
    testar_fluxo_expiracao()