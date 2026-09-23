def chave_disponibilidade(livro_id: int) -> str:
    """Retorna a chave padronizada para o cache de disponibilidade de um livro."""
    return f"disponibilidade:livro:{livro_id}"