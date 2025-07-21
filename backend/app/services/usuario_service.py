from ..db.connection import get_connection
from ..utils.security import hash_password
from mysql.connector import Error
from fastapi import HTTPException

# creamos un nuevo usuario
def crear_usuario(data):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener el siguiente código de usuario
        cursor.execute("SELECT MAX(cod_usuario) FROM usuarios")
        resultado = cursor.fetchone()
        nuevo_codigo = (resultado[0] or 0) + 1

        # Hashear la contraseña
        hashed = hash_password(data.contrasenia)

        # Insertar usuario
        query = """
        INSERT INTO usuarios (cod_usuario, nombre, usuario, contrasenia, correo, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nuevo_codigo, data.nombre, data.usuario, hashed, data.correo, "A"))

        # Obtener todas las opciones disponibles
        cursor.execute("SELECT cod_opcion FROM opciones")
        todas_las_opciones = [fila[0] for fila in cursor.fetchall()]

        # Convertir permisos recibidos en set para fácil comparación
        permisos_seleccionados = set(data.permisos or [])

        # Insertar permisos S/N según corresponda
        for cod_opcion in todas_las_opciones:
            permiso_valor = 'S' if cod_opcion in permisos_seleccionados else 'N'
            cursor.execute("""
                INSERT INTO permisos (cod_usuario, cod_opcion, permiso)
                VALUES (%s, %s, %s)
            """, (nuevo_codigo, cod_opcion, permiso_valor))

        conn.commit()
        return {"mensaje": f"Usuario creado exitosamente"}
    
    except Error as e:
        print("Error al crear el usuario:", e)
        return {"error": f"Error al crear el usuario: {str(e)}"}
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# obtenemos los datos del usuario
def obtener_usuarios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cod_usuario, nombre, usuario, correo, estado FROM usuarios")
    resultado = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultado

# Actualizar un usuario existente
def actualizar_usuario(cod_usuario: int, data):
    conn = get_connection()
    cursor = conn.cursor()
    campos = []
    valores = []

    for campo, valor in data.dict(exclude_unset=True).items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if not campos:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    valores.append(cod_usuario)
    query = f"UPDATE usuarios SET {', '.join(campos)} WHERE cod_usuario = %s"

    cursor.execute(query, tuple(valores))
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Usuario actualizado con éxito"}
