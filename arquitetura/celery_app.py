from celery import Celery
from celery.schedules import crontab

app = Celery(
    "biblioteca_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
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