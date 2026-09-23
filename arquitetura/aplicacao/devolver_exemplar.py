from datetime import datetime


class DevolverExemplar:
    def __init__(
        self,
        repo_emprestimo,
        repo_exemplar,
    ):
        self._repo_emprestimo = repo_emprestimo
        self._repo_exemplar = repo_exemplar

    def executar(self, emprestimo_id: int) -> None:
        """Registra a devolução, descobre o livro afetado e invalida o cache."""
        
        # 1. Busca o empréstimo para validar existência e obter o ID do exemplar
        emprestimo = self._repo_emprestimo.buscar_por_id(emprestimo_id)
        if emprestimo is None:
            raise ValueError(f"Empréstimo {emprestimo_id} não encontrado.")

        # 2. Registra a devolução no repositório
        self._repo_emprestimo.marcar_como_devolvido(emprestimo_id, datetime.now())

        # 3. Descobre o livro através do exemplar para solicitar a invalidação ao repositório
        exemplar = self._repo_exemplar.buscar_por_id(emprestimo.exemplar_id)
        if exemplar:
            self._repo_exemplar.invalidar_disponibilidade(exemplar.livro_id)