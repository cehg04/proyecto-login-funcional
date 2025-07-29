from ..db.connection import get_connection
from mysql.connector import Error


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