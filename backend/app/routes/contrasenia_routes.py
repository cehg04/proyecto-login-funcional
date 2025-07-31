from fastapi import APIRouter, Query, HTTPException
from ..services.contrasenia_service import obtener_contrasenias, crear_contrasenias, obtener_empresas, obtener_proveedores, obtener_monedas
from ..models.contrasenia_model import EntradaCompletaContrasenia
from ..db.connection import get_connection

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

@router.get("/proveedores-autocomplete")
def autocomplete_proveedores(q: str, cod_empresa: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    consulta = """
        SELECT cod_proveedor, nombre, nit
        FROM proveedores
        WHERE cod_empresa = %s AND (
            nombre LIKE %s OR
            cod_proveedor LIKE %s OR
            nit LIKE %s
        )
        LIMIT 15
    """
    like = f"%{q}%"
    cursor.execute(consulta, (cod_empresa, like, like, like))
    return cursor.fetchall()


# end-point para listar monedas
@router.get("/monedas")
def listar_monedas():
    return obtener_monedas()


