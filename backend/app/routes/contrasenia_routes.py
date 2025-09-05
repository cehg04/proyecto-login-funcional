from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
from ..services.contrasenia_service import crear_contrasenias, obtener_empresas, obtener_monedas, crear_detalle_contrasenia, anular_contrasenia
from ..services.contrasenia_service import obtener_siguiente_linea, obtener_encabezados_filtrados, obtener_contrasenia_completa_filtrada, obtener_detalles_pendientes
from ..models.contrasenia_model import DetalleContrasenia, EntradaContrasenia, AnulacionContrasenia
from ..db.connection import get_connection
from ..utils.dependencies import obtener_usuario_desde_token
from reportlab.lib.pagesizes import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO

    
router = APIRouter(prefix="/contrasenias", tags=["contrasenias"])

# ---------------- Obtener todos los encabezados -------------------------------------------------------------------------

# end-point para obtener los encabezados
from datetime import datetime, timedelta

@router.get("/ver-encabezados")
def listar_encabezados(
    cod_contrasenia: Optional[str] = Query(None),
    cod_empresa: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),  # Nueva: fecha inicial
    fecha_fin: Optional[str] = Query(None)     # Nueva: fecha finalhit s
):
    try:
        cod_contrasenia_int = int(cod_contrasenia) if cod_contrasenia and cod_contrasenia.isdigit() else None
        cod_empresa_int = int(cod_empresa) if cod_empresa and cod_empresa.isdigit() else None
        
        # Fechas por defecto (hoy como inicio, y fin opcional)
        fecha_inicio_val = fecha_inicio if fecha_inicio else datetime.now().strftime('%Y-%m-%d')
        fecha_fin_val = fecha_fin if fecha_fin else fecha_inicio_val  # Si no hay fin, usa la inicio

        resultados = obtener_encabezados_filtrados(
            cod_contrasenia_int,
            cod_empresa_int,
            fecha_inicio_val,
            fecha_fin_val
        )
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# end-point para toda la contraseña
@router.get("/ver-completa-filtrada")
def ver_contrasenia_completa_filtrada(
    cod_contrasenia: int = Query(..., description="Código de la contraseña"),
    cod_empresa: int = Query(..., description="Código de la empresa")
):
    return obtener_contrasenia_completa_filtrada(cod_contrasenia, cod_empresa)


# ---------------- Anulacion de encabezados para la contrasela ------------------------------------------------------------
# end-point para anular contraseñas
@router.post("/anular")
def anular_contrasenia_endpoint(request: AnulacionContrasenia):
    try:
        resultado = anular_contrasenia(
            cod_contrasenia=request.cod_contrasenia,
            cod_empresa=request.cod_empresa,
            usuario_x=request.usuario_x,
            comentario=request.comentario
        )
        return {"message": "Contraseña anulada exitosamente", "data": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al anular contraseña: {str(e)}")

# ---------------- creacion de encabezados para la contrasela ------------------------------------------------------------

# end-point para crear contraseñas
@router.post("/crear-contrasenia")
def crear_contrasenia_endpoint(data: EntradaContrasenia, usuario_actual: int = Depends(obtener_usuario_desde_token)):
    try:
        return crear_contrasenias(data, usuario_actual)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# end-point para listar empresas
@router.get("/empresas")
def listar_empresa():
    return obtener_empresas()

# end-point para el autocompletado de los proveedores
@router.get("/proveedores-autocomplete")
def autocomplete_proveedores(q: str, cod_empresa: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    consulta = """
        SELECT cod_proveedor, nombre, nit
        FROM proveedores
        WHERE cod_empresa = %s AND (
            nombre LIKE %s OR
            cod_proveedor LIKE %s OR
            nit LIKE %s
        )
        LIMIT 15
    """
    like = f"%{q}%"
    cursor.execute(consulta, (cod_empresa, like, like, like))
    return cursor.fetchall()



# ---------------- creacion de lo detalles para la contrasela ------------------------------------------------------------

# end-point para los detalles de la contraseña
@router.post("/detalle")
def guardar_detalle_contrasenia(detalle: DetalleContrasenia):
    try:
        crear_detalle_contrasenia(detalle)
        return {"mensaje": "Detalle guardado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# end-poin para la linea del detalle
@router.get("/linea")
def get_siguiente_linea(cod_contrasenia: int, cod_empresa: int):
    try:
        siguiente_linea = obtener_siguiente_linea(cod_contrasenia, cod_empresa)
        return {"linea": siguiente_linea}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# end-point para listar monedas
@router.get("/monedas")
def listar_monedas():
    return obtener_monedas()

# ---------------- Creacion de documento PDF ------------------------------------------------------------
# end-point para generar PDF en formato ticket

@router.get("/imprimir-encabezado/{cod_contrasenia}/{cod_empresa}")
def imprimir_encabezado(cod_contrasenia: int, cod_empresa: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Traemos encabezado + detalle
        cursor.execute("""
            SELECT 
                e.num_contrasenia,
                DATE_FORMAT(e.fecha_contrasenia, '%Y-%m-%d') AS fecha_contrasenia,
                e.usuario_creacion,
                CASE WHEN e.estado = 'R' THEN 'Realizado'
                     WHEN e.estado = 'X' THEN 'Anulado'
                     ELSE e.estado
                END AS estado_encabezado,
                emp.nombre AS empresa_nombre,
                prov.nombre AS proveedor_nombre,
                d.num_factura,
                DATE_FORMAT(d.fecha_factura, '%Y-%m-%d') AS fecha_factura,
                CONCAT(d.cod_moneda, ' ', FORMAT(d.monto, 2)) AS monto_con_moneda,
                d.retension_iva,
                d.retension_isr,
                d.numero_retension_iva,
                d.numero_retension_isr,
                CASE WHEN d.estado = 'R' THEN 'Recibido'
                     WHEN d.estado = 'P' THEN 'Pendiente'
                     WHEN d.estado = 'E' THEN 'Entregado'
                END AS estado_detalle
            FROM enca_contrasenias e
            JOIN empresas emp ON e.cod_empresa = emp.cod_empresa
            JOIN proveedores prov ON e.cod_proveedor = prov.cod_proveedor
                                   AND e.cod_empresa_proveedor = prov.cod_empresa
            LEFT JOIN detalle_contrasenias d 
                   ON e.cod_contrasenia = d.cod_contrasenia 
                  AND e.cod_empresa = d.cod_empresa
            WHERE e.cod_contrasenia = %s
              AND e.cod_empresa = %s;
        """, (cod_contrasenia, cod_empresa))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            raise HTTPException(status_code=404, detail="Contraseña no encontrada")

        encabezado = rows[0]
        detalles = rows

        # obtenemos el nombre del usuario creador
        usuario_creacion = encabezado.get("usuario_creacion")
        nombre_emisor = ""
        if usuario_creacion:
            conn2 = get_connection()
            cursor2 = conn2.cursor(dictionary=True)
            cursor2.execute("SELECT nombre FROM usuarios WHERE cod_usuario = %s", (usuario_creacion,))
            usuario_row = cursor2.fetchone()
            if usuario_row:
                nombre_emisor = usuario_row["nombre"]
            cursor2.close()
            conn2.close()

        # PDF en memoria (ticket 80x250 mm)
        buffer = BytesIO()
        styles = getSampleStyleSheet()

        # Estilos personalizados
        titulo_style = ParagraphStyle(
            name='TituloGrande',
            parent=styles['Normal'],
            fontSize=16,
            alignment=1,  
            spaceAfter=6,
            leading=16,
            fontName='Times-Bold'
        )
        subtitulo_style = ParagraphStyle(
            name='Subtitulo',
            parent=styles['Normal'],
            fontSize=9,
            alignment=1,  
            spaceAfter=6,
            leading=12,
            fontName='Times-Roman'
        )
        centrado_style = ParagraphStyle(
            name='Centrado',
            parent=styles['Normal'],
            alignment=1,  
            fontSize=7,
            fontName='Times-Roman',
        )
        encabezado_style = ParagraphStyle(
            name='Encabezado',
            parent=styles['Normal'],
            fontSize=8,
            alignment=0,  
            spaceAfter=4,
            leading=10,
            fontName='Times-Roman'
        )

        # formato de fecha
        fecha_contrasenia = encabezado.get("fecha_contrasenia", "")
        if fecha_contrasenia:
            try:
                fecha_contrasenia = datetime.strptime(fecha_contrasenia, '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                pass 
                
        story = []

        # ENCABEZADO
        titulo = f"<b>{encabezado['empresa_nombre']}</b>"
        story.append(Paragraph(titulo, titulo_style))
        subtitulo = f"Contraseña No. <b>{encabezado['num_contrasenia']}</b>"
        story.append(Paragraph(subtitulo, subtitulo_style))
        story.append(Spacer(1, 6))

        story.append(Paragraph(f"GUATEMALA, {fecha_contrasenia}", encabezado_style))
        story.append(Paragraph(f"<b>RECIBIMOS DE:</b> {encabezado['proveedor_nombre']}", encabezado_style))
        story.append(Spacer(1, 8))

        # texto agregado del formato
        story.append(Paragraph("LOS SIGUIENTES DOCUMENTOS PARA REVISION Y PAGO", centrado_style))
        story.append(Spacer(1, 8))

        # Cabecera de tabla
        data = [["FACTURA No.", "FECHA", "MONTO"]]

        # Filas
        for d in detalles:
            monto_moneda = d.get("monto_con_moneda", "")
            fecha_factura = d.get("fecha_factura", "")
            if fecha_factura:
                try:
                    fecha_factura = datetime.strptime(fecha_factura, '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    pass
            data.append([
                d.get("num_factura", ""),
                fecha_factura,
                monto_moneda
                
            ])

        # Tabla
        table = Table(data, colWidths=[25*mm, 22*mm, 22*mm, 20*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.black),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,0), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))

        story.append(table)
        story.append(Spacer(1, 8))
        story.append(Paragraph("LOS DIAS DE PAGOS MIERCOLES DE 14:00 A 16:00 HORAS", centrado_style))
        story.append(Paragraph("LOS DIAS DE PAGOS VIERNES DE 14:00 A 15:00 HORAS", centrado_style))
        story.append(Paragraph("RECEPCION DE FACTURAS: LUNES, MIERCOLES Y VIERNES DE 8:00 AM A 12:00PM", centrado_style))
        story.append(Spacer(1, 18))

        # linea para nuestra firma
        story.append(Paragraph(f"<b>EMISOR:</b> {nombre_emisor if nombre_emisor else ''}", centrado_style))
        story.append(Spacer(1, 1))
        story.append(Spacer(1, 10))
        story.append(Paragraph("5a. CALLE 5-19 ZONA 9 PBX: (502) 2427-5800 ", centrado_style))

        # calcular altura del contenido
        tmp_doc = SimpleDocTemplate(buffer, pagesize=(80*mm, 1000*mm))
        tmp_story = list(story)
        tmp_doc.build(tmp_story)

        # medimos los altos reales en los puntos
        from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
        story_height = sum([flow.wrap(80*mm, 1000*mm)[1] + flow.getSpaceAfter() for flow in story])

        # convertir a mm y darle un margen extra
        page_height = (story_height / 2.83465) + 20  
        if page_height < 150:
            page_height = 150

        buffer.seek(0)
        buffer.truncate(0)
        doc = SimpleDocTemplate(buffer, pagesize=(80*mm, 150*mm),
                                rightMargin=5, leftMargin=5,
                                topMargin=5, bottomMargin=5)
        # Construir PDF
        doc.build(story)

        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=ticket_{cod_contrasenia}.pdf"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- funcion para obtener los detalles de las contraseñas ------------------------------------------------------------
@router.get("/detalles-pendientes")
def obtener_detalles_pendientes_api():
    try:
        detalles = obtener_detalles_pendientes()
        return {
            "success": True,
            "data": detalles,
            "total": len(detalles)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


