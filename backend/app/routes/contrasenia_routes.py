from fastapi import APIRouter, Query
from ..services.contrasenia_service import obtener_contrasenias

router = APIRouter(
    prefix="/contrasenias",
    tags=["contrasenias"]
)

@router.get("/")
def listar_contrasenias(cod_empresa: int = Query(...)):
    contrasenias = obtener_contrasenias(cod_empresa)
    return contrasenias

