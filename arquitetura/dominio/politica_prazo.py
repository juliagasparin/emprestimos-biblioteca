# Strategy: calcula quantos dias um Emprestimo tem até a devolução prevista.
# Existe porque o prazo não pode mais ser um int fixo — depende de contexto de negócio.

from abc import ABC, abstractmethod

from dominio.repositorios import RepositorioReserva


class PoliticaPrazo(ABC):
    @abstractmethod
    def calcular_dias(self, usuario_id: int, livro_id: int) -> int:
        ...


class PrazoPadrao(PoliticaPrazo):
    """Prazo fixo, sem considerar contexto. Comportamento atual do sistema."""

    def __init__(self, dias: int = 14):
        self._dias = dias

    def calcular_dias(self, usuario_id: int, livro_id: int) -> int:
        return self._dias


class PrazoComFilaDeReserva(PoliticaPrazo):
    """Encurta o prazo se houver reserva ativa de outro usuário
    esperando pelo mesmo livro — libera o exemplar mais rápido."""

    def __init__(
        self,
        repo_reserva: RepositorioReserva,
        dias_padrao: int = 14,
        dias_com_fila: int = 7,
    ):
        self._repo_reserva = repo_reserva
        self._dias_padrao = dias_padrao
        self._dias_com_fila = dias_com_fila

    def calcular_dias(self, usuario_id: int, livro_id: int) -> int:
        if self._repo_reserva.existe_reserva_pendente_para_livro(
            livro_id, excluir_usuario_id=usuario_id
        ):
            return self._dias_com_fila
        return self._dias_padrao
