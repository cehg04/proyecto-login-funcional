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
    num_factura: int
    cod_moneda: str
    monto: float
    retension_iva: Optional[str] = 'N'
    retension_isr: Optional[str] = 'N'
    numero_retension_iva: Optional[int] = None
    numero_retension_isr: Optional[int] = None
    estado: str = 'R'

# ------------ modelo del encabezado de la contraseña ----------------------------
class EntradaContrasenia(BaseModel):
    cod_empresa: int
    cod_proveedor: str
    fecha_contrasenia: date
# --------------------------------------------------------------------------------

# ------------ modelo del detalle de la contraseña -------------------------------
class DetalleContrasenia(BaseModel):
    cod_contrasenia: int
    cod_empresa: int
    num_factura: int
    linea: int
    cod_moneda: str
    monto: float
    retension_iva: Optional[str] = 'N'
    retension_isr: Optional[str] = 'N'
    numero_retension_iva: Optional[int] = None
    numero_retension_isr: Optional[int] = None
# --------------------------------------------------------------------------------

class EntradaCompletaContrasenia(BaseModel):
    encabezado: EntradaContrasenia
    detalles: List[EntradaDetalleContrasenia]