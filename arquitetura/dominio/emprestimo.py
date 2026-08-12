# Valida a invariante central: 
# reserva vinculada precisa ser do mesmo usuário e livro.

from datetime import datetime
from typing import Optional

from dominio.reserva import Reserva

class Emprestimo:
    def __init__(
        self,
        id: Optional[int],
        usuario_id: int,
        exemplar_id: int,
        livro_id: int,
        emprestado_em: datetime,
        prevista_devolucao_em: datetime,
        devolvido_em: Optional[datetime] = None,
        reserva: Optional[Reserva] = None,
    ):
        if usuario_id is None or exemplar_id is None or livro_id is None:
            raise ValueError(
                "Emprestimo precisa de usuario_id, exemplar_id e livro_id."
            )

        if prevista_devolucao_em <= emprestado_em:
            raise ValueError(
                "prevista_devolucao_em precisa ser depois de emprestado_em."
            )

        # Invariante central
        if reserva is not None:
            self._validar_coerencia_com_reserva(reserva, usuario_id, livro_id)

        self.id = id
        self.usuario_id = usuario_id
        self.exemplar_id = exemplar_id
        self.livro_id = livro_id
        self.emprestado_em = emprestado_em
        self.prevista_devolucao_em = prevista_devolucao_em
        self.devolvido_em = devolvido_em
        self.reserva_id = reserva.id if reserva else None

    @staticmethod
    def _validar_coerencia_com_reserva(
        reserva: Reserva, usuario_id: int, livro_id: int
    ) -> None:
        if not reserva.esta_ativa():
            raise ValueError(
                f"Reserva {reserva.id} está com status {reserva.status} "
                "e não pode gerar um empréstimo (só PENDENTE ou "
                "AGUARDANDO_RETIRADA podem)."
            )
        if reserva.usuario_id != usuario_id:
            raise ValueError(
                f"Reserva {reserva.id} pertence ao usuario {reserva.usuario_id}, "
                f"não ao usuario {usuario_id} deste empréstimo."
            )
        if reserva.livro_id != livro_id:
            raise ValueError(
                f"Reserva {reserva.id} é do livro {reserva.livro_id}, "
                f"não do livro {livro_id} deste empréstimo."
            )

    def esta_ativo(self) -> bool:
        return self.devolvido_em is None

    def registrar_devolucao(self, devolvido_em: datetime) -> None:
        if self.devolvido_em is not None:
            raise ValueError(f"Emprestimo {self.id} já foi devolvido.")
        if devolvido_em < self.emprestado_em:
            raise ValueError("Data de devolução não pode ser anterior ao empréstimo.")
        self.devolvido_em = devolvido_em

    def __repr__(self):
        return (
            f"Emprestimo(id={self.id}, usuario_id={self.usuario_id}, "
            f"exemplar_id={self.exemplar_id}, reserva_id={self.reserva_id})"
        )
