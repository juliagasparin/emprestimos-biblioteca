import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from infraestrutura.politica_prazo_remota import PrazoComFilaDeReservaRemota
from dominio.politica_prazo import PrazoComFilaDeReserva

# Mock ou instância real do seu repositório de reserva
# Dependendo de como seu projeto instancia os repositórios para testes manuais/integração:
class RepositorioReservaFakeParaTeste:
    def __init__(self, tem_reserva: bool):
        self._tem_reserva = tem_reserva

    def existe_reserva_pendente_para_livro(self, livro_id: int, excluir_usuario_id: int) -> bool:
        return self._tem_reserva

def testar_integracao():
    print("Iniciando teste de integração com o microsserviço...")

    # Cenário 1: Com reserva pendente (deve retornar 7 via microsserviço)
    repo_com_reserva = RepositorioReservaFakeParaTeste(tem_reserva=True)
    fallback = PrazoComFilaDeReserva(repo_reserva=repo_com_reserva)
    
    politica_remota = PrazoComFilaDeReservaRemota(
        repo_reserva=repo_com_reserva,
        cliente_http=requests,
        fallback=fallback
    )

    dias = politica_remota.calcular_dias(usuario_id=1, livro_id=10)
    print(f"Resultado com reserva (esperado 7): {dias}")
    assert dias == 7, f"Esperado 7, mas veio {dias}"

    # Cenário 2: Sem reserva pendente (deve retornar 14 via microsserviço)
    repo_sem_reserva = RepositorioReservaFakeParaTeste(tem_reserva=False)
    fallback_sem = PrazoComFilaDeReserva(repo_reserva=repo_sem_reserva)
    
    politica_remota_sem = PrazoComFilaDeReservaRemota(
        repo_reserva=repo_sem_reserva,
        cliente_http=requests,
        fallback=fallback_sem
    )

    dias_sem = politica_remota_sem.calcular_dias(usuario_id=1, livro_id=10)
    print(f"Resultado sem reserva (esperado 14): {dias_sem}")
    assert dias_sem == 14, f"Esperado 14, mas veio {dias_sem}"

    print("Sucesso! O sistema principal conversou com o microsserviço corretamente.")

if __name__ == "__main__":
    testar_integracao()