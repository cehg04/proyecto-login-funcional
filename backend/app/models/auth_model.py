from pydantic import BaseModel

# modelo para el login
class LoginData(BaseModel):
    usuario: str
    contrasenia: str
