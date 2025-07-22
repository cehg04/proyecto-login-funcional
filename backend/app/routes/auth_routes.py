from fastapi import HTTPException
from fastapi import APIRouter
from ..models.auth_model import LoginData
from ..services.auth_service import autenticar_usuario
from ..utils.jwt_handler import crear_token  

router = APIRouter(prefix="/api", tags=["Login"])

@router.post("/login")
def login(data: LoginData):
    usuario_autenticado = autenticar_usuario(data)
    
    if not usuario_autenticado:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    token = crear_token({
        "cod_usuario": usuario_autenticado["cod_usuario"],
        "usuario": usuario_autenticado["usuario"]
    })
    
    return {
        "token": token,
        "cod_usuario": usuario_autenticado["cod_usuario"],
        "usuario": usuario_autenticado["usuario"],
        "nombre": usuario_autenticado.get("nombre", "")
    }
