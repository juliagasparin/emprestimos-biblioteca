# Valida título e ISBN

class Livro:
    def __init__(self, id: int, titulo: str, isbn: str):
        if not titulo or not titulo.strip():
            raise ValueError("Livro precisa de um título.")
        if not isbn or not isbn.strip():
            raise ValueError("Livro precisa de um ISBN.")

        self.id = id
        self.titulo = titulo
        self.isbn = isbn

    def __repr__(self):
        return f"Livro(id={self.id}, titulo={self.titulo!r})"
