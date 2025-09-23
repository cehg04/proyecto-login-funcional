from fastapi import APIRouter, HTTPException, Query
from ..services.reportes_service import obtener_reporte_contrasenias_todas, obtener_reporte_documentos_todos
from ..services import reportes_service

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/contrasenias-todas")
def route_contrasenias_todas(
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    cod_empresa: str = Query(None)
):
    try:
        print(f"Parámetros recibidos: fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}, cod_empresa={cod_empresa}")
        resultado = obtener_reporte_contrasenias_todas(fecha_inicio, fecha_fin, cod_empresa)
        print(f"Registros encontrados: {len(resultado)}")
        return resultado
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error en endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documentos-todos")
def route_documentos_todos(
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    cod_empresa: str = Query(None)
):
    try:
        return obtener_reporte_documentos_todos(fecha_inicio, fecha_fin, cod_empresa)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    

@router.get("/empresas-con-contrasenias")
def get_empresas_con_contrasenias():
    try:
        return reportes_service.obtener_empresas_con_contrasenias()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
