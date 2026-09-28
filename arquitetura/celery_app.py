import os
from celery import Celery
from celery.schedules import crontab

# Lê as configurações do Redis via variáveis de ambiente com fallbacks locais
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")

app = Celery(
    "biblioteca_worker",
    broker=f"redis://{redis_host}:{redis_port}/0",
    backend=f"redis://{redis_host}:{redis_port}/0",
)

app.conf.update(
    timezone="America/Sao_Paulo",
    enable_utc=True,
)

app.conf.imports = ["infraestrutura.tasks"]

app.conf.beat_schedule = {
    "expirar-reservas-a-cada-hora": {
        "task": "tarefas.expirar_reservas",
        "schedule": crontab(minute=0),
    },
}