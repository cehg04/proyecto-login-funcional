from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    usuario: str
    contrasenia: str
    correo: EmailStr

class UsuarioBase(BaseModel):
    nombre: str
    usuario: str
    correo: EmailStr

class UsuarioCreate(UsuarioBase):
    contrasenia: str

class UsuarioUpdate(UsuarioBase):
    pass

class UsuarioOut(UsuarioBase):
    cod_usuario: int
    estado: str