import json
from typing import Optional
from dominio.exemplar import Exemplar
from dominio.repositorios import RepositorioExemplar
from infraestrutura.cache_keys import chave_disponibilidade


class RepositorioExemplarCache(RepositorioExemplar):
    def __init__(self, repositorio_real: RepositorioExemplar, redis_client, ttl: int = 60):
        self.repositorio_real = repositorio_real
        self.redis = redis_client
        self.ttl = ttl

    def _chave_cache(self, livro_id: int) -> str:
        return chave_disponibilidade(livro_id)

    def buscar_disponibilidade(self, livro_id: int) -> dict:
        chave = self._chave_cache(livro_id)
        
        # 1. Tenta buscar no Cache (Redis)
        dados_cached = self.redis.get(chave)
        if dados_cached:
            return json.loads(dados_cached)

        # 2. Cache Miss: Busca no banco de dados real
        resultado = self.repositorio_real.buscar_disponibilidade(livro_id)

        # 3. Salva no Redis com TTL configurado
        self.redis.setex(
            name=chave,
            time=self.ttl,
            value=json.dumps(resultado)
        )

        return resultado

    def invalidar_disponibilidade(self, livro_id: int) -> None:
        """Invalida a chave do livro no Redis ao ocorrer alteração de estado."""
        chave = self._chave_cache(livro_id)
        self.redis.delete(chave)

    # Delegando métodos de leitura diretamente para o repositório real
    def buscar_por_id(self, exemplar_id: int) -> Optional[Exemplar]:
        return self.repositorio_real.buscar_por_id(exemplar_id)

    def esta_disponivel(self, exemplar_id: int) -> bool:
        return self.repositorio_real.esta_disponivel(exemplar_id)

    # --- MÉTODOS DE ESCRITA / MUTAÇÃO NO DECORATOR ---
    # Se o seu RepositorioExemplar possui métodos que salvam ou alteram o estado do exemplar:

    def salvar(self, exemplar: Exemplar) -> Exemplar:
        """Salva a alteração no banco e invalida o cache do livro correspondente."""
        exemplar_salvo = self.repositorio_real.salvar(exemplar)
        # O Decorator garante a invalidação sem que o Caso de Uso precise saber
        self.invalidar_disponibilidade(exemplar.livro_id)
        return exemplar_salvo