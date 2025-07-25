from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


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


