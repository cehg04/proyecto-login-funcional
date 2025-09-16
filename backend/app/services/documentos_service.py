from fastapi import HTTPException
from mysql.connector import Error
from ..db.connection import get_connection
from ..models.documentos_model import DocumentoVarioCreate

# funcion para obtener documentos varios pendientes
def obtener_documentos_pendientes():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT
                dv.cod_documento,
                emp.nombre AS empresa_nombre, 
                dv.cod_tipo_documento,
                dv.cod_proveedor,
                dv.nombre_solicitud,
                dv.numero_documento,
                dv.cod_moneda,
                dv.monto,
                dv.observaciones,
                CASE
                    WHEN dv.estado = 'P' THEN 'Pendiente'
                    WHEN dv.estado = 'R' THEN 'Recibido'
                    WHEN dv.estado = 'E' THEN 'Entregado'
                    WHEN dv.estado = 'X' THEN 'Anulado'
                END AS estado,
                emp.nombre AS empresa_nombre,
                m.abreviatura AS moneda_descripcion,
                td.nombre_documento AS tipo_documento
            FROM documentos_varios dv
            JOIN empresas emp ON dv.cod_empresa = emp.cod_empresa
            JOIN monedas m ON dv.cod_moneda = m.cod_moneda
            JOIN tipo_documentos td ON dv.cod_tipo_documento = td.cod_tipo_documento
            WHERE dv.estado = 'P'
            ORDER BY dv.cod_documento
        """
        cursor.execute(sql)
        resultados = cursor.fetchall()
        return resultados
    except Error as e:
        print(f"Error al obtener documentos varios pendientes: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# funcion para obtener documentos varios sin duplicados
def obtener_documentos_varios():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
                SELECT 
                    d.cod_documento,
                    t.nombre_documento AS tipo_documento,
                    e.nombre AS empresa_nombre,
                    p.nombre AS proveedor_nombre,
                    d.nombre_solicitud,
                    d.numero_documento,
                    CONCAT(m.cod_moneda, ' ', FORMAT(d.monto, 2)) AS monto_con_moneda,  
                    COALESCE(d.numero_retension_iva, 'N/A') AS numero_retension_iva,
                    COALESCE(d.numero_retension_isr, 'N/A') AS numero_retension_isr,
                    d.observaciones,
                    CASE
                        WHEN d.estado = 'P' THEN 'Pendiente'
                        WHEN d.estado = 'E' THEN 'Entregado'
                        WHEN d.estado = 'R' THEN 'Recibido'
                        WHEN d.estado = 'X' THEN 'Anulado'
                    END AS estado
                FROM documentos_varios d
                JOIN empresas e ON d.cod_empresa = e.cod_empresa
                JOIN tipo_documentos t ON d.cod_tipo_documento = t.cod_tipo_documento
                LEFT JOIN proveedores p ON d.cod_proveedor = p.cod_proveedor AND d.cod_empresa = p.cod_empresa
                JOIN monedas m ON d.cod_moneda = m.cod_moneda
                WHERE d.estado IN ('P', 'E', 'R', 'X')
                ORDER BY d.cod_documento DESC;
            """)
        rows = cursor.fetchall()
        return [
                {
                    "cod_documento": r[0],
                    "tipo_documento": r[1],
                    "empresa_nombre": r[2],
                    "proveedor_nombre": r[3],
                    "nombre_solicitud": r[4],
                    "numero_documento": r[5],
                    "monto_con_moneda": r[6],
                    "numero_retension_iva": r[7],
                    "numero_retension_isr": r[8],
                    "observaciones": r[9],
                    "estado": r[10]
            }
            for r in rows
        ]
    except Exception as e:
        print("Error al obtener documentos varios:", e)
        return []
    finally:
        cursor.close()
        conn.close()



# funcion para anular documento
def anular_documento(cod_documento: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE documentos_varios
            SET estado = 'X'
            WHERE cod_documento = %s AND estado = 'P'
        """, (cod_documento,))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            return {"success": False, "message": "No se encontró el documento o ya esta Anulado."}
        
        return {"success": True, "message": "Documento anulado correctamente."}
    
    except Exception as e:
        print("Error al anular documento:", e)
        return {"success": False, "message": str(e)}
    
    finally:
        cursor.close()
        conn.close()

# funcion para crear un documento
def crear_documento_vario(doc: DocumentoVarioCreate):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener el siguiente cod_documento 
        cursor.execute("SELECT MAX(cod_documento) FROM documentos_varios")
        resultado = cursor.fetchone()
        nuevo_cod = (resultado[0] + 1) if resultado[0] is not None else 1

        # Insertar el documento
        cursor.execute("""
            INSERT INTO documentos_varios (
                cod_documento, cod_empresa, cod_tipo_documento,
                cod_proveedor, nombre_solicitud, numero_documento,
                cod_moneda, monto, observaciones, estado, retension_iva, retension_isr,
                numero_retension_iva, numero_retension_isr
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            nuevo_cod,
            doc.cod_empresa,
            doc.cod_tipo_documento,
            doc.cod_proveedor,
            doc.nombre_solicitud,
            doc.numero_documento,
            doc.cod_moneda,
            doc.monto,
            doc.observaciones,
            'P',
            doc.retencion_iva,
            doc.retencion_isr,
            doc.numero_retension_iva,
            doc.numero_retension_isr
        ))

        conn.commit()
        return {
            "mensaje": "Documento creado correctamente",
            "cod_documento": nuevo_cod
        }

    except Error as e:
        print(f"Error al insertar documentos_varios: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar documento")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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

# funcion listar los tipos de documentos
def obtener_tipo_documentos():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT cod_tipo_documento, nombre_documento
            FROM tipo_documentos
            WHERE estado = 'A'
        """)
        return [
            {"cod_tipo_documento": r[0], "nombre_documento": r[1]}
            for r in cursor.fetchall()
        ]
    except Exception as e:
        print("Error al obtener tipo_documentos:", e)
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