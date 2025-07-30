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

class EntradaDetalleContrasenia(BaseModel):
    usuario: str
    contrasenia: str
    sistema: str
    observacion: str
    tipo_contrasenia: str

class EntradaContrasenia(BaseModel):
    cod_empresa: int
    cod_proveedor: int
    fecha_contrasenia: date
    tipo_contrasenia: str
    estado: str

class EntradaCompletaContrasenia(BaseModel):
    encabezado: EntradaContrasenia
    detalles: List[EntradaDetalleContrasenia]