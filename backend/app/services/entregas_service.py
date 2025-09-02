from datetime import datetime
from fastapi import HTTPException
from typing import Optional, List
from mysql.connector import Error
from ..db.connection import get_connection
from ..models.entregas_model import EncaEntregaCreate, DetalleEntrega, DetalleEntregaDc

# obtener la lista de encabezados de las entregas
def obtener_entregas(cod_entrega: Optional[int] = None, cod_empresa: Optional[int] = None, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None): 
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT
                e.cod_entrega,
                e.cod_empresa,
                e.num_entrega,
                e.fecha_entrega,
                emp.nombre AS empresa_nombre,
                CASE 
                    WHEN e.tipo_entrega = 'DC' THEN 'Documento con contraseña'
                    WHEN e.tipo_entrega = 'DS' THEN 'Documento sin contraseña'
                END AS tipo_entrega,
                CASE
                    WHEN e.estado = 'P' THEN 'Pendiente'
                    WHEN e.estado = 'R' THEN 'Recibido'
                    WHEN e.estado = 'X' THEN 'Anulado'
                END AS estado
            FROM enca_entregas e
            JOIN empresas emp ON e.cod_empresa = emp.cod_empresa
        """
        filtros = []
        params = []

        if fecha_inicio and fecha_fin:
            filtros.append("DATE(e.fecha_entrega) BETWEEN %s AND %s")
            params.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            filtros.append("DATE(e.fecha_entrega) = %s")
            params.append(fecha_inicio)

        if cod_entrega is not None:
            filtros.append("e.cod_entrega = %s")
            params.append(cod_entrega)

        if cod_empresa is not None:
            filtros.append("e.cod_empresa = %s")
            params.append(cod_empresa)

        if filtros:
            sql += " WHERE " + " AND ".join(filtros)

        sql += " ORDER BY e.fecha_entrega DESC"

        cursor.execute(sql, tuple(params))
        resultados = cursor.fetchall()
        return resultados
           
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener entregas: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# -------------------------------------------------------------------------------------------
# crear el encabezado de la entrega de contraseñas
def crear_entrega_contrasenia(data: EncaEntregaCreate, usuario_actual: int):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cod_empresa = data.cod_empresa

        # obtener el codigo de entrega siguiente
        cursor.execute("""
            SELECT MAX(cod_entrega)
            FROM enca_entregas
            WHERE cod_empresa = %s
        """, (cod_empresa,))
        resultado = cursor.fetchone()
        nuevo_codigo = (resultado[0] or 0) + 1

        # generar el numero de entrega
        num_entrega = generar_num_entrega(data.cod_empresa, nuevo_codigo)

        # insertar el encabezado de la entrega
        query = """
            INSERT INTO enca_entregas (
                cod_entrega, cod_empresa, num_entrega, fecha_entrega,
                usuario_creacion, fecha_creacion, estado, tipo_entrega
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            nuevo_codigo,
            data.cod_empresa,
            num_entrega,
            data.fecha_entrega,
            usuario_actual,
            datetime.now(),
            "P",  # estado por defecto = pendiente
            "DC"
        ))
        conn.commit()
        return {
            "mensaje": "Encabezado de entrega creado correctamente",
            "cod_entrega": nuevo_codigo,
            "num_entrega": num_entrega,
            "cod_empresa": data.cod_empresa
        }
    except Error as e:
        print("Error al crear entrega:", e)
        return {"error": str(e)}
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# crear el encabezado de la entrega de documentos
def crear_entrega_documentos(data: EncaEntregaCreate, usuario_actual: int):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cod_empresa = data.cod_empresa

        # obtener el codigo de entrega siguiente
        cursor.execute("""
            SELECT MAX(cod_entrega)
            FROM enca_entregas
            WHERE cod_empresa = %s
        """, (cod_empresa,))
        resultado = cursor.fetchone()
        nuevo_codigo = (resultado[0] or 0) + 1

        # generar el numero de entrega
        num_entrega = generar_num_entrega(data.cod_empresa, nuevo_codigo)

        # insertar el encabezado de la entrega
        query = """
            INSERT INTO enca_entregas (
                cod_entrega, cod_empresa, num_entrega, fecha_entrega,
                usuario_creacion, fecha_creacion, estado, tipo_entrega
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            nuevo_codigo,
            data.cod_empresa,
            num_entrega,
            data.fecha_entrega,
            usuario_actual,
            datetime.now(),
            "P",  
            "DS"
        ))
        conn.commit()
        return {
            "mensaje": "Encabezado de entrega creado correctamente",
            "cod_entrega": nuevo_codigo,
            "num_entrega": num_entrega,
            "cod_empresa": data.cod_empresa
        }
    except Error as e:
        print("Error al crear entrega:", e)
        return {"error": str(e)}
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# funcion para generar el numero de entrega
def generar_num_entrega(cod_empresa: int, nuevo_codigo: int) -> str:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener abreviatura de la empresa
        cursor.execute("SELECT abreviatura FROM empresas WHERE cod_empresa = %s", (cod_empresa,))
        resultado = cursor.fetchone()

        if resultado is None:
            raise ValueError("Empresa no encontrada")
        
        abreviatura_empresa = resultado['abreviatura']

        # Generar número de entrega con formato
        num_entrega = f"ENT-{abreviatura_empresa}-{nuevo_codigo:07d}"
        return num_entrega
    
    except Error as e:
        print("Error al generar número de entrega:", e)
        raise HTTPException(status_code=500, detail="Error al generar número de entrega")
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
        
# funcion para obtener la lista de empresas
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
# -------------------------------------------------------------------------------------------
# funcion para crear los detalles de la entrega de contraseñas
def crear_detalles_entrega_contrasenia(detalles: List[DetalleEntrega]):
    if not detalles:
        raise HTTPException(status_code=400, detail="No se proporcionaron detalles para procesar")

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener la última línea de la entrega
        cursor.execute("""
            SELECT COALESCE(MAX(linea), 0)
            FROM detalle_entregas
            WHERE cod_entrega = %s AND cod_empresa = %s
            FOR UPDATE
        """, (detalles[0].cod_entrega, detalles[0].cod_empresa))
        linea = cursor.fetchone()[0] or 0

        # Preparar query de UPDATE para detalle_contrasenias
        sql_update = """
            UPDATE detalle_contrasenias
            SET estado = 'E'
            WHERE cod_contrasenia = %s
              AND cod_empresa = %s
              AND linea = %s
              AND estado = 'P'
        """

        # Preparar query de INSERT para detalle_entregas
        sql_insert = """
            INSERT INTO detalle_entregas (
                cod_entrega,
                cod_empresa,
                linea,
                cod_contrasenia,
                cod_empresa_contrasenia,
                linea_contrasenia,
                num_factura,
                cod_moneda,
                monto,  
                retension_iva,
                retension_isr,
                numero_retension_iva,
                numero_retension_isr,
                estado,
                cod_documento
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values_insert = []
        total_actualizados = 0

        # Procesar cada detalle
        for d in detalles:
            # update primero
            cursor.execute(sql_update, (d.cod_contrasenia, d.cod_empresa_contrasenia, d.linea_contrasenia))
            total_actualizados += cursor.rowcount

            # si se actualizó correctamente, lo insertamos
            linea += 1
            values_insert.append((
                d.cod_entrega,
                d.cod_empresa,
                linea,
                d.cod_contrasenia,
                d.cod_empresa_contrasenia,
                d.linea_contrasenia,
                d.num_factura,
                d.cod_moneda,
                d.monto,
                d.retension_iva,
                d.retension_isr,
                d.numero_retension_iva,
                d.numero_retension_isr,
                d.estado,
                d.cod_documento
            ))

        if total_actualizados == 0:
            raise HTTPException(status_code=404, detail="No se encontró detalle pendiente para actualizar")

        # ejecutar los inserts en lote
        cursor.executemany(sql_insert, values_insert)

        conn.commit()

        return {
            "success": True,
            "mensaje": f"{total_actualizados} detalles actualizados y {len(values_insert)} insertados en la entrega"
        }

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar entrega: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# funcion para crear los detalles de la entrega de los documentos
def crear_detalles_entrega_documentos(detalles: List[DetalleEntregaDc]):
    if not detalles:
        raise HTTPException(status_code=400, detail="No se proporcionaron detalles para procesar")

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener la última línea de la entrega
        cursor.execute("""
            SELECT COALESCE(MAX(linea), 0)
            FROM detalle_entregas
            WHERE cod_entrega = %s AND cod_empresa = %s
            FOR UPDATE
        """, (detalles[0].cod_entrega, detalles[0].cod_empresa))
        linea = cursor.fetchone()[0] or 0

        # Preparar query de UPDATE para detalle_contrasenias
        sql_update = """
            UPDATE documentos_varios
            SET estado = 'E'
            WHERE cod_documento = %s
            AND estado = 'P'
        """


        # Preparar query de INSERT para detalle_entregas
        sql_insert = """
            INSERT INTO detalle_entregas (
                cod_entrega,
                cod_empresa,
                linea,
                cod_moneda,
                monto,  
                estado,
                cod_documento
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values_insert = []
        total_actualizados = 0

        # Procesar cada detalle
        for d in detalles:
            # update primero
            cursor.execute(sql_update, (d.cod_documento,))
            total_actualizados += cursor.rowcount

            # si se actualizó correctamente, lo insertamos
            linea += 1
            values_insert.append((
                d.cod_entrega,
                d.cod_empresa,
                linea,
                d.cod_moneda,
                d.monto,
                d.estado,
                d.cod_documento
            ))

        if total_actualizados == 0:
            raise HTTPException(status_code=404, detail="No se encontró detalle pendiente para actualizar")

        # ejecutar los inserts en lote
        cursor.executemany(sql_insert, values_insert)

        conn.commit()

        return {
            "success": True,
            "mensaje": f"{total_actualizados} detalles actualizados y {len(values_insert)} insertados en la entrega"
        }

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar entrega: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# funcion para obtener la siguiente linea de entrega
def obtener_siguiente_linea_entrega(cod_entrega: int, cod_empresa: int):
    """Obtiene el siguiente número de línea para una entrega"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT COALESCE(MAX(linea), 0) + 1 as siguiente_linea
            FROM detalle_entregas
            WHERE cod_entrega = %s AND cod_empresa = %s
        """
        cursor.execute(sql, (cod_entrega, cod_empresa))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 1
    except Error as e:
        print(f"Error al obtener siguiente línea: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# funcion para ver el encabezado y detalle junto
def obtener_entrega_completa(cod_entrega: int, cod_empresa: int):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        #Encabezado
        query_encabezado = """
            SELECT
                e.cod_entrega,
                e.cod_empresa,
                e.num_entrega,
                CASE
                    WHEN e.tipo_entrega = 'DC' THEN 'Documento con Contraseña'
                    WHEN e.tipo_entrega = 'DS' THEN 'Documento sin Contraseña'
                END AS tipo_entrega,
                CASE
                    WHEN e.estado = 'P' THEN 'Pendiente'
                    WHEN e.estado = 'R' THEN 'Recibido'
                    WHEN e.estado = 'X' THEN 'Anulado'
                END AS estado
            FROM enca_entregas e
            WHERE e.cod_entrega = %s AND e.cod_empresa = %s
        """
        cursor.execute(query_encabezado, (cod_entrega, cod_empresa))
        encabezado = cursor.fetchone()

        if not encabezado:
            raise HTTPException(status_code=404, detail= "Encabezado de entrega no encontrado")
        
        # Detalle de la entrega
        query_detalle = """
            select
                COALESCE(d.num_factura, 'N/A') AS num_factura,
                d.cod_moneda,
                d.monto,
                CASE
                    WHEN d.retension_iva = 'S' THEN 'Si Tiene'
                    WHEN d.retension_iva = 'N' THEN 'No Tiene'
                    ELSE 'N/A'
                END AS retension_iva,
                CASE
                    WHEN d.retension_isr = 'S' THEN 'Si Tiene'
                    WHEN d.retension_isr = 'N' THEN 'No Tiene'
                    ELSE 'N/A'
                END AS retension_isr,
                COALESCE(d.numero_retension_iva, 'N/A') AS numero_retension_iva,
                COALESCE(d.numero_retension_isr, 'N/A') AS numero_retension_isr,
                CASE
                    WHEN d.estado = 'P' THEN 'Pendiente'
                    WHEN d.estado = 'C' THEN 'Confirmado'
                END AS estado
                FROM detalle_entregas d
                WHERE d.cod_entrega = %s AND d.cod_empresa = %s
                ORDER BY d.linea
        """
        cursor.execute(query_detalle, (cod_entrega, cod_empresa))
        detalles = cursor.fetchall()
        
        return {
            "encabezado": encabezado,
            "detalles": detalles
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la entrega: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# funcion para Anular la entrega del encabezado
def anular_entrega(cod_entrega: int, cod_empresa: int, usuario_x: int):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar existencia
        check_query = """
            SELECT estado FROM enca_entregas
            WHERE cod_entrega = %s AND cod_empresa = %s
        """
        cursor.execute(check_query, (cod_entrega, cod_empresa))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="La entrega no existe")
        if result[0] == 'X':
            raise HTTPException(status_code=400, detail="La entrega ya esta anulada")
        
        # Actualizar estado
        query = """
            UPDATE enca_entregas
            SET estado = 'X', usuario_x = %s, fecha_x = %s
            WHERE cod_entrega = %s AND cod_empresa = %s
        """
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(query, (usuario_x, fecha_actual, cod_entrega, cod_empresa))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=500, detail="No se pudo anular la entrega")
        
        conn.commit()
        return {"status": "ok", "mensaje": "Entrega anulada correctamente"}
    
    except Error as e:
        print("Error al anular la entrega:", e)
        raise HTTPException(status_code=500, detail=f"Error al anular la entrega: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()