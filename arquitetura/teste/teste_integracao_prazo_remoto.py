# teste_integracao_prazo_remoto.py
import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from infraestrutura.politica_prazo_remota import PrazoComFilaDeReservaRemota
from dominio.politica_prazo import PrazoComFilaDeReserva


# Mock / Dublê do repositório de reserva para execução dos testes
class RepositorioReservaFakeParaTeste:
    def __init__(self, tem_reserva: bool):
        self._tem_reserva = tem_reserva

    def existe_reserva_pendente_para_livro(self, livro_id: int, excluir_usuario_id: int) -> bool:
        return self._tem_reserva

@pytest.mark.integracao
def testar_integracao_caminho_feliz():
    print("\n--- Teste 1: Caminho Feliz (Microsserviço Online) ---")

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

@pytest.mark.integracao
def testar_integracao_fallback_indisponivel():
    print("\n--- Teste 2: Fallback (Microsserviço Indisponível) ---")

    # Instancia o repositório e o fallback local
    repo_com_reserva = RepositorioReservaFakeParaTeste(tem_reserva=True)
    fallback = PrazoComFilaDeReserva(repo_reserva=repo_com_reserva)

    # 1. Calculamos o valor que o fallback local retornaria diretamente
    resultado_esperado_local = fallback.calcular_dias(usuario_id=1, livro_id=10)

    # Instancia a política remota
    politica_remota = PrazoComFilaDeReservaRemota(
        repo_reserva=repo_com_reserva,
        cliente_http=requests,
        fallback=fallback
    )

    # 2. Espionamos a instância do fallback para garantir que seu método seja invocado
    with patch.object(fallback, 'calcular_dias', wraps=fallback.calcular_dias) as espiao_fallback:
        
        # 3. Simulamos a falha de conexão HTTP (ConnectionError/Timeout)
        with patch("requests.post", side_effect=requests.exceptions.ConnectionError("Serviço indisponível")):
            
            # 4. Executamos a chamada da política remota com o serviço indisponível
            dias_retornados = politica_remota.calcular_dias(usuario_id=1, livro_id=10)

            # --- ASSERT 1: O valor retornado bate com a regra de negócio esperada (7) ---
            assert dias_retornados == 7, f"Esperado 7, mas veio {dias_retornados}"

            # --- ASSERT 2 (Duplo): O valor é exatamente o mesmo retornado pela política local ---
            assert dias_retornados == resultado_esperado_local, (
                f"Resultado ({dias_retornados}) difere do fallback local ({resultado_esperado_local})"
            )

            # --- VERIFICAÇÃO RIGOROSA: Confirma que o fallback foi de fato executado ---
            espiao_fallback.assert_called_once_with(1, 10)
            print("Confirmado: O método calcular_dias do fallback foi realmente executado.")

    print("Sucesso! O fallback foi totalmente provado por execução de código.")


if __name__ == "__main__":
    testar_integracao_caminho_feliz()
    testar_integracao_fallback_indisponivel()