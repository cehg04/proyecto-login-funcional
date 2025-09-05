$(document).ready(function () {
    // Función para obtener parámetros desde URL
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    const codEntrega = parseInt(getUrlParameter('cod_entrega'));
    const codEmpresa = parseInt(getUrlParameter('cod_empresa'));

    if (!codEntrega || !codEmpresa) {
        alert('Parámetros faltantes: cod_entrega y cod_empresa');
        return;
    }

    // 🔹 Colores para ENCABEZADO
    function obtenerClaseBadgeEncabezado(estado) {
        switch ((estado || '').toLowerCase()) {
            case 'pendiente':
                return 'bg-warning text-dark'; // Amarillo
            case 'recibido':
                return 'bg-success text-white'; // Verde
            case 'anulado':
                return 'bg-danger text-white'; // Rojo
            default:
                return 'bg-secondary text-white'; // Gris por defecto
        }
    }

    // 🔹 Colores para DETALLE
    function obtenerClaseBadgeDetalle(estado) {
        switch ((estado || '').toLowerCase()) {
            case 'pendiente':
                return 'bg-warning text-dark'; // Amarillo
            case 'confirmado':
                return 'bg-success text-white'; // Verde
            default:
                return 'bg-secondary text-white'; // Gris
        }
    }

    // Petición AJAX al endpoint
    $.ajax({
        url: `/entregas/detalle/${codEntrega}/${codEmpresa}`,
        method: 'GET',
        success: function (data) {
            if (!data || !data.encabezado) {
                Swal.fire("Error", "No se pudo cargar la entrega", "error");
                return;
            }
            mostrarEncabezado(data.encabezado);
            mostrarDetalles(data.encabezado, data.detalles);
        },
        error: function (xhr) {
            Swal.fire("Error", "No se pudo cargar la entrega: " + (xhr.responseJSON?.detail || xhr.statusText), "error");
        }
    });

    // Mostrar encabezado en HTML
    function mostrarEncabezado(encabezado) {
        $('#numEntrega').text(encabezado.num_entrega || '');
        $('#tipoEntrega').text(encabezado.tipo_entrega || '');
        $('#nombreUsuarioEntrega').text(encabezado.nombre_usuario_entrega || '');

        const claseBadge = obtenerClaseBadgeEncabezado(encabezado.estado);
        $('#estadoEntrega').html(`<span class="badge ${claseBadge}">${encabezado.estado || ''}</span>`);
    }

    // Mostrar detalles en tabla según tipo de entrega
    function mostrarDetalles(encabezado, detalles) {
        if (encabezado.tipo_entrega === "Documento con Contraseña") {
            $("#tablaDCContainer").show();
            $("#tablaDSContainer").hide();

            const tbody = $("#tablaDC tbody");
            tbody.empty();
            detalles.forEach(d => {
                const claseBadgeDetalle = obtenerClaseBadgeDetalle(d.estado);
                tbody.append(`
                    <tr>
                        <td>${d.num_factura || "N/A"}</td>
                        <td>${d.monto_con_moneda || 'N/A'}</td>
                        <td>${d.retension_iva || "N/A"}</td>
                        <td>${d.retension_isr || "N/A"}</td>
                        <td>${d.numero_retension_iva || "N/A"}</td>
                        <td>${d.numero_retension_isr || "N/A"}</td>
                        <td><span class="badge ${claseBadgeDetalle}">${d.estado || "Desconocido"}</span></td>
                    </tr>
                `);
            });

        } else if (encabezado.tipo_entrega === "Documento sin Contraseña") {
            $("#tablaDCContainer").hide();
            $("#tablaDSContainer").show();

            const tbody = $("#tablaDS tbody");
            tbody.empty();
            detalles.forEach(d => {
                const claseBadgeDetalle = obtenerClaseBadgeDetalle(d.estado);
                tbody.append(`
                    <tr>
                        <td>${d.tipo_documento || 'N/A'}</td>
                        <td>${d.proveedor_nombre || 'N/A'}</td>
                        <td>${d.nombre_solicitud || 'N/A'}</td>
                        <td>${d.numero_documento || 'N/A'}</td>
                        <td>${d.monto_con_moneda || 'N/A'}</td>
                        <td>${d.numero_retension_iva || 'N/A'}</td>
                        <td>${d.numero_retension_isr || 'N/A'}</td>
                        <td title="${d.observaciones ? d.observaciones : 'Sin observaciones'}">
                            ${d.observaciones && d.observaciones.length > 20 
                                ? d.observaciones.substring(0, 20) + '...' 
                                : (d.observaciones || 'Sin observaciones')}
                        </td>
                        <td><span class="badge ${claseBadgeDetalle}">${d.estado || 'Sin estado'}</span></td>
                    </tr>
                `);
            });
        }
    }
});



