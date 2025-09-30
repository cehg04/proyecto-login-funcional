$(document).ready(function () {
    cargarDocumentosVarios();

    if (validar_permisos(11) !== 'S') {
        Swal.fire({
            title: "Acceso denegado",
            text: "No tienes permiso para ver los Documentos",
            icon: "warning",
            confirmButtonText: "OK"
        }).then(() => {
            window.location.href = "inicio.html";
        });
        return;
    }

    if (validar_permisos(12) !== 'S') {
        $("#btnCrearDocumento").hide();
    }

    function cargarDocumentosVarios() {
        $.ajax({
            url: "/documentos/varios",
            method: "GET",
            success: function (data) {
                const tbody = $("#tablaDocumentos tbody");
                tbody.empty();
                    
                if (!data || data.length === 0) {
                    tbody.html('<tr><td colspan="10" class="text-center">No hay datos disponibles</td></tr>');
                    if ($.fn.DataTable.isDataTable('#tablaDocumentos')) {
                        $('#tablaDocumentos').DataTable().destroy();
                    }
                    return;
                }

                data.forEach(function (doc) {

                 let badgeClass = '';
                if (doc.estado === 'Pendiente') badgeClass = 'bg-primary text-white';
                else if (doc.estado === 'Anulado') badgeClass = 'bg-danger text-white';
                else if (doc.estado === 'Recibido') badgeClass = 'bg-success text-white';
                else if (doc.estado === 'Entregado') badgeClass = 'bg-info text-white';
                else badgeClass = 'bg-secondary text-white'; 
                    tbody.append(`
                        <tr>
                        <td>${doc.cod_documento}</td>
                        <td>${doc.fecha_creacion || "N/A"}</td>
                        <td>${doc.tipo_documento}</td>
                        <td>${doc.proveedor_nombre || "N/A"}</td>
                        <td>${doc.nombre_solicitud || "N/A"}</td>
                        <td>${doc.numero_documento}</td>
                        <td>${doc.monto_con_moneda || ''}</td>
                        <td><span class="badge ${badgeClass}">${doc.estado}</span></td>
                        <td>
                            <button class="btn btn-danger btn-sm btn-anular" data-cod="${doc.cod_documento}">Anular</button>
                        </td>
                        <td title="${doc.observaciones || ''}">${doc.observaciones || "N/A"}</td>
                        <td>${doc.numero_retension_iva || "N/A"}</td>
                        <td>${doc.numero_retension_isr || "N/A"}</td>
                        </tr>
                    `);
                });

                if ($.fn.DataTable.isDataTable('#tablaDocumentos')) {
                    $('#tablaDocumentos').DataTable().destroy(); 
                }

                let table = $('#tablaDocumentos').DataTable({
                    responsive: true,
                    language: {
                        url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
                    },
                    pageLength: 10,
                    lengthMenu: [5, 10, 25, 50],
                    columnDefs: [
                        { orderable: false, targets: [10] },
                        { className: "text-center", targets: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] },
                        { className: "truncate", targets: 7 }
                    ]
                });
                    table.on('draw', function () {
                    if (validar_permisos(15) !== 'S') {
                        $(".btn-anular").remove();
                    }
                });
            },
            error: function () {
                $("#tablaDocumentos tbody").html('<tr><td colspan="9" class="text-center text-danger">No se pudieron cargar los documentos.</td></tr>');
            }
        });
    }

    // Validar si el usuario tiene permiso 15 al dibujar la tabla
$('#tablaDocumentos').on('draw.dt', function () {
    if (validar_permisos(13) !== 'S') {
        $(".btn-anular").remove();
    }
});

$('#tablaDocumentos').on('click', '.btn-anular', function () {
    const codDocumento = $(this).data('cod');
    const codDocNum = parseInt(codDocumento, 10);

    if (isNaN(codDocNum)) {
    Swal.fire("Error", "El código del documento no es válido.", "error");
    return;
    }

    console.log("Código del documento a anular:", codDocNum);

    Swal.fire({
        title: '¿Estás seguro?',
        text: '¿Deseas anular este documento?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, anular',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/documentos/anular",
                method: "PUT",
                contentType: "application/json",
                processData: false,
                data: JSON.stringify({ cod_documento: codDocNum }),
                success: function (resp) {
                    Swal.fire("Éxito", resp.message || resp.mensaje || "Documento anulado", "success")
                        .then(() => location.reload());
                },
                error: function (xhr) {
                    let msg = "Ocurrió un error al anular el documento.";
                    if (xhr.responseJSON && xhr.responseJSON.detail) {
                        msg = xhr.responseJSON.detail;
                    }
                    Swal.fire("Error", msg, "error");
                }
            });
        }
    });
});

});
