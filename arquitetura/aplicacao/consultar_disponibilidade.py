from dominio.repositorios import RepositorioExemplar


class ConsultarDisponibilidade:
    def __init__(self, repo_exemplar: RepositorioExemplar):
        self._repo_exemplar = repo_exemplar

    def executar(self, livro_id: int) -> dict:
        """Consulta a disponibilidade de um livro utilizando o repositório configurado (com cache ou Postgres)."""
        return self._repo_exemplar.buscar_disponibilidade(livro_id)