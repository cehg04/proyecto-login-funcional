from fastapi import APIRouter, HTTPException, Request
from ..models.usuario_model import UsuarioCreate, UsuarioUpdate
from ..services.usuario_service import crear_usuario, obtener_usuarios, actualizar_usuario
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
    return obtener_usuarios()

# agregar opciones de usuario
@router.get("/opciones")
def obtener_opciones():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cod_opcion, nombre_opcion FROM opciones")
    opciones = cursor.fetchall()
    cursor.close()
    conn.close()
    return opciones

# Obtener usuario por ID
@router.get("/{cod_usuario}")
def obtener_usuario(cod_usuario: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cod_usuario, nombre, usuario, correo, estado FROM usuarios WHERE cod_usuario = %s", (cod_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    if usuario:
        return usuario
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

# Actualizar un usuario existente
@router.put("/{cod_usuario}")
def modificar_usuario(cod_usuario: int, data: UsuarioUpdate):
    return actualizar_usuario(cod_usuario, data)

# Cambiar el estado de un usuario
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
    

