from ..db.connection import get_connection
from ..utils.security import hash_password
from mysql.connector import Error
from fastapi import HTTPException

def obtener_usuario():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cod_usuario, nombre, usuario, correo, estado FROM usuarios")
    resultado = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultado

def crear_usuario(data):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener el último código
        cursor.execute("SELECT MAX(cod_usuario) FROM usuarios")
        resultado = cursor.fetchone()
        nuevo_codigo = (resultado[0] or 0) + 1

        hashed = hash_password(data.contrasenia)

        query = """
        INSERT INTO usuarios (cod_usuario, nombre, usuario, contrasenia, correo, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nuevo_codigo, data.nombre, data.usuario, hashed, data.correo, "A"))
        conn.commit()

        return {"mensaje": f"Usuario creado exitosamente"}
    except Error as e:
        print("Error al crear usuario:", e)
        return {"error": f"Error al crear usuario: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def actualizar_usuario(cod_usuario: int, data):
    conn = get_connection()
    cursor = conn.cursor()
    campos = []
    valores = []

    for campo, valor in data.dict(exclude_unset=True).items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if not campos:
        raise HTTPException(status_code=400, detail="No hay datos para poder Actualizar")
    
    valores.append(cod_usuario)
    query = f"UPDATE usuarios SET {', '.join(campos)} WHERE cod_usuario = %s"

    cursor.execute(query, tuple(valores))
    conn.commit()
    cursor.close()
    conn.close()
    return {"msg": "Usuario actualizado con Exito"}