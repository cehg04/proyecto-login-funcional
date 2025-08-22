from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.documentos_model import DocumentoVarioCreate, AnularDocumentoRequest
from ..services.documentos_service import crear_documento_vario, obtener_documentos_varios, anular_documento, obtener_tipo_documentos


router = APIRouter(prefix="/documentos", tags=["Documentos"])


# Crear un nuevo documento
@router.post("/crear")
def ruta_crear_documento(doc: DocumentoVarioCreate):
    try:
        return crear_documento_vario(doc)
    except HTTPException as e:
        raise e
    except Exception as e:
        print("Error inesperado en la ruta crear_documento:", e)
        raise HTTPException(status_code=500, detail="Error inesperado al crear documento")

# Listar tipos de documentos activos
@router.get("/tipos")
def listar_tipos_documentos():
    return obtener_tipo_documentos()

# Listar documentos varios
@router.get("/varios")
def listar_documentos_varios():
    return obtener_documentos_varios()

# Anular un documento
@router.put("/anular")
def anular_documento_route(request: AnularDocumentoRequest):
    resultado = anular_documento(request.cod_documento)
    if not resultado["success"]:
        raise HTTPException(status_code=400, detail=resultado["message"])
    return {"mensaje": resultado["message"]}



