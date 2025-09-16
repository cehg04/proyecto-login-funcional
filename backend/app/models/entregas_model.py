from pydantic import BaseModel
from datetime import date
from typing import Optional
from typing import List 

# modelo para obtener las entregas creadas
class MostrarEntregas(BaseModel):
    cod_entrega: int
    cod_empresa: int
    num_entrega: str
    fecha_entrega: date
    tipo_entrega: str
    estado: str
    empresa_nombre: str

# modelo para crear el encabezado de las entregas
class EncaEntregaCreate(BaseModel):
    cod_empresa: int
    fecha_entrega: date
    cod_usuario_entrega: int

# modelo para crear el detalle de las entregas de contraseñas
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

# modelo para crear el detalle de las entregas de docuementos
class DetalleEntregaDc(BaseModel):
    cod_entrega: int
    cod_empresa: int
    linea: Optional[int] = None
    cod_moneda: str
    monto: float
    estado: Optional[str] = 'P'
    cod_documento: int  


# modelo de Anulacion de la entrega
class AnulacionEntrega(BaseModel):
    cod_entrega: int
    cod_empresa: int
    usuario_x: int

# modelo para Mostrar entregas pendientes
class EntregaPendiente(BaseModel):
    cod_entrega: int
    cod_empresa: int
    fecha_entrega: date
    usuario_creacion: str
    estado: str

# modelo para el boton guardar seleccion
class GuardarRequest(BaseModel):
    cod_entrega: int
    cod_empresa: int
    lineas: List[int]

# modelo para el boton de confirmacion parcial
class ConfirmarRequest(BaseModel):
    cod_entrega: int
    cod_empresa: int
    comentario: str
    


