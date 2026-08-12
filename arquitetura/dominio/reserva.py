# Guarda o status da fila
# PENDENTE, AGUARDANDO_RETIRADA etc.
# e diz se ainda está ativa.

from datetime import datetime
from enum import Enum

class StatusReserva(str, Enum):
    PENDENTE = "PENDENTE"
    AGUARDANDO_RETIRADA = "AGUARDANDO_RETIRADA"
    ATENDIDA = "ATENDIDA"
    EXPIRADA = "EXPIRADA"
    CANCELADA = "CANCELADA"

_STATUS_ATIVOS = {StatusReserva.PENDENTE, StatusReserva.AGUARDANDO_RETIRADA}

class Reserva:
    def __init__(
        self,
        id: int,
        usuario_id: int,
        livro_id: int,
        criado_em: datetime,
        status: StatusReserva = StatusReserva.PENDENTE,
        notificado_em: datetime | None = None,
    ):
        if usuario_id is None or livro_id is None:
            raise ValueError("Reserva precisa de usuario_id e livro_id.")

        self.id = id
        self.usuario_id = usuario_id
        self.livro_id = livro_id
        self.criado_em = criado_em
        self.status = status
        self.notificado_em = notificado_em

    def esta_ativa(self) -> bool:
        return self.status in _STATUS_ATIVOS

    def __repr__(self):
        return (
            f"Reserva(id={self.id}, usuario_id={self.usuario_id}, "
            f"livro_id={self.livro_id}, status={self.status})"
        )
