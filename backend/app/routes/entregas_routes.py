from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from typing import List, Optional
from ..models.entregas_model import EncaEntregaCreate, MostrarEntregas, DetalleEntrega, AnulacionEntrega, DetalleEntregaDc, EntregaPendiente, GuardarRequest, ConfirmarRequest
from ..services.entregas_service import crear_entrega_contrasenia, crear_entrega_documentos, crear_detalles_entrega_contrasenia,crear_detalles_entrega_documentos ,obtener_entregas, obtener_entrega_completa, anular_entrega, obtener_entregas_pendientes, obtener_recepcion_completa, actualizar_estado_detalle, confirmar_entrega_parcial
from ..models.entregas_model import EntregaPendiente
from ..utils.dependencies import obtener_usuario_desde_token
from ..db.connection import get_connection
from reportlab.lib.pagesizes import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/entregas",tags=["Entregas"])

# endpoint para crear el encabezado de la entrega de contraseñas
@router.post("/crear-contrasenia")
def crear_encabezado_entrega(
    data: EncaEntregaCreate,
    usuario_actual: int = Depends(obtener_usuario_desde_token)):

    resultado = crear_entrega_contrasenia(data, usuario_actual)

    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    
    print("JSON recibido:", data)
    return resultado

# endpoint para crear el encabezado de la entrega de documentos
@router.post("/crear-documento")
def crear_encabezado_entrega(
    data: EncaEntregaCreate,
    usuario_actual: int = Depends(obtener_usuario_desde_token)):

    resultado = crear_entrega_documentos(data, usuario_actual)

    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    
    print("JSON recibido:", data)
    return resultado

# endpoint para crear el detalle de la entrega de contraseñas
@router.post("/detalles-contrasenia")
def guardar_detalles_entrega(
    detalles: List[DetalleEntrega],
    usuario_actual: int = Depends(obtener_usuario_desde_token)
):
    if not detalles:
        raise HTTPException(status_code=400, detail="No se enviaron detalles para guardar")
    try:
        return crear_detalles_entrega_contrasenia(detalles)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar detalles: {str(e)}")
    
# endpoint para crear el detalle de la entrega de documentos
@router.post("/detalles-documentos")
def guardar_detalles_entrega(
    detalles: List[DetalleEntregaDc],
    usuario_actual: int = Depends(obtener_usuario_desde_token)
):
    if not detalles:
        raise HTTPException(status_code=400, detail="No se enviaron detalles para guardar")
    try:
        return crear_detalles_entrega_documentos(detalles)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar detalles: {str(e)}")
    
# endpoint para obtener los encabezados de las entregas
@router.get("/encabezados", response_model=List[MostrarEntregas])
def listar_entregas(
    cod_entrega: Optional[str] = Query(None),
    cod_empresa: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None)
):
    try:
        # Convertir a int si corresponde
        cod_entrega_int = int(cod_entrega) if cod_entrega and cod_entrega.isdigit() else None
        cod_empresa_int = int(cod_empresa) if cod_empresa and cod_empresa.isdigit() else None

        # Manejo de fechas: si no viene nada, usa la fecha de hoy
        fecha_inicio_val = fecha_inicio if fecha_inicio else datetime.now().strftime('%Y-%m-%d')
        fecha_fin_val = fecha_fin if fecha_fin else fecha_inicio_val

        resultados = obtener_entregas(
            cod_entrega=cod_entrega_int,
            cod_empresa=cod_empresa_int,
            fecha_inicio=fecha_inicio_val,
            fecha_fin=fecha_fin_val
        )
        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en listar_entregas: {str(e)}")


@router.get("/detalle/{cod_entrega}/{cod_empresa}")
def ver_entrega_completa(cod_entrega: int, cod_empresa: int):
    try:
        return obtener_entrega_completa(cod_entrega, cod_empresa)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el endpoint ver_entrega_completa: {str(e)}")
    
    
# endpoint para anular la Entrega
@router.post("/anular")
def anular_entrega_endpoint(request: AnulacionEntrega):
    try:
        resultado = anular_entrega(
            cod_entrega=request.cod_entrega,
            cod_empresa=request.cod_empresa,
            usuario_x=request.usuario_x
        )
        return {"menssage": "Entrega anulada exitosamente", "data": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al anular la entrega: {str(e)}")

# endpoint para la lista de usuarios
@router.get("/usuarios")
def listar_usuarios_entregas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT u.cod_usuario, u.nombre
    FROM usuarios u
    INNER JOIN permisos p ON u.cod_usuario = p.cod_usuario
    WHERE p.cod_opcion = 10
        AND p.permiso = 'S'
        AND u.estado = 'A';
    """
    cursor.execute(query)
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return usuarios

# end-point para generar el PDF en formato ticket
@router.get("/imprimir-entrega/{cod_entrega}/{cod_empresa}")
def imprimir_entrega(cod_entrega: int, cod_empresa: int):
    try:
        # Obtener datos desde el service
        resultado = obtener_entrega_completa(cod_entrega, cod_empresa)
        encabezado = resultado["encabezado"]
        detalles = resultado["detalles"]

        if not encabezado:
            raise HTTPException(status_code=404, detail="Entrega no encontrada")

        #  Obtener nombre del usuario que entrega
        nombre_emisor = ""
        cod_usuario = encabezado.get("cod_usuario_entrega")
        if cod_usuario:
            conn2 = get_connection()
            cursor2 = conn2.cursor(dictionary=True)
            cursor2.execute("SELECT nombre FROM usuarios WHERE cod_usuario = %s", (cod_usuario,))
            usuario_row = cursor2.fetchone()
            if usuario_row:
                nombre_emisor = usuario_row.get("nombre", "")
            cursor2.close()
            conn2.close()

        #  Preparar PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=(80*mm, 150*mm),
                                rightMargin=5, leftMargin=5,
                                topMargin=5, bottomMargin=5)
        story = []
        styles = getSampleStyleSheet()

        # Estilos
        titulo_style = ParagraphStyle(name='Titulo', parent=styles['Normal'], fontSize=16, alignment=1, spaceAfter=6, fontName='Times-Bold')
        subtitulo_style = ParagraphStyle(name='Subtitulo', parent=styles['Normal'], fontSize=9, alignment=1, spaceAfter=4, fontName='Times-Roman')
        centrado_style = ParagraphStyle(name='Centrado', parent=styles['Normal'], alignment=1, fontSize=7, fontName='Times-Roman')

        # Formatear fecha
        fecha_entrega = encabezado.get("fecha_entrega", "")
        if fecha_entrega:
            try:
                fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                pass

        # Encabezado del ticket
        story.append(Paragraph(f"<b>{encabezado.get('empresa_nombre', '')}</b>", titulo_style))
        story.append(Paragraph(f"Entrega No. <b>{encabezado.get('num_entrega', '')}</b>", subtitulo_style))
        story.append(Paragraph(f"Fecha: {fecha_entrega}", subtitulo_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph("SE ENTREGAN LOS SIGUIENTES DOCUMENTOS", centrado_style))
        story.append(Spacer(1, 6))

        # definir un estilo para las celdas 
        celda_style = ParagraphStyle(
            name='Celda',
            fontSize=7,
            leading=8,
            alignment=1,
            fontName='Times-Roman'
        )

        # Detalle según tipo de entrega
        if encabezado["tipo_entrega"] == "Documento con Contraseña":
            data = [["Factura", "Proveedor", "Monto"]]
            for d in detalles:
                data.append([
                    Paragraph(str(d.get("num_factura", "")), centrado_style),
                    Paragraph(str(d.get("proveedor_nombre", "")), celda_style),
                    Paragraph(str(d.get("monto_con_moneda", "")), centrado_style )
                ])
            col_widths = [20*mm, 25*mm, 20*mm]
        else:
            data = [["Documento", "Proveedor", "Nombre Solicitud", "Monto"]]
            for d in detalles:
                data.append([
                    d.get("numero_documento", ""),
                    Paragraph(str(d.get("proveedor_nombre", "")), celda_style),
                    d.get("nombre_solicitud", ""),
                    d.get("monto_con_moneda", "")
                ])
            col_widths = [15*mm, 20*mm, 23*mm, 18*mm]

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.black),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),     # Centrar horizontal
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),    # Centrar vertical
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,0), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),       # Opcional: ajustar padding
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(table)
        story.append(Spacer(1, 8))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Usuario Entrega:</b> {nombre_emisor}", centrado_style))
        story.append(Spacer(1, 25))
        story.append(Paragraph("____________________________________", centrado_style))
        story.append(Paragraph("<b>Usuario Recibe</b>", centrado_style))

        
        # Tamaño exacto de ticket: 68.75 x 105.1 mm
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(80*mm, 110*mm),
            rightMargin=2, leftMargin=2, topMargin=2, bottomMargin=2
        )

        #  Construir PDF
        doc.build(story)
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="application/pdf",
                                 headers={"Content-Disposition": f"inline; filename=entrega_{cod_entrega}.pdf"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# end point para las entregas pendientes 
@router.get("/pendientes/{cod_usuario}", response_model=List[EntregaPendiente])
def listar_entregas_pendientes(
    cod_usuario: int,
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None)
):
    return obtener_entregas_pendientes(cod_usuario, fecha_inicio, fecha_fin)

# end point para mostrar las entregas completas en recepcion
@router.get("/recepcion/{cod_entrega}/{cod_empresa}")
def ver_recepcion_completa(cod_entrega: int, cod_empresa: int):
    return obtener_recepcion_completa(cod_entrega, cod_empresa)

# endpoint para el botón de guardar
@router.post("/guardar")
def guardar_detalles(req: GuardarRequest):
    return actualizar_estado_detalle(req.cod_entrega, req.cod_empresa, req.lineas)

# end point para el boton confirmar parcial
@router.post("/confirmar-parcial")
def confirmar_parcial(req: ConfirmarRequest):
    return confirmar_entrega_parcial(req.cod_entrega, req.cod_empresa, req.comentario)
