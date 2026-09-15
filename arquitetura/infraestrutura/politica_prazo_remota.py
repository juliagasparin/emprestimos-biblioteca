from dominio.repositorios import RepositorioReserva
from dominio.politica_prazo import PoliticaPrazo


class PrazoComFilaDeReservaRemota(PoliticaPrazo):
    """Mesma regra de PrazoComFilaDeReserva, mas delegada ao servico-prazo via HTTP."""

    def __init__(
        self,
        repo_reserva: RepositorioReserva,
        cliente_http,
        fallback: PoliticaPrazo,
    ):
        self._repo_reserva = repo_reserva
        self._cliente_http = cliente_http
        self._fallback = fallback

    def calcular_dias(self, usuario_id: int, livro_id: int) -> int:
        tem_reserva_pendente = self._repo_reserva.existe_reserva_pendente_para_livro(
            livro_id, excluir_usuario_id=usuario_id
        )
        try:
            resposta = self._cliente_http.post(
                "http://127.0.0.1:8001/calcular-prazo",
                json={"tem_reserva_pendente": tem_reserva_pendente},
                timeout=2,
            )
            resposta.raise_for_status()
            return resposta.json() # Pega o número inteiro puro direto
        except (Exception,) as erro:
            return self._fallback.calcular_dias(usuario_id, livro_id)