from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CalculoPrazoRequest(BaseModel):
    tem_reserva_pendente: bool 
    # todo request pra esse endpoint precisa ter um campo tem_reserva_pendente
    # e precisa ser boolean 


DIAS_PADRAO = 14
DIAS_COM_FILA = 7


def calcular_prazo_com_fila(tem_reserva_pendente: bool) -> int:
    if tem_reserva_pendente:
        return DIAS_COM_FILA
    return DIAS_PADRAO

@app.post("/calcular-prazo")

def calcular_prazo(request: CalculoPrazoRequest) -> int:
    return calcular_prazo_com_fila(request.tem_reserva_pendente)