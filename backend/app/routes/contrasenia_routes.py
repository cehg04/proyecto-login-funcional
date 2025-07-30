from fastapi import APIRouter, Query, HTTPException
from ..services.contrasenia_service import obtener_contrasenias, crear_contrasenias, obtener_empresas, obtener_proveedores
from ..models.contrasenia_model import EntradaCompletaContrasenia
router = APIRouter(
    prefix="/contrasenias",
    tags=["contrasenias"]
)

# end-point de listar las contraseñas
@router.get("/")
def listar_contrasenias(cod_empresa: int = Query(...)):
    contrasenias = obtener_contrasenias(cod_empresa)
    return contrasenias

# end-point para crear contraseñas
@router.post("/crear-contrasenia")
def crear_contrasenia_endpoint(data: EntradaCompletaContrasenia):
    try:
        return crear_contrasenias(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# end-point para listar empresas
@router.get("/empresas")
def listar_empresa():
    return obtener_empresas()

@router.get("/proveedores")
def listar_proveedores(cod_empresa: int = Query(...)):
    return obtener_proveedores(cod_empresa)

