$(document).ready(function () {

    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    const codContrasenia = parseInt(getUrlParameter('cod_contrasenia'));
    const codEmpresa = parseInt(getUrlParameter('cod_empresa'));

    if (!codContrasenia || !codEmpresa) {
        alert('Parámetros faltantes: cod_contrasenia y cod_empresa');
        return;
    }

    function obtenerClaseBadgeEncabezado(estado) {
        switch ((estado || '').toLowerCase()) {
            case 'realizado':
                return 'bg-success text-white'; 
            case 'anulado':
                return 'bg-danger text-white'; 
            default:
                return 'bg-secondary text-white';
        }
    }

    function obtenerClaseBadgeDetalle(estado) {
        switch ((estado || '').toLowerCase()) {
            case 'entregado':
                return 'bg-info text-white'; 
            case 'recibido':
                return 'bg-success text-white'; 
            case 'pendiente':
                return 'bg-primary text-white'; 
            default:
                return 'bg-secondary text-white'; 
        }
    }

    $.ajax({
        url: '/contrasenias/ver-completa-filtrada',
        method: 'GET',
        data: {
            cod_contrasenia: codContrasenia,
            cod_empresa: codEmpresa
        },
        success: function (data) {
            mostrarEncabezado(data.encabezado);
            mostrarDetalles(data.detalles);
        },
        error: function (xhr) {
            alert('Error al cargar datos: ' + (xhr.responseJSON?.detail || xhr.statusText));
        }
    });

    function mostrarEncabezado(encabezado) {
        $('#numContrasenia').text(encabezado.num_contrasenia || '');
        $('#empresaNombre').text(encabezado.empresa_nombre || '');
        $('#proveedorNombre').text(encabezado.proveedor_nombre || '');

        const claseBadge = obtenerClaseBadgeEncabezado(encabezado.estado);
        $('#estadoContrasenia').html(`<span class="badge ${claseBadge}">${encabezado.estado || ''}</span>`);
    }

    function mostrarDetalles(detalles) {
        const tbody = $('#tablaDetalles tbody');
        tbody.empty();

        if (!detalles || detalles.length === 0) {
            tbody.append('<tr><td colspan="8" class="text-center">No hay detalles disponibles</td></tr>');
            return;
        }

        detalles.forEach(detalle => {
            const claseBadgeDetalle = obtenerClaseBadgeDetalle(detalle.estado);
            tbody.append(`
                <tr>
                    <td class="text-center">${detalle.num_factura || ''}</td>
                    <td class="text-center">${detalle.monto_con_moneda || ''}</td>
                    <td class="text-center">${detalle.retension_iva || ''}</td>
                    <td class="text-center">${detalle.retension_isr || ''}</td>
                    <td class="text-center">${detalle.numero_retension_iva || ''}</td>
                    <td class="text-center">${detalle.numero_retension_isr || ''}</td>
                    <td class="text-center">
                        <span class="badge ${claseBadgeDetalle}">${detalle.estado || ''}</span>
                    </td>
                </tr>
            `);
        });
    }
});




