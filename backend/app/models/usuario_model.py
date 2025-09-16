from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import List

# Base model for Usuario
class UsuarioBase(BaseModel):
    nombre: str
    usuario: str
    correo: EmailStr

# Base para crear un nuevo usuario
class UsuarioCreate(UsuarioBase):
    contrasenia: str
    permisos: Optional[List[int]] = []
    
# Base para actualizar usuario
class UsuarioUpdate(UsuarioBase):
    estado: Optional[str]  # Opcional para update parcial

# Base para un Usuario inactivo
class UsuarioOut(UsuarioBase):
    cod_usuario: int
    estado: str
