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
    retencion_iva: Optional[str] = None   
    retencion_isr: Optional[str] = None   
    numero_retension_iva: Optional[int] = None
    numero_retension_isr: Optional[int] = None

# modelo para ver un documento vario
class DocumentoVario(BaseModel):
    cod_documento: int
    cod_tipo_documento: int
    cod_empresa: int
    cod_proveedor: Optional[str] = None
    nombre_solicitud: Optional[str] = None
    numero_documento: Optional[int] = None
    cod_moneda: str
    monto: float
    numero_retension_iva: Optional[int] = None
    numero_retension_isr: Optional[int] = None
    observaciones: Optional[str] = None
    estado: str

# modelo para anular un documento
class AnularDocumentoRequest(BaseModel):
    cod_documento: int