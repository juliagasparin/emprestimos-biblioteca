# Valida que nome e email existem antes de o objeto poder ser criado.

class Usuario:
    def __init__(self, id: int, nome: str, email: str):
        if not nome or not nome.strip():
            raise ValueError("Usuario precisa de um nome.")
        if not email or "@" not in email:
            raise ValueError("Usuario precisa de um email válido.")

        self.id = id
        self.nome = nome
        self.email = email

    def __repr__(self):
        return f"Usuario(id={self.id}, nome={self.nome!r})"
