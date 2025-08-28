from datetime import datetime
from fastapi import HTTPException
from typing import Optional, List
from mysql.connector import Error
from ..db.connection import get_connection
from ..models.entregas_model import EncaEntregaCreate, DetalleEntrega

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
# crear el encabezado de la entrega
def crear_entrega(data: EncaEntregaCreate, usuario_actual: int):
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
# funcion para crear los detalles de la entrega
def crear_detalles_entrega(detalles: List[DetalleEntrega]):
    if not detalles:
        raise HTTPException(status_code=400, detail="No se proporcionaron detalles para guardar")

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener la última línea de esta entrega
        cursor.execute("""
            SELECT COALESCE(MAX(linea), 0)
            FROM detalle_entregas
            WHERE cod_entrega = %s AND cod_empresa = %s
            FOR UPDATE
        """, (detalles[0].cod_entrega, detalles[0].cod_empresa))
        linea = cursor.fetchone()[0] or 0

        query = """
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

        values_list = []
        for d in detalles:
            linea += 1  # Backend calcula la línea automáticamente
            values_list.append((
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

        cursor.executemany(query, values_list)
        conn.commit()

        return {"success": True, "mensaje": f"{len(detalles)} detalle(s) de entrega guardado(s) correctamente"}

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear detalles de entrega: {str(e)}")

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