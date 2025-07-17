from pydantic import BaseModel

class LoginData(BaseModel):
    usuario: str
    contrasenia: str
