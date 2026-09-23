# aplicacao/expirar_reservas_pendentes.py

from datetime import datetime, timedelta
from typing import Protocol

from dominio.reserva import Reserva


class RepositorioReservas(Protocol):
    def buscar_aguardando_retirada(self) -> list[Reserva]:
        ...

    def marcar_como_expirada(self, reserva_id: int) -> None:
        ...


def expirar_reservas_pendentes(
    repositorio: RepositorioReservas,
    janela: timedelta = timedelta(hours=48),
    agora: datetime | None = None,
) -> list[int]:
    agora = agora or datetime.now()
    reservas_ids_expiradas: list[int] = []

    for reserva in repositorio.buscar_aguardando_retirada():
        if reserva.esta_expirada(janela, agora):
            repositorio.marcar_como_expirada(reserva.id)
            reservas_ids_expiradas.append(reserva.id)

    return reservas_ids_expiradas