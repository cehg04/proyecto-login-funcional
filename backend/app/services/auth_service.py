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
        cursor.execute("""
            SELECT cod_usuario, usuario, nombre, contrasenia, estado 
            FROM usuarios 
            WHERE usuario = %s AND estado = 'A'
        """, (data.usuario,))
        usuario = cursor.fetchone()

        if usuario and verify_password(data.contrasenia, usuario["contrasenia"]):
            return {  # Devuelve todos los campos necesarios
                "cod_usuario": usuario["cod_usuario"],
                "usuario": usuario["usuario"],
                "nombre": usuario["nombre"],
                "estado": usuario["estado"]
            }
        else:
            return None  # Mejor que devolver un diccionario con error

    except Error as e:
        print("Error al autenticar usuario:", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
