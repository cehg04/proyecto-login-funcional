from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: str
    usuario: str
    correo: EmailStr

class UsuarioCreate(UsuarioBase):
    contrasenia: str

class UsuarioUpdate(UsuarioBase):
    estado: Optional[str]  # Opcional para update parcial

class UsuarioOut(UsuarioBase):
    cod_usuario: int
    estado: str
