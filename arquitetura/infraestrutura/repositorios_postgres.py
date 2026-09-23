# Implementação real dos repositórios,
# com SQL de verdade contra o schema PostgreSQL.

from typing import Optional

from psycopg import Connection as PgConnection

from dominio.usuario import Usuario
from dominio.livro import Livro
from dominio.exemplar import Exemplar, StatusExemplar
from dominio.reserva import Reserva, StatusReserva
from dominio.emprestimo import Emprestimo
from dominio.repositorios import (
    RepositorioUsuario,
    RepositorioLivro,
    RepositorioExemplar,
    RepositorioReserva,
    RepositorioEmprestimo,
)


class RepositorioExemplarPostgres(RepositorioExemplar):
    def __init__(self, conexao: PgConnection):
        self._conexao = conexao

    def buscar_disponibilidade(self, livro_id: int) -> dict:
        """Busca a contagem de exemplares totais e disponíveis para um livro."""
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 'DISPONIVEL') AS disponiveis
                FROM exemplares
                WHERE livro_id = %s;
                """,
                (livro_id,)
            )
            row = cursor.fetchone()
            
            if row:
                total = row[0] if isinstance(row, tuple) else row['total']
                disponiveis = row[1] if isinstance(row, tuple) else row['disponiveis']
            else:
                total, disponiveis = 0, 0

            return {
                "livro_id": livro_id,
                "total": total,
                "disponiveis": disponiveis,
                "em_estoque": disponiveis > 0
            }

    def buscar_por_id(self, exemplar_id: int) -> Optional[Exemplar]:
        with self._conexao.cursor() as cur:
            cur.execute(
                "SELECT id, livro_id, status FROM exemplares WHERE id = %s",
                (exemplar_id,),
            )
            linha = cur.fetchone()
            if linha is None:
                return None
            return Exemplar(
                id=linha[0], livro_id=linha[1], status=StatusExemplar(linha[2])
            )

    def esta_disponivel(self, exemplar_id: int) -> bool:
        with self._conexao.cursor() as cur:
            cur.execute(
                """
                SELECT NOT EXISTS (
                    SELECT 1 FROM emprestimos
                    WHERE exemplar_id = %s AND devolvido_em IS NULL
                )
                """,
                (exemplar_id,),
            )
            (disponivel,) = cur.fetchone()
            return disponivel

    def invalidar_disponibilidade(self, livro_id: int) -> None:
        """
        O repositório PostgreSQL puro não gerencia cache em memória/Redis,
        portanto esta implementação é vazia, mas necessária para satisfazer o contrato da interface.
        """
        pass


class RepositorioLivroPostgres(RepositorioLivro):
    def __init__(self, conexao: PgConnection):
        self._conexao = conexao

    def buscar_por_id(self, livro_id: int) -> Optional[Livro]:
        with self._conexao.cursor() as cur:
            cur.execute(
                "SELECT id, titulo, isbn FROM livros WHERE id = %s",
                (livro_id,),
            )
            linha = cur.fetchone()
            if linha is None:
                return None
            return Livro(id=linha[0], titulo=linha[1], isbn=linha[2])


class RepositorioReservaPostgres(RepositorioReserva):
    def __init__(self, conexao: PgConnection):
        self._conexao = conexao

    def buscar_por_id(self, reserva_id: int) -> Optional[Reserva]:
        with self._conexao.cursor() as cur:
            cur.execute(
                """
                SELECT id, usuario_id, livro_id, criado_em,
                       status, notificado_em
                FROM reservas WHERE id = %s
                """,
                (reserva_id,),
            )
            linha = cur.fetchone()
            if linha is None:
                return None
            return Reserva(
                id=linha[0],
                usuario_id=linha[1],
                livro_id=linha[2],
                criado_em=linha[3],
                status=StatusReserva(linha[4]),
                notificado_em=linha[5],
            )

    def existe_reserva_pendente_para_livro(
        self, livro_id: int, excluir_usuario_id: int
    ) -> bool:
        with self._conexao.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM reservas
                    WHERE livro_id = %s
                      AND usuario_id <> %s
                      AND status IN ('PENDENTE', 'AGUARDANDO_RETIRADA')
                )
                """,
                (livro_id, excluir_usuario_id),
            )
            (existe,) = cur.fetchone()
            return existe

    def buscar_aguardando_retirada(self) -> list[Reserva]:
        with self._conexao.cursor() as cur:
            cur.execute(
                """
                SELECT id, usuario_id, livro_id, criado_em,
                       status, notificado_em
                FROM reservas WHERE status = 'AGUARDANDO_RETIRADA'
                """
            )
            linhas = cur.fetchall()
            return [
                Reserva(
                    id=linha[0],
                    usuario_id=linha[1],
                    livro_id=linha[2],
                    criado_em=linha[3],
                    status=StatusReserva(linha[4]),
                    notificado_em=linha[5],
                )
                for linha in linhas
            ]

    def marcar_como_expirada(self, reserva_id: int) -> None:
        with self._conexao.cursor() as cur:
            cur.execute(
                """
                UPDATE reservas
                SET status = 'EXPIRADA'
                WHERE id = %s
                """,
                (reserva_id,),
            )
            self._conexao.commit()


class RepositorioEmprestimoPostgres(RepositorioEmprestimo):
    def __init__(self, conexao: PgConnection):
        self._conexao = conexao

    def existe_emprestimo_ativo_para_exemplar(self, exemplar_id: int) -> bool:
        with self._conexao.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM emprestimos
                    WHERE exemplar_id = %s AND devolvido_em IS NULL
                )
                """,
                (exemplar_id,),
            )
            (existe,) = cur.fetchone()
            return existe

    def salvar(self, emprestimo: Emprestimo) -> Emprestimo:
        with self._conexao.cursor() as cur:
            cur.execute(
                """
                INSERT INTO emprestimos
                    (usuario_id, exemplar_id, emprestado_em,
                     prevista_devolucao_em, reserva_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    emprestimo.usuario_id,
                    emprestimo.exemplar_id,
                    emprestimo.emprestado_em,
                    emprestimo.prevista_devolucao_em,
                    emprestimo.reserva_id,
                ),
            )
            (novo_id,) = cur.fetchone()
            self._conexao.commit()
            emprestimo.id = novo_id
            return emprestimo