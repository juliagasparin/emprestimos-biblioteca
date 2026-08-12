# Busca exemplar, busca reserva, monta o Emprestimo e salva.

from datetime import datetime, timedelta
from typing import Optional

from dominio.repositorios import (
    RepositorioExemplar,
    RepositorioReserva,
    RepositorioEmprestimo,
)
from dominio.emprestimo import Emprestimo

class ExemplarIndisponivelError(Exception):
    """Levantada quando o exemplar não existe, não está ATIVO ou já está emprestado."""

class CriarEmprestimo:
    def __init__(
        self,
        repo_exemplar: RepositorioExemplar,
        repo_reserva: RepositorioReserva,
        repo_emprestimo: RepositorioEmprestimo,
        prazo_padrao_dias: int = 14,
    ):
        self._repo_exemplar = repo_exemplar
        self._repo_reserva = repo_reserva
        self._repo_emprestimo = repo_emprestimo
        self._prazo_padrao_dias = prazo_padrao_dias

    def executar(
        self,
        usuario_id: int,
        exemplar_id: int,
        livro_id: int,
        reserva_id: Optional[int] = None,
    ) -> Emprestimo:
        exemplar = self._repo_exemplar.buscar_por_id(exemplar_id)
        if exemplar is None or not exemplar.esta_ativo():
            raise ExemplarIndisponivelError(
                f"Exemplar {exemplar_id} não existe ou não está ATIVO."
            )

        if self._repo_emprestimo.existe_emprestimo_ativo_para_exemplar(exemplar_id):
            raise ExemplarIndisponivelError(
                f"Exemplar {exemplar_id} já está emprestado."
            )

        reserva = None
        if reserva_id is not None:
            reserva = self._repo_reserva.buscar_por_id(reserva_id)
            if reserva is None:
                raise ValueError(f"Reserva {reserva_id} não encontrada.")

        emprestado_em = datetime.now()
        prevista_devolucao_em = emprestado_em + timedelta(days=self._prazo_padrao_dias)

        emprestimo = Emprestimo(
            id=None,
            usuario_id=usuario_id,
            exemplar_id=exemplar_id,
            livro_id=livro_id,
            emprestado_em=emprestado_em,
            prevista_devolucao_em=prevista_devolucao_em,
            reserva=reserva,
        )

        return self._repo_emprestimo.salvar(emprestimo)
