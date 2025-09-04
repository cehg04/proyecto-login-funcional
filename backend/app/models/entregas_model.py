from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict, Any

# obtener las entregas creadas
class MostrarEntregas(BaseModel):
    cod_entrega: int
    cod_empresa: int
    num_entrega: str
    fecha_entrega: date
    tipo_entrega: str
    estado: str
    empresa_nombre: str

# crear el encabezado de las entregas de ambos 
class EncaEntregaCreate(BaseModel):
    cod_empresa: int
    fecha_entrega: date
    cod_usuario_entrega: int

# crear el detalle de las entregas de contraseñas
class DetalleEntrega(BaseModel):
    cod_entrega: int
    cod_empresa: int
    linea: Optional[int] = None
    cod_contrasenia: int 
    cod_empresa_contrasenia: int
    linea_contrasenia: Optional[int] = None
    num_factura: Optional[int] = None
    cod_moneda: str
    monto: float
    retension_iva: Optional[str] = 'N'
    retension_isr: Optional[str] = 'N'
    numero_retension_iva: Optional[int] = None
    numero_retension_isr: Optional[int] = None
    estado: Optional[str] = 'P'
    cod_documento: Optional[int] = None

# crear el detalle de las entregas de docuementos
class DetalleEntregaDc(BaseModel):
    cod_entrega: int
    cod_empresa: int
    linea: Optional[int] = None
    cod_moneda: str
    monto: float
    estado: Optional[str] = 'P'
    cod_documento: int  


# Anulacion de la entrega
class AnulacionEntrega(BaseModel):
    cod_entrega: int
    cod_empresa: int
    usuario_x: int



