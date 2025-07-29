$(document).ready(function () {
    const cod_empresa = 1; // Puedes cambiar esto según sesión

    $.ajax({
        url: `/contrasenias/?cod_empresa=${cod_empresa}`,
        method: "GET",
        success: function (data) {
            const tbody = $("#tablaContrasenias tbody");
            tbody.empty();

            data.forEach(item => {
                const row = `
                    <tr>
                        <td>${item.cod_contrasenia}</td>
                        <td>${item.num_contrasenia}</td>
                        <td>${item.cod_proveedor}</td>
                        <td>${item.fecha_contrasenia}</td>
                        <td>${item.estado}</td>
                        <td><button class="btn btn-primary btn-sm btn-detalle" data-detalles='${JSON.stringify(item.detalles)}'>Ver</button></td>
                    </tr>
                `;
                tbody.append(row);
            });

            $(".btn-detalle").on("click", function () {
                const detalles = $(this).data("detalles");
                const detalleBody = $("#tablaDetalleBody");
                detalleBody.empty();

                detalles.forEach(det => {
                    detalleBody.append(`
                        <tr>
                            <td>${det.num_factura}</td>
                            <td>${det.cod_moneda}</td>
                            <td>${det.monto}</td>
                            <td>${det.retension_iva || ''}</td>
                            <td>${det.retension_isr || ''}</td>
                            <td>${det.estado}</td>
                        </tr>
                    `);
                });

                $("#modalDetalle").modal("show");
            });
        },
        error: function () {
            alert("Error al cargar las contraseñas.");
        }
    });
});
