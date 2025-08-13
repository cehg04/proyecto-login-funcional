from ..db.connection import get_connection
from mysql.connector import Error
from ..models.contrasenia_model import EntradaContrasenia, DetalleContrasenia
from datetime import datetime
from fastapi import HTTPException
from typing import Optional

# ---------------------- creacion de la vista de contrasenias  ----------------------------------------------------
# obtener el encabezado filtrado
def obtener_encabezados_filtrados(cod_contrasenia: Optional[int] = None, cod_empresa: Optional[int] = None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT
                e.cod_contrasenia,
                e.num_contrasenia,
                e.cod_empresa,
                DATE_FORMAT(e.fecha_creacion, '%Y-%m-%d %H:%i:%s') AS fecha_creacion,
                emp.nombre AS empresa_nombre,
                prov.nombre AS proveedor_nombre,
                e.estado
            FROM enca_contrasenias e
            JOIN empresas emp ON e.cod_empresa = emp.cod_empresa
            JOIN proveedores prov ON e.cod_proveedor = prov.cod_proveedor AND e.cod_empresa_proveedor = prov.cod_empresa
        """

        filtros = []
        params = []

        if cod_contrasenia is not None:
            filtros.append("e.cod_contrasenia = %s")
            params.append(cod_contrasenia)

        if cod_empresa is not None:
            filtros.append("e.cod_empresa = %s")
            params.append(cod_empresa)

        if filtros:
            sql += " WHERE " + " AND ".join(filtros)

        sql += " ORDER BY e.fecha_creacion DESC"

        cursor.execute(sql, tuple(params))
        resultados = cursor.fetchall()
        return resultados

    except Error as e:
        print(f"Error en obtener encabezados filtrados: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# obtener el detalle y el encabezado juntos
def obtener_contrasenia_completa_filtrada(cod_contrasenia: int, cod_empresa: int):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # === Encabezado filtrado ===
        query_encabezado = """
            SELECT 
                e.cod_empresa,
                e.cod_proveedor,
                e.num_contrasenia,
                e.estado,
                emp.nombre AS empresa_nombre,
                prov.nombre AS proveedor_nombre
            FROM enca_contrasenias e
            JOIN empresas emp ON e.cod_empresa = emp.cod_empresa
            JOIN proveedores prov ON e.cod_proveedor = prov.cod_proveedor
                AND e.cod_empresa_proveedor = prov.cod_empresa
            WHERE e.cod_contrasenia = %s
              AND e.cod_empresa = %s
        """
        cursor.execute(query_encabezado, (cod_contrasenia, cod_empresa))
        encabezado = cursor.fetchone()

        if not encabezado:
            raise HTTPException(status_code=404, detail="Encabezado no encontrado")

        # === Detalle filtrado ===
        query_detalle = """
            SELECT num_factura, cod_moneda, monto,
                   retension_iva, retension_isr,
                   numero_retension_iva, numero_retension_isr,
                   estado
            FROM detalle_contrasenias
            WHERE cod_contrasenia = %s AND cod_empresa = %s
        """
        cursor.execute(query_detalle, (cod_contrasenia, cod_empresa))
        detalles = cursor.fetchall()

        return {
            "encabezado": encabezado,
            "detalles": detalles
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la contraseña: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------- creacion del servicio de encabezado de la contrasenia ------------------------------------
# creacion de contraseñas
def crear_contrasenias(data: EntradaContrasenia, usuario_actual: int):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cod_empresa = data.cod_empresa

        # Obtener siguiente código de encabezado
        cursor.execute("""
            SELECT MAX(cod_contrasenia) 
            FROM enca_contrasenias
            WHERE cod_empresa = %s
            """, (cod_empresa,))

        resultado = cursor.fetchone()
        nuevo_codigo = (resultado[0] or 0) + 1

        # Generar número de contraseña
        num_contrasenia = generar_num_contrasenia(data.cod_empresa, nuevo_codigo)

        query = """
            INSERT INTO enca_contrasenias (
                cod_contrasenia, cod_empresa, cod_empresa_proveedor,
                num_contrasenia, cod_proveedor, fecha_contrasenia,
                usuario_creacion, fecha_creacion, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            nuevo_codigo,
            data.cod_empresa,
            data.cod_empresa, 
            num_contrasenia,
            data.cod_proveedor,
            data.fecha_contrasenia,
            usuario_actual,
            datetime.now(),
            'R'
        ))

        conn.commit()
        return {
            "mensaje": "Encabezado de contraseña creado correctamente",
            "cod_contrasenia": nuevo_codigo,
            "num_contrasenia": num_contrasenia,
            "cod_empresa": data.cod_empresa
        }

    except Error as e:
        print("Error al crear contraseña:", e)
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# funcion para crear el numero de la contraseña
def generar_num_contrasenia(cod_empresa: int, nuevo_codigo: int) -> str:
    conn = None
    cursor = None
    abreviatura_empresa = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener la abreviatura de la empresa
        cursor.execute("SELECT abreviatura FROM empresas WHERE cod_empresa = %s", (cod_empresa,))
        resultado = cursor.fetchone()

        if resultado is None:
            raise ValueError("No se encontró la empresa con el código proporcionado.")

        abreviatura_empresa = resultado['abreviatura']

        # Generar el número de contraseña
        num_contrasenia = f"CON-{abreviatura_empresa}-{nuevo_codigo:07d}"
        return num_contrasenia

    except Error as e:
        print("Error al generar num_contrasenia:", e)
        raise HTTPException(status_code=500, detail="Error al generar num_contrasenia")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# funcion para listar las empresas
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

# funcion listar los proveedores
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


# ---------------------- creacion del servicio de detalle de la contrasenia ------------------------------------
# funcion para crear los detalles de la contraseña
def crear_detalle_contrasenia(detalle: DetalleContrasenia):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Validar que num_factura no exista ya para esa contraseña y empresa
        cursor.execute("""
        SELECT 1 FROM detalle_contrasenias WHERE num_factura = %s
        """, (detalle.num_factura,))
        existe = cursor.fetchone()
        if existe:
            raise HTTPException(status_code=400, detail="Número de factura ya existe")

        # Obtener el valor máximo actual de línea para esa contraseña + empresa
        cursor.execute("""
            SELECT MAX(linea) FROM detalle_contrasenias
            WHERE cod_contrasenia = %s AND cod_empresa = %s
        """, (detalle.cod_contrasenia, detalle.cod_empresa))
        resultado = cursor.fetchone()
        max_linea = resultado[0] if resultado[0] is not None else -1
        nueva_linea = max_linea + 1

        # Insertar el detalle
        cursor.execute("""
            INSERT INTO detalle_contrasenias (
                cod_contrasenia, cod_empresa, linea,
                num_factura, cod_moneda, monto,
                retension_iva, retension_isr,
                numero_retension_iva, numero_retension_isr
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            detalle.cod_contrasenia,
            detalle.cod_empresa,
            nueva_linea,
            detalle.num_factura,
            detalle.cod_moneda,
            detalle.monto,
            detalle.retension_iva,
            detalle.retension_isr,
            detalle.numero_retension_iva,
            detalle.numero_retension_isr
        ))

        conn.commit()
        return {"mensaje": "Detalle guardado correctamente", "linea": nueva_linea}
    except Error as e:
        print(f"Error al insertar detalle_contrasenias: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el detalle")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# funcion para obtener la linea siguiente
def obtener_siguiente_linea(cod_contrasenia: int, cod_empresa: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT MAX(linea) FROM detalle_contrasenias
                WHERE cod_contrasenia = %s AND cod_empresa = %s
            """
            cursor.execute(query, (cod_contrasenia, cod_empresa))
            resultado = cursor.fetchone()
            if resultado[0] is None:
                return 0
            else:
                return resultado[0] + 1
    finally:
        conn.close()

# funcion para lista para los tipo monedas
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






