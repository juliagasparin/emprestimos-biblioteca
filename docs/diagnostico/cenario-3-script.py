import os, sys, traceback
import psycopg, redis
from aplicacao.criar_emprestimo import CriarEmprestimo
from aplicacao.devolver_exemplar import DevolverExemplar
from dominio.politica_prazo import PrazoComFilaDeReserva
from infraestrutura.repositorios_postgres import (
    RepositorioExemplarPostgres, RepositorioReservaPostgres,
    RepositorioEmprestimoPostgres)
from infraestrutura.repositorio_exemplares_cache import RepositorioExemplarCache
from infraestrutura.cache_keys import chave_disponibilidade

if os.getenv("DB_NAME") != "biblioteca_diag":
    sys.exit("ABORTA: DB_NAME diferente de biblioteca_diag")

def conectar(**extra):
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", 5432)),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD") or os.getenv("DB_PASS"),
        dbname=os.getenv("DB_NAME"), **extra)

conn = conectar()                    # usada pelos repositorios
obs = conectar(autocommit=True)      # so para olhar o banco
print("BANCO:", obs.execute("SELECT current_database()").fetchone()[0])
if obs.execute("SELECT current_database()").fetchone()[0] != "biblioteca_diag":
    sys.exit("ABORTA: banco errado")

r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)), db=0, decode_responses=True)
CHAVE = chave_disponibilidade(1)

repo_ex = RepositorioExemplarCache(RepositorioExemplarPostgres(conn), r, ttl=60)
repo_res = RepositorioReservaPostgres(conn)
repo_emp = RepositorioEmprestimoPostgres(conn)
criar = CriarEmprestimo(repo_ex, repo_res, repo_emp, PrazoComFilaDeReserva(repo_res))
devolver = DevolverExemplar(repo_emp, repo_ex)

def estado(titulo):
    print("\n--- ESTADO:", titulo)
    print("emprestimos:")
    for l in obs.execute("SELECT id, usuario_id, exemplar_id, reserva_id, emprestado_em::date, prevista_devolucao_em, devolvido_em FROM emprestimos ORDER BY id"):
        print("  ", l)
    print("reservas:")
    for l in obs.execute("SELECT id, usuario_id, livro_id, status FROM reservas ORDER BY id"):
        print("  ", l)
    print("redis", CHAVE, "=", r.get(CHAVE), "| ttl =", r.ttl(CHAVE))

def tentar(rotulo, fn):
    print("\n=== ", rotulo)
    try:
        res = fn()
        print("ACEITO:", res)
        if hasattr(res, "prevista_devolucao_em"):
            print("DIAS DE PRAZO:", (res.prevista_devolucao_em - res.emprestado_em).days)
        return res
    except Exception as e:
        print("EXCECAO:", type(e).__name__, "-", e)
        traceback.print_exc(file=sys.stdout)
        conn.rollback()
        return None

estado("INICIAL")
print("\nCache aquecido (como a API faria):", repo_ex.buscar_disponibilidade(1))
estado("apos aquecer o cache")

# (a) Ana, reserva 1
emp_ana = tentar("a) Ana (usuario 1) pega exemplar 1, livro 1, reserva_id=1",
                 lambda: criar.executar(usuario_id=1, exemplar_id=1, livro_id=1, reserva_id=1))
estado("apos (a)")

# (b) Bruno, sem reserva
tentar("b) Bruno (usuario 2) pega exemplar 2, livro 1, sem reserva",
       lambda: criar.executar(usuario_id=2, exemplar_id=2, livro_id=1))
estado("apos (b)")

# (c) Carla reserva o livro 1 (criada AQUI, status pelo padrao do banco)
rid = obs.execute("INSERT INTO reservas (livro_id, usuario_id) VALUES (1, 3) RETURNING id").fetchone()[0]
print("\nReserva da Carla criada, id =", rid)
estado("antes de (c)")
combos = [
    ("c1", dict(usuario_id=3, exemplar_id=3, livro_id=1, reserva_id=rid)),
    ("c2", dict(usuario_id=3, exemplar_id=3, livro_id=2, reserva_id=rid)),
    ("c3", dict(usuario_id=3, exemplar_id=3, livro_id=1)),
    ("c4", dict(usuario_id=3, exemplar_id=3, livro_id=2)),
]
for nome, kw in combos:
    tentar(f"{nome}) executar({kw})", lambda kw=kw: criar.executar(**kw))
    estado(f"apos {nome}")
    # limpeza entre tentativas (feita pelo script, visivel aqui)
    obs.execute("DELETE FROM emprestimos WHERE exemplar_id = 3")
    obs.execute("UPDATE reservas SET status = 'PENDENTE' WHERE id = %s", (rid,))
    print(f"LIMPEZA apos {nome}: emprestimos do exemplar 3 apagados; reserva {rid} voltou a PENDENTE")

# (d) devolucao da Ana
if emp_ana:
    tentar(f"d) DevolverExemplar.executar({emp_ana.id})", lambda: devolver.executar(emp_ana.id))
estado("apos (d)")