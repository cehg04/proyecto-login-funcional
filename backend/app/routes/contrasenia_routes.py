from fastapi import APIRouter, Query, HTTPException,Depends
from datetime import datetime
from fastapi.responses import JSONResponse
from typing import List, Optional
from ..services.contrasenia_service import crear_contrasenias, obtener_empresas, obtener_monedas, crear_detalle_contrasenia
from ..services.contrasenia_service import obtener_siguiente_linea, obtener_encabezados_filtrados, obtener_contrasenia_completa_filtrada
from ..models.contrasenia_model import DetalleContrasenia, EntradaContrasenia, AnularRequest
from ..db.connection import get_connection
from ..utils.dependencies import obtener_usuario_desde_token

router = APIRouter(prefix="/contrasenias", tags=["contrasenias"])

# ---------------- Obtener todos los encabezados -------------------------------------------------------------------------

# end-point para obtener los encabezados
from datetime import datetime, timedelta

@router.get("/ver-encabezados")
def listar_encabezados(
    cod_contrasenia: Optional[str] = Query(None),
    cod_empresa: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),  # Nueva: fecha inicial
    fecha_fin: Optional[str] = Query(None)     # Nueva: fecha finalhit s
):
    try:
        cod_contrasenia_int = int(cod_contrasenia) if cod_contrasenia and cod_contrasenia.isdigit() else None
        cod_empresa_int = int(cod_empresa) if cod_empresa and cod_empresa.isdigit() else None
        
        # Fechas por defecto (hoy como inicio, y fin opcional)
        fecha_inicio_val = fecha_inicio if fecha_inicio else datetime.now().strftime('%Y-%m-%d')
        fecha_fin_val = fecha_fin if fecha_fin else fecha_inicio_val  # Si no hay fin, usa la inicio

        resultados = obtener_encabezados_filtrados(
            cod_contrasenia_int,
            cod_empresa_int,
            fecha_inicio_val,
            fecha_fin_val
        )
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# end-point para toda la contraseña
@router.get("/ver-completa-filtrada")
def ver_contrasenia_completa_filtrada(
    cod_contrasenia: int = Query(..., description="Código de la contraseña"),
    cod_empresa: int = Query(..., description="Código de la empresa")
):
    return obtener_contrasenia_completa_filtrada(cod_contrasenia, cod_empresa)


# ---------------- Anulacion de encabezados para la contrasela ------------------------------------------------------------


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



