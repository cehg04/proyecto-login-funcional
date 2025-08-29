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

    // Petición AJAX al endpoint
    $.ajax({
        url: `/entregas/detalle/${codEntrega}/${codEmpresa}`,
        method: 'GET',
        success: function (data) {
            mostrarEncabezado(data.encabezado);
            mostrarDetalles(data.detalles);
        },
        error: function (xhr) {
            alert('Error al cargar datos: ' + (xhr.responseJSON?.detail || xhr.statusText));
        }
    });

    // Mostrar encabezado en HTML
    function mostrarEncabezado(encabezado) {
        $('#numEntrega').text(encabezado.num_entrega || '');
        $('#tipoEntrega').text(encabezado.tipo_entrega || '');
        $('#estadoEntrega').text(encabezado.estado || '');
    }

    // Mostrar detalles en tabla
    function mostrarDetalles(detalles) {
        const tbody = $('#tablaDetalles tbody');
        tbody.empty();

        if (!detalles || detalles.length === 0) {
            tbody.append('<tr><td colspan="9" class="text-center">No hay detalles disponibles</td></tr>');
            return;
        }

        detalles.forEach(detalle => {
            tbody.append(`
                <tr>
                    <td>${detalle.num_factura || ''}</td>
                    <td>${detalle.cod_moneda || ''}</td>
                    <td>${detalle.monto ? parseFloat(detalle.monto).toFixed(2) : ''}</td>
                    <td>${detalle.retension_iva || ''}</td>
                    <td>${detalle.retension_isr || ''}</td>
                    <td>${detalle.numero_retension_iva || ''}</td>
                    <td>${detalle.numero_retension_isr || ''}</td>
                    <td>${detalle.estado || ''}</td>
                </tr>
            `);
        });
    }
});
