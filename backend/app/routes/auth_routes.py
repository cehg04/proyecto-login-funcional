from fastapi import HTTPException, Depends
from fastapi import APIRouter
from ..models.auth_model import LoginData
from ..services.auth_service import autenticar_usuario, obtener_permisos_por_usuario
from ..utils.jwt_handler import crear_token  


router = APIRouter(prefix="/api", tags=["Login"])

# Ruta para iniciar sesión
@router.post("/login")
def login(data: LoginData):
    usuario_autenticado = autenticar_usuario(data)
    
    if not usuario_autenticado:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # obtener permisos del usuario
    permisos = obtener_permisos_por_usuario(usuario_autenticado["cod_usuario"])

    # Crear el token incluyendo la información esencial del usuario
    token = crear_token({
        "cod_usuario": usuario_autenticado["cod_usuario"],
        "usuario": usuario_autenticado["usuario"],
        "nombre": usuario_autenticado["nombre"],  
        "permisos": permisos
    })

    return {
        "token": token,
        "user_data": {  # Datos adicionales para el frontend
            "nombre": usuario_autenticado["nombre"],
            "permisos": permisos
        }
    }

