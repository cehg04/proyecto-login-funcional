from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from ..services.contrasenia_service import crear_contrasenias, obtener_empresas, obtener_monedas, crear_detalle_contrasenia, anular_contrasenia
from ..services.contrasenia_service import obtener_siguiente_linea, obtener_encabezados_filtrados, obtener_contrasenia_completa_filtrada
from ..models.contrasenia_model import DetalleContrasenia, EntradaContrasenia, AnulacionContrasenia
from ..db.connection import get_connection
from ..utils.dependencies import obtener_usuario_desde_token
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
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
                CASE WHEN e.estado = 'R' THEN 'Realizado'
                     WHEN e.estado = 'X' THEN 'Anulado'
                     ELSE e.estado
                END AS estado_encabezado,
                emp.nombre AS empresa_nombre,
                prov.nombre AS proveedor_nombre,
                d.num_factura,
                d.cod_moneda,
                d.monto,
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

        # PDF en memoria (ticket 80x250 mm)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=(80*mm, 250*mm),
                                rightMargin=5, leftMargin=5,
                                topMargin=5, bottomMargin=5)

        story = []
        styles = getSampleStyleSheet()

        # ENCABEZADO
        titulo = f"<para align='center'><b>{encabezado['empresa_nombre']}</b>   </para>"
        story.append(Paragraph(titulo, styles['Normal']))
        story.append(Spacer(1, 6))
        subtitulo = f"<para align='center'> Contraseña No. {encabezado['num_contrasenia']}</para>"
        story.append(Paragraph(subtitulo, styles['Normal']))
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Encabezado</b>", styles['Normal']))
        story.append(Paragraph(f"Empresa: {encabezado['empresa_nombre']}", styles['Normal']))
        story.append(Paragraph(f"Proveedor: {encabezado['proveedor_nombre']}", styles['Normal']))
        story.append(Paragraph(f"Fecha: {encabezado['fecha_contrasenia']}", styles['Normal']))
        story.append(Spacer(1, 8))

        # DETALLES
        story.append(Paragraph("<b>Detalles</b>", styles['Normal']))

        # Cabecera de tabla
        data = [["FACTURA No", "MONTO", "FECHA"]]

        # Filas
        for d in detalles:
            data.append([
                d.get("num_factura", ""),
                str(d.get("monto", "")),
                d.get("fecha_factura", "")
            ])

        # Tabla
        table = Table(data, colWidths=[25*mm, 12*mm, 18*mm, 20*mm])
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

        # Construir PDF
        doc.build(story)

        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=ticket_{cod_contrasenia}.pdf"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

