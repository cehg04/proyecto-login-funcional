from fastapi import APIRouter
from ..models.auth_model import LoginData
from ..services.auth_service import autenticar_usuario

router = APIRouter(prefix="/api", tags=["Login"])

@router.post("/login")
def login(data: LoginData):
    return autenticar_usuario(data)
