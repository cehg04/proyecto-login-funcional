from fastapi import HTTPException
from ..db.connection import get_connection

def obtener_reporte_contrasenias_todas(fecha_inicio: str = None, fecha_fin: str = None, cod_empresa: str = None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT
                ec.cod_empresa,
                ec.num_contrasenia,
                DATE_FORMAT(ec.fecha_creacion, '%Y-%m-%d') AS fecha_creacion,
                dc.num_factura,
                CONCAT(dc.cod_moneda, ' ', FORMAT(dc.monto, 2)) AS monto,
                CASE
                    WHEN dc.estado = 'P' THEN 'Pendiente'
                    WHEN dc.estado = 'E' THEN 'Entregado'
                    WHEN dc.estado = 'R' THEN 'Recibido'
                    ELSE 'Sin Estado'
                END AS estado
            FROM enca_contrasenias ec
            JOIN detalle_contrasenias dc
                ON ec.cod_contrasenia = dc.cod_contrasenia
                AND ec.cod_empresa = dc.cod_empresa
        """

        filtros = []
        params = []

        if fecha_inicio and fecha_fin:
            filtros.append("DATE(ec.fecha_creacion) BETWEEN %s AND %s")
            params.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            filtros.append("DATE(ec.fecha_creacion) = %s")
            params.append(fecha_inicio)

        if cod_empresa:
            filtros.append("ec.cod_empresa = %s")
            params.append(cod_empresa)

        if filtros:
            sql += " WHERE " + " AND ".join(filtros)

        sql += " ORDER BY ec.fecha_creacion DESC"

        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte de contraseñas: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def obtener_reporte_documentos_todos(fecha_inicio: str = None, fecha_fin: str = None, cod_empresa: str = None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT 
                dv.cod_empresa,
                dv.cod_documento,
                DATE_FORMAT(dv.fecha_creacion, '%Y-%m-%d') AS fecha_creacion,
                td.nombre_documento AS tipo_documento,
                dv.numero_documento,
                CONCAT(dv.cod_moneda, ' ', FORMAT(dv.monto, 2)) AS monto,
                CASE
                    WHEN dv.estado = 'P' THEN 'Pendiente'
                    WHEN dv.estado = 'E' THEN 'Entregado'
                    WHEN dv.estado = 'R' THEN 'Recibido'
                    WHEN dv.estado = 'X' THEN 'Anulado'
                    ELSE 'Sin Estado'
                END AS estado
            FROM documentos_varios dv
            JOIN tipo_documentos td 
                ON dv.cod_tipo_documento = td.cod_tipo_documento
        """

        filtros = []
        params = []

        if fecha_inicio and fecha_fin:
            filtros.append("DATE(dv.fecha_creacion) BETWEEN %s AND %s")
            params.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            filtros.append("DATE(dv.fecha_creacion) = %s")
            params.append(fecha_inicio)

        if cod_empresa:
            filtros.append("dv.cod_empresa = %s")
            params.append(cod_empresa)

        if filtros:
            sql += " WHERE " + " AND ".join(filtros)

        sql += " ORDER BY dv.fecha_creacion DESC"

        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte de documentos varios: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def obtener_empresas_con_contrasenias():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT DISTINCT ec.cod_empresa, e.nombre AS nombre_empresa
            FROM enca_contrasenias ec
            JOIN empresas e ON ec.cod_empresa = e.cod_empresa
            ORDER BY ec.cod_empresa
        """
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        raise Exception(f"Error al obtener empresas con contraseñas: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

