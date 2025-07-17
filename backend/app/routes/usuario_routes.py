from fastapi import APIRouter, HTTPException, Request
from ..models.usuario_model import UsuarioCreate, UsuarioUpdate
from ..services.usuario_service import crear_usuario
from ..db.connection import get_connection

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

# Registrar los usuarios
@router.post("/") 
def registrar_usuario(data: UsuarioCreate):
    print("Datos recibidos:", data)
    return crear_usuario(data)

# Obtener todos los usuarios
@router.get("/")
def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cod_usuario, nombre, usuario, correo, estado FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios    

@router.put("/{cod_usuario}")
def actualizar_usuario(cod_usuario: int, data: UsuarioUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE usuarios
            SET nombre=%s, usuario=%s, correo=%s
            WHERE cod_usuario=%s
        """, (data.nombre, data.usuario, data.correo, cod_usuario))
        conn.commit()
        return {"mensaje": "Usuario actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.put("/estado/{cod_usuario}")
def cambiar_estado_usuario(cod_usuario: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT estado FROM usuarios WHERE cod_usuario = %s", (cod_usuario,))
        estado_actual = cursor.fetchone()
        if not estado_actual:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        nuevo_estado = "I" if estado_actual[0] == "A" else "A"
        cursor.execute("UPDATE usuarios SET estado=%s WHERE cod_usuario=%s", (nuevo_estado, cod_usuario))
        conn.commit()
        return {"mensaje": f"Estado actualizado: {nuevo_estado}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()