# prova automatizada (com repositórios falsos) 
# de que a invariante da reserva é respeitada.
from datetime import datetime

import pytest

from dominio.exemplar import Exemplar, StatusExemplar
from dominio.reserva import Reserva, StatusReserva
from dominio.repositorios import (
    RepositorioExemplar,
    RepositorioReserva,
    RepositorioEmprestimo,
)
from aplicacao.criar_emprestimo import CriarEmprestimo, ExemplarIndisponivelError


class RepositorioExemplarFake(RepositorioExemplar):
    def __init__(self, exemplares):
        self._exemplares = {e.id: e for e in exemplares}

    def buscar_por_id(self, exemplar_id):
        return self._exemplares.get(exemplar_id)

    def esta_disponivel(self, exemplar_id):
        return True


class RepositorioReservaFake(RepositorioReserva):
    def __init__(self, reservas):
        self._reservas = {r.id: r for r in reservas}

    def buscar_por_id(self, reserva_id):
        return self._reservas.get(reserva_id)


class RepositorioEmprestimoFake(RepositorioEmprestimo):
    def __init__(self):
        self._salvos = []
        self._proximo_id = 1

    def existe_emprestimo_ativo_para_exemplar(self, exemplar_id):
        return any(
            e.exemplar_id == exemplar_id and e.esta_ativo() for e in self._salvos
        )

    def salvar(self, emprestimo):
        emprestimo.id = self._proximo_id
        self._proximo_id += 1
        self._salvos.append(emprestimo)
        return emprestimo


def _montar_caso_de_uso(exemplares, reservas):
    return CriarEmprestimo(
        repo_exemplar=RepositorioExemplarFake(exemplares),
        repo_reserva=RepositorioReservaFake(reservas),
        repo_emprestimo=RepositorioEmprestimoFake(),
    )


# --- Testes ---


def test_criar_emprestimo_sem_reserva_funciona():
    exemplar = Exemplar(id=1, livro_id=10, status=StatusExemplar.ATIVO)
    caso_de_uso = _montar_caso_de_uso(exemplares=[exemplar], reservas=[])

    emprestimo = caso_de_uso.executar(usuario_id=100, exemplar_id=1, livro_id=10)

    assert emprestimo.id is not None
    assert emprestimo.reserva_id is None


def test_criar_emprestimo_com_reserva_coerente_funciona():
    exemplar = Exemplar(id=1, livro_id=10, status=StatusExemplar.ATIVO)
    reserva = Reserva(id=5, usuario_id=100, livro_id=10, criado_em=datetime(2026, 1, 1))
    caso_de_uso = _montar_caso_de_uso(exemplares=[exemplar], reservas=[reserva])

    emprestimo = caso_de_uso.executar(
        usuario_id=100, exemplar_id=1, livro_id=10, reserva_id=5
    )

    assert emprestimo.reserva_id == 5


def test_criar_emprestimo_com_reserva_de_outro_usuario_falha():
    exemplar = Exemplar(id=1, livro_id=10, status=StatusExemplar.ATIVO)
    reserva = Reserva(id=5, usuario_id=999, livro_id=10, criado_em=datetime(2026, 1, 1))
    caso_de_uso = _montar_caso_de_uso(exemplares=[exemplar], reservas=[reserva])

    with pytest.raises(ValueError, match="pertence ao usuario"):
        caso_de_uso.executar(usuario_id=100, exemplar_id=1, livro_id=10, reserva_id=5)


def test_criar_emprestimo_com_reserva_de_outro_livro_falha():
    exemplar = Exemplar(id=1, livro_id=10, status=StatusExemplar.ATIVO)
    reserva = Reserva(id=5, usuario_id=100, livro_id=999, criado_em=datetime(2026, 1, 1))
    caso_de_uso = _montar_caso_de_uso(exemplares=[exemplar], reservas=[reserva])

    with pytest.raises(ValueError, match="é do livro"):
        caso_de_uso.executar(usuario_id=100, exemplar_id=1, livro_id=10, reserva_id=5)


def test_criar_emprestimo_com_reserva_cancelada_falha():
    exemplar = Exemplar(id=1, livro_id=10, status=StatusExemplar.ATIVO)
    reserva = Reserva(
        id=5,
        usuario_id=100,
        livro_id=10,
        criado_em=datetime(2026, 1, 1),
        status=StatusReserva.CANCELADA,
    )
    caso_de_uso = _montar_caso_de_uso(exemplares=[exemplar], reservas=[reserva])

    with pytest.raises(ValueError, match="está com status"):
        caso_de_uso.executar(usuario_id=100, exemplar_id=1, livro_id=10, reserva_id=5)


def test_criar_emprestimo_com_reserva_ja_atendida_falha():
    exemplar = Exemplar(id=1, livro_id=10, status=StatusExemplar.ATIVO)
    reserva = Reserva(
        id=5,
        usuario_id=100,
        livro_id=10,
        criado_em=datetime(2026, 1, 1),
        status=StatusReserva.ATENDIDA,
    )
    caso_de_uso = _montar_caso_de_uso(exemplares=[exemplar], reservas=[reserva])

    with pytest.raises(ValueError, match="está com status"):
        caso_de_uso.executar(usuario_id=100, exemplar_id=1, livro_id=10, reserva_id=5)


def test_criar_emprestimo_exemplar_ja_emprestado_falha():
    exemplar = Exemplar(id=1, livro_id=10, status=StatusExemplar.ATIVO)
    caso_de_uso = _montar_caso_de_uso(exemplares=[exemplar], reservas=[])

    caso_de_uso.executar(usuario_id=100, exemplar_id=1, livro_id=10)

    with pytest.raises(ExemplarIndisponivelError):
        caso_de_uso.executar(usuario_id=200, exemplar_id=1, livro_id=10)
