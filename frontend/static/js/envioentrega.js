let detallesPendientes = []; // guardamos todos los detalles en memoria
let codEntregaGlobal = null;
let codEmpresaGlobal = null;

$(document).ready(function () {
    cargarEmpresas();
    cargarDetallesPendientes();

    // Un solo botón para crear encabezado + asignar detalles
    $("#btnAsignarDetalles").on("click", function () {
        const seleccionados = obtenerSeleccionados();

        if (seleccionados.length === 0) {
            Swal.fire("Aviso", "Debes seleccionar al menos un detalle", "warning");
            return;
        }

        const token = localStorage.getItem("token");
        if (!token) {
            Swal.fire("Error", "No hay token, inicia sesión nuevamente", "error");
            return;
        }

        // Paso 1: crear encabezado si no existe
        if (!codEntregaGlobal) {
            const dataEncabezado = {
                cod_empresa: $("#cod_empresa").val(),
                fecha_entrega: $("#fecha_entrega").val()
            };

            if (!dataEncabezado.cod_empresa || !dataEncabezado.fecha_entrega) {
                Swal.fire("Error", "Debes completar todos los campos del encabezado", "warning");
                return;
            }

            $.ajax({
                url: "/entregas/crear",
                method: "POST",
                contentType: "application/json",
                headers: { "Authorization": "Bearer " + token },
                data: JSON.stringify(dataEncabezado),
                success: function (resp) {
                    codEntregaGlobal = resp.cod_entrega;
                    codEmpresaGlobal = resp.cod_empresa;
                    console.log("Encabezado creado:", resp);

                    // Paso 2: enviar detalles ya seleccionados
                    enviarDetalles(seleccionados, token);
                },
                error: function (xhr) {
                    let errorMsg = "Error al crear entrega";
                    if (xhr.responseJSON && xhr.responseJSON.detail) {
                        errorMsg = xhr.responseJSON.detail;
                    }
                    Swal.fire("Error", errorMsg, "error");
                }
            });
        } else {
            // Si ya existe el encabezado, solo mandamos los detalles
            enviarDetalles(seleccionados, token);
        }
    });
});

function cargarEmpresas() {
    $.get("/contrasenias/empresas", function (data) {
        const $empresa = $("#cod_empresa");
        $empresa.empty().append('<option value="">Seleccione Empresa</option>');
        data.forEach(emp => {
            $empresa.append(`<option value="${emp.cod_empresa}">${emp.nombre}</option>`);
        });
    });
}

function cargarDetallesPendientes() {
    $.ajax({
        url: "/contrasenias/detalles-pendientes",
        method: "GET",
        dataType: "json",
        success: function (response) {
            if (response.success) {
                detallesPendientes = response.data;
                const $tbody = $("#tablaDetalles tbody");
                $tbody.empty();

                detallesPendientes.forEach((d, index) => {
                    $tbody.append(`
                        <tr>
                            <td>
                                <input type="checkbox" 
                                    class="check-detalle" 
                                    data-index="${index}" 
                                    data-cod-contrasenia="${d.cod_contrasenia}">
                            </td>
                            <td>${d.num_factura || ''}</td>
                            <td>${d.cod_moneda || ''}</td>
                            <td>${d.monto || ''}</td>
                            <td>${d.retension_iva || ''}</td>
                            <td>${d.retension_isr || ''}</td>
                            <td>${d.numero_retension_iva || ''}</td>
                            <td>${d.numero_retension_isr || ''}</td>
                            <td>${d.estado || ''}</td>
                        </tr>
                    `);
                });
                console.log("Total registros:", response.total);
            } else {
                Swal.fire("Error", "No se pudieron cargar los detalles.", "error");
            }
        },
        error: function (xhr, status, error) {
            console.error("Error AJAX:", error);
            Swal.fire("Error", "Error al obtener los detalles pendientes.", "error");
        }
    });
}

function obtenerSeleccionados() {
    let seleccionados = [];
    $("#tablaDetalles tbody .check-detalle:checked").each(function () {
        const index = $(this).data("index");
        seleccionados.push(detallesPendientes[index]);
    });
    return seleccionados;
}

function enviarDetalles(seleccionados, token) {
    if (seleccionados.length === 0) return;

    // Payload para insertar en detalle_entregas
    const payload = seleccionados.map(s => ({
        cod_contrasenia: s.cod_contrasenia,
        cod_empresa_contrasenia: s.cod_empresa,
        linea_contrasenia: s.linea,
        num_factura: s.num_factura,
        cod_moneda: s.cod_moneda,   
        monto: s.monto,
        retension_iva: s.retension_iva,
        retension_isr: s.retension_isr,
        numero_retension_iva: s.numero_retension_iva,
        numero_retension_isr: s.numero_retension_isr,
        estado: s.estado ? s.estado.charAt(0) : 'P',
        cod_entrega: codEntregaGlobal,
        cod_empresa: codEmpresaGlobal
    }));

    console.log("Payload a enviar:", payload);

    $.ajax({
        url: "/entregas/detalles",
        method: "POST",
        contentType: "application/json",
        headers: { "Authorization": "Bearer " + token },
        data: JSON.stringify(payload),
        success: function (resp) {
            Swal.fire("Éxito", resp.mensaje || "Detalles asignados correctamente", "success");

            // 🚀 Paso extra: marcar como entregados en detalle_contrasenias
            const payloadEstado = {
                detalles: seleccionados.map(s => ({
                    cod_contrasenia: s.cod_contrasenia,
                    cod_empresa: s.cod_empresa
                }))
            };

            $.ajax({
                url: "/contrasenias/entregar",
                method: "PUT",
                contentType: "application/json",
                headers: { "Authorization": "Bearer " + token },
                data: JSON.stringify(payloadEstado),
                success: function (resp2) {
                    console.log("Estados actualizados:", resp2);
                    cargarDetallesPendientes(); // refresca tabla
                },
                error: function (xhr) {
                    console.error("Error al actualizar estados:", xhr.responseJSON?.detail || xhr.statusText);
                    Swal.fire("Error", "Los detalles se insertaron, pero no se pudo actualizar el estado.", "warning");
                }
            });
        },
        error: function (xhr) {
            let errorMsg = "Error al asignar detalles";
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                errorMsg = xhr.responseJSON.detail;
            }
            Swal.fire("Error", errorMsg, "error");
        }
    });
}



