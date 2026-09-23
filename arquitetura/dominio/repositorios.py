# dominio/repositorios.py

# Interfaces abstratas (contratos)
# que dizem o que cada repositório precisa saber fazer
from abc import ABC, abstractmethod
from typing import Optional

from dominio.usuario import Usuario
from dominio.livro import Livro
from dominio.exemplar import Exemplar
from dominio.reserva import Reserva
from dominio.emprestimo import Emprestimo


class RepositorioUsuario(ABC):
    @abstractmethod
    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        ...


class RepositorioLivro(ABC):
    @abstractmethod
    def buscar_por_id(self, livro_id: int) -> Optional[Livro]:
        ...


class RepositorioExemplar(ABC):
    @abstractmethod
    def buscar_por_id(self, exemplar_id: int) -> Optional[Exemplar]:
        ...

    @abstractmethod
    def esta_disponivel(self, exemplar_id: int) -> bool:
        ...

    @abstractmethod
    def buscar_disponibilidade(self, livro_id: int) -> dict:
        """Retorna a contagem total e disponíveis para o livro."""
        ...

    @abstractmethod
    def invalidar_disponibilidade(self, livro_id: int) -> None:
        """
        Invalida qualquer dado de disponibilidade em cache referente a este livro.
        Implementações sem cache podem simplesmente não fazer nada (pass).
        """
        ...


class RepositorioReserva(ABC):
    @abstractmethod
    def buscar_por_id(self, reserva_id: int) -> Optional[Reserva]:
        ...

    @abstractmethod
    def existe_reserva_pendente_para_livro(
        self, livro_id: int, excluir_usuario_id: int
    ) -> bool:
        ...

    @abstractmethod
    def buscar_aguardando_retirada(self) -> list[Reserva]:
        ...

    @abstractmethod
    def marcar_como_expirada(self, reserva_id: int) -> None:
        ...


class RepositorioEmprestimo(ABC):
    @abstractmethod
    def salvar(self, emprestimo: Emprestimo) -> Emprestimo:
        ...

    @abstractmethod
    def existe_emprestimo_ativo_para_exemplar(self, exemplar_id: int) -> bool:
        ...