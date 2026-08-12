# Cópia física: guarda o status ATIVO/BAIXADO/PERDIDO.

from enum import Enum

class StatusExemplar(str, Enum):
    ATIVO = "ATIVO"
    BAIXADO = "BAIXADO"
    PERDIDO = "PERDIDO"

class Exemplar:
    def __init__(self, id: int, livro_id: int, status: StatusExemplar = StatusExemplar.ATIVO):
        if livro_id is None:
            raise ValueError("Exemplar precisa estar vinculado a um livro_id.")

        self.id = id
        self.livro_id = livro_id
        self.status = status

    def esta_ativo(self) -> bool:
        # Só um exemplar ATIVO pode, em tese, ser emprestado
        return self.status == StatusExemplar.ATIVO

    def __repr__(self):
        return f"Exemplar(id={self.id}, livro_id={self.livro_id}, status={self.status})"
