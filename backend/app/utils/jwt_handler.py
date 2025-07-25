from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "tu_clave_secreta_super_segura"
ALGORITHM = "HS256"

def crear_token(data: dict, exp_minutes: int = 480):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=exp_minutes)
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verificar_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except Exception:
        return None
    

