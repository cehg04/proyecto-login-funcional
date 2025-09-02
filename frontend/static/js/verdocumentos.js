$(document).ready(function () {
    cargarDocumentosVarios();

    // Validar permisos 
    if (validar_permisos(13) !== 'S') {
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

    if (validar_permisos(14) !== 'S') {
        $("#btnCrearDocumento").hide();
    }

    function cargarDocumentosVarios() {
        $.ajax({
            url: "/documentos/varios",
            method: "GET",
            success: function (data) {
                const tbody = $("#tablaDocumentos tbody");
                tbody.empty();
                data.forEach(function (doc) {

                 let badgeClass = '';
                if (doc.estado === 'Pendiente') badgeClass = 'bg-primary text-white';
                else if (doc.estado === 'Anulado') badgeClass = 'bg-danger text-white';
                else if (doc.estado === 'Recibido') badgeClass = 'bg-success text-white';
                else if (doc.estado === 'Entregado') badgeClass = 'bg-info text-white';
                else badgeClass = 'bg-secondary text-white'; 
                    tbody.append(`
                        <tr>
                        <td>${doc.empresa_nombre}</td>
                        <td>${doc.tipo_documento}</td>
                        <td>${doc.proveedor_nombre}</td>
                        <td>${doc.nombre_solicitud}</td>
                        <td>${doc.numero_documento}</td>
                        <td class="text-center">${doc.monto_con_moneda || ''}</td>
                        <td>${doc.observaciones || ''}</td>
                        <td><span class="badge ${badgeClass}">${doc.estado}</span></td>
                        <td>
                            <button class="btn btn-danger btn-sm btn-anular" data-cod="${doc.cod_documento}">Anular</button>
                        </td>
                        </tr>
                    `);
                });

                // Inicializar DataTable después de llenar la tabla
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
                        { orderable: false, targets: [] }
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

