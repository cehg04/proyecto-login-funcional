from ..db.connection import get_connection
from ..utils.security import verify_password
from ..utils.jwt_handler import crear_token
from mysql.connector import Error

def autenticar_usuario(data):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND estado = 'A'", (data.usuario,))
        usuario = cursor.fetchone()

        if usuario and verify_password(data.contrasenia, usuario["contrasenia"]):
            token = crear_token({
                "cod_usuario": usuario["cod_usuario"],
                "usuario": usuario["usuario"],
                "nombre": usuario["nombre"]  # ✅ Incluir nombre en el token
            })
            return {"token": token, "usuario": usuario["usuario"]}
        else:
            return {"error": "Usuario o contraseña incorrectos o inactivo"}

    except Error as e:
        print("Error al autenticar usuario:", e)
        return {"error": "Error del servidor"}
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
