import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env na raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

sys.path.append(str(ROOT_DIR / "arquitetura"))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import psycopg
import redis

from infraestrutura.repositorios_postgres import RepositorioExemplarPostgres
from infraestrutura.repositorio_exemplares_cache import RepositorioExemplarCache
from aplicacao.consultar_disponibilidade import ConsultarDisponibilidade

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def obter_conexao():
    conexao = psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    try:
        yield conexao
    finally:
        conexao.close()

@app.get("/disponibilidade/{livro_id}")
def consultar_disponibilidade_endpoint(livro_id: int, conexao = Depends(obter_conexao)):
    try:
        repo_postgres = RepositorioExemplarPostgres(conexao)
        repo_cache = RepositorioExemplarCache(repo_postgres, redis_client)
        caso_uso = ConsultarDisponibilidade(repo_cache)
        
        resultado = caso_uso.executar(livro_id)
        
        if not resultado or resultado.get("total", 0) == 0:
            raise HTTPException(status_code=404, detail="Livro não encontrado ou sem exemplares cadastrados.")
            
        return resultado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))