from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

# ------------ Obtener el encabezado ---------------------------------------------
class EncabezadoContrasenia(BaseModel):
    cod_contrasenia: int
    fecha_contrasenia: str
    empresa_nombre: str
    proveedor_nombre: str
    estado: str

# ------------ modelo del encabezado de la contraseña ----------------------------
class EntradaContrasenia(BaseModel):
    cod_empresa: int
    cod_proveedor: str
    fecha_contrasenia: date

# ------------ modelo del detalle de la contraseña -------------------------------
class DetalleContrasenia(BaseModel):
    cod_contrasenia: Optional[int] = None
    cod_empresa: Optional[int] = None
    num_factura: int
    linea: Optional[int] = None
    cod_moneda: str
    monto: float
    retension_iva: Optional[str] = 'N'
    retension_isr: Optional[str] = 'N'
    numero_retension_iva: Optional[int] = None
    numero_retension_isr: Optional[int] = None
# ------------ modelo de la anulacion de contraseña --------------------------------

