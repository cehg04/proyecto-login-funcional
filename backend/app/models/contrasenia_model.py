from pydantic import BaseModel
from datetime import date
from typing import Optional, List

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
    fecha_factura: date

# ------------ modelo de la anulacion de contraseña --------------------------------
class AnulacionContrasenia(BaseModel):
    cod_contrasenia: int
    cod_empresa: int
    usuario_x: int
    comentario: str = None

# ------------ Actualizacion de estado --------------------------------------------
class CambiarEstado(BaseModel):
    cod_contrasenia: int
    cod_empresa: int

class ListaCambiarEstado(BaseModel):
    detalles: List[CambiarEstado]
