from pydantic import BaseModel
from typing import Optional

# modelo para crear un documento vario
class DocumentoVarioCreate(BaseModel):
    cod_empresa: int
    cod_tipo_documento: int
    cod_proveedor: Optional[str] = None
    nombre_solicitud: Optional[str] = None
    numero_documento: Optional[int] = None
    cod_moneda: str
    monto: float
    observaciones: Optional[str] = None

# modelo para ver un documento vario
class DocumentoVario(BaseModel):
    cod_documento: int
    cod_empresa: int
    cod_tipo_documento: int
    cod_proveedor: Optional[str] = None
    nombre_solicitud: Optional[str] = None
    numero_documento: Optional[int] = None
    cod_moneda: str
    monto: float
    observaciones: Optional[str] = None
    estado: str

# modelo para anular un documento
class AnularDocumentoRequest(BaseModel):
    cod_documento: int