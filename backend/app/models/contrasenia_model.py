from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class DetalleContrasenia(BaseModel):
    linea: int
    num_factura: int
    cod_moneda: str
    monto: float
    retension_iva: Optional[str]
    retension_isr: Optional[str]
    numero_retension_iva: Optional[int]
    numero_retension_isr: Optional[int]
    estado: str

class EncaContrasenia(BaseModel):
    cod_contrasenia: int
    cod_empresa: int
    cod_empresa_proveedor: int
    num_contrasenia: str
    cod_proveedor: str
    fecha_contrasenia: date
    usuarios_creacion: int
    fecha_creacion: datetime
    estado: str
    usuario_x: Optional[int]
    fecha_x: Optional[datetime]
    comentario: Optional[str]
    detalles: Optional[List[DetalleContrasenia]] = []
    