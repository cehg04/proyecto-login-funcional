from ..db.connection import get_connection
from mysql.connector import Error
from ..models.contrasenia_model import EntradaCompletaContrasenia
from datetime import datetime

# obtener las contraseñas
def obtener_contrasenias(cod_empresa: int):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        #obtener encabezados
        cursor.execute("""
            SELECT cod_contrasenia, cod_empresa, cod_empresa_proveedor, num_contrasenia,
                   cod_proveedor, fecha_contrasenia, estado
            FROM enca_contrasenias
            WHERE cod_empresa = %s AND estado = 'R'
            ORDER BY fecha_contrasenia DESC
        """, (cod_empresa,))
        encabezados = cursor.fetchall()

        #obtener los detalles por cada contrasenia
        for enc in encabezados:
            cursor.execute("""
                SELECT linea, num_factura, cod_moneda, monto,
                       retension_iva, retension_isr,
                       numero_retension_iva, numero_retension_isr, estado
                FROM detalle_contrasenias
                WHERE cod_contrasenia = %s AND cod_empresa = %s
                ORDER BY linea ASC
            """, (enc["cod_contrasenia"], enc["cod_empresa"]))
            detalles = cursor.fetchall()
            enc["detalles"] = detalles  
        return encabezados
        
    
    except Error as e:
        print("Error al obtener contraseñas:", e)
        return []
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# creacion de contraseñas
def crear_contrasenias(data, usuario_actual):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener siguiente código de encabezado
        cursor.execute("SELECT MAX(cod_contrasenia) FROM enca_contrasenias")
        resultado = cursor.fetchone()
        nuevo_codigo = (resultado[0] or 0) + 1

        cod_empresa = data['cod_empresa']
        cod_empresa_proveedor = cod_empresa

        # Insertar encabezado
        query = """
            INSERT INTO enca_contrasenias (
                cod_contrasenia, cod_empresa, cod_empresa_proveedor,
                num_contrasenia, cod_proveedor, fecha_contrasenia,
                usuario_creacion, fecha_creacion, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            nuevo_codigo,
            cod_empresa,
            cod_empresa_proveedor,
            data['num_contrasenia'],
            data['cod_proveedor'],
            data['fecha_contrasenia'],
            usuario_actual,
            datetime.now(),
            'R'
        ))

        linea = 0

        # Insertar detalles
        for detalle in data['detalles']:
            cursor.execute("""
                INSERT INTO detalle_contrasenias (
                    cod_contrasenia, cod_empresa, linea,
                    num_factura, cod_moneda,
                    monto, retension_iva, retension_isr,
                    numero_retension_iva, numero_retension_isr,
                    estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    nuevo_codigo,                    # viene del encabezado insertado
                    data['cod_empresa'],            # también viene del encabezado
                    linea,
                    detalle['num_factura'],
                    detalle['cod_moneda'],
                    detalle['monto'],
                    'S' if detalle.get('retension_iva', False) else 'N',
                    'S' if detalle.get('retension_isr', False) else 'N',
                    detalle.get('numero_retension_iva'),  # puede ser None
                    detalle.get('numero_retension_isr'),  # puede ser None
                    'P'
                ))
            linea += 1

        conn.commit()
        return {"mensaje": "Contraseña creada con éxito", "cod_contrasenia": nuevo_codigo}

    except Error as e:
        print("Error al crear contraseña:", e)
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# lista para las empresas
def obtener_empresas():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT cod_empresa, nombre FROM empresas WHERE estado = 'A'")
        rows = cursor.fetchall()
        return [{"cod_empresa": r[0], "nombre": r[1]} for r in rows]
    except Exception as e:
        print("Error al obtener empresas:", e)
        return []
    finally:
        cursor.close()
        conn.close()


# lista para los proveedores
def obtener_proveedores(cod_empresa):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT cod_proveedor, nombre
            FROM proveedores
            WHERE cod_empresa = %s AND estado = 'A'
        """, (cod_empresa,))
        rows = cursor.fetchall()
        return [{"cod_proveedor": r[0], "nombre": r[1]} for r in rows]
    finally:
        cursor.close()
        conn.close()


# lista para los tipo monedas
def obtener_monedas():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT cod_moneda, abreviatura FROM monedas")
        return [{"cod_moneda": r[0], "abreviatura": r[1]} for r in cursor.fetchall()]
    except Exception as e:
        print("Error al obtener monedas:", e)
        return []
    finally:
        cursor.close()
        conn.close()
