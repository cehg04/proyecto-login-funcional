from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import List, Optional
from ..models.entregas_model import EncaEntregaCreate, MostrarEntregas, DetalleEntrega, AnulacionEntrega
from ..services.entregas_service import crear_entrega, obtener_entregas, crear_detalles_entrega, obtener_entrega_completa, anular_entrega
from ..utils.dependencies import obtener_usuario_desde_token

router = APIRouter(prefix="/entregas",tags=["Entregas"])

# endpoint para crear el encabezado de la entrega
@router.post("/crear")
def crear_encabezado_entrega(
    data: EncaEntregaCreate,
    usuario_actual: int = Depends(obtener_usuario_desde_token)):

    resultado = crear_entrega(data, usuario_actual)

    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    
    print("JSON recibido:", data)
    return resultado
        
# endpoint para crear el detalle de la entrega
@router.post("/detalles")
def guardar_detalles_entrega(
    detalles: List[DetalleEntrega],
    usuario_actual: int = Depends(obtener_usuario_desde_token)
):
    if not detalles:
        raise HTTPException(status_code=400, detail="No se enviaron detalles para guardar")
    try:
        return crear_detalles_entrega(detalles)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar detalles: {str(e)}")
    
# endpoint para obtener los encabezados de las entregas
@router.get("/encabezados", response_model=List[MostrarEntregas])
def listar_entregas(
    cod_entrega: Optional[str] = Query(None),
    cod_empresa: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None)
):
    try:
        # Convertir a int si corresponde
        cod_entrega_int = int(cod_entrega) if cod_entrega and cod_entrega.isdigit() else None
        cod_empresa_int = int(cod_empresa) if cod_empresa and cod_empresa.isdigit() else None

        # Manejo de fechas: si no viene nada, usa la fecha de hoy
        fecha_inicio_val = fecha_inicio if fecha_inicio else datetime.now().strftime('%Y-%m-%d')
        fecha_fin_val = fecha_fin if fecha_fin else fecha_inicio_val

        resultados = obtener_entregas(
            cod_entrega=cod_entrega_int,
            cod_empresa=cod_empresa_int,
            fecha_inicio=fecha_inicio_val,
            fecha_fin=fecha_fin_val
        )
        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en listar_entregas: {str(e)}")

# endpoint para poder ver la entrega completa
@router.get("/detalle/{cod_entrega}/{cod_empresa}")
def ver_entrega_completa(cod_entrega: int, cod_empresa: int):

    try:
        resultado = obtener_entrega_completa(cod_entrega, cod_empresa)
        return resultado

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el endpoint: {str(e)}")
    
# endpoint para anular la Entrega
@router.post("/anular")
def anular_entrega_endpoint(request: AnulacionEntrega):
    try:
        resultado = anular_entrega(
            cod_entrega=request.cod_entrega,
            cod_empresa=request.cod_empresa,
            usuario_x=request.usuario_x
        )
        return {"menssage": "Entrega anulada exitosamente", "data": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al anular la entrega: {str(e)}")
    