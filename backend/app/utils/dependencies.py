from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..utils.jwt_handler import verificar_token


SECRET_KEY = "clave_secreta_segura"
ALGORITHM = "HS256"

security = HTTPBearer()

# Verifica si el token de sesión es válido
def verificar_sesion(request: Request):
    token = request.cookies.get("token")

    if not token:
        return RedirectResponse("/", status_code=302)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return RedirectResponse("/", status_code=302)


# obtiene el toquen para utilizarlo en el encabezado de la contraseña
def obtener_usuario_desde_token(authorization: str = Header(...)):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Formato de token inválido")
        
        token = authorization.split(" ")[1]
        payload = verificar_token(token)
        
        if not payload or "cod_usuario" not in payload:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        
        return payload["cod_usuario"]
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")