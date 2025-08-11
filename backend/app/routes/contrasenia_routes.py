from fastapi import APIRouter, Query, HTTPException,Depends
from ..services.contrasenia_service import crear_contrasenias, obtener_empresas, obtener_proveedores, obtener_monedas, crear_detalle_contrasenia, obtener_siguiente_linea
from ..models.contrasenia_model import DetalleContrasenia, EntradaContrasenia
from ..db.connection import get_connection
from ..utils.dependencies import obtener_usuario_desde_token

router = APIRouter(prefix="/contrasenias", tags=["contrasenias"])

# ---------------- creacion de encabezados para la contrasela ------------------------------------------------------------

# end-point para crear contraseñas
@router.post("/crear-contrasenia")
def crear_contrasenia_endpoint(data: EntradaContrasenia, usuario_actual: int = Depends(obtener_usuario_desde_token)):
    try:
        return crear_contrasenias(data, usuario_actual)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# end-point para listar empresas
@router.get("/empresas")
def listar_empresa():
    return obtener_empresas()

# end-point para el autocompletado de los proveedores
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

# ---------------- creacion de lo detalles para la contrasela ------------------------------------------------------------

# end-point para los detalles de la contraseña
@router.post("/detalle")
def guardar_detalle_contrasenia(detalle: DetalleContrasenia):
    try:
        crear_detalle_contrasenia(detalle)
        return {"mensaje": "Detalle guardado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# end-poin para la linea del detalle
@router.get("/linea")
def get_siguiente_linea(cod_contrasenia: int, cod_empresa: int):
    try:
        siguiente_linea = obtener_siguiente_linea(cod_contrasenia, cod_empresa)
        return {"linea": siguiente_linea}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# end-point para listar monedas
@router.get("/monedas")
def listar_monedas():
    return obtener_monedas()



