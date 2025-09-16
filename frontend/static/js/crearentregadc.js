let detallesPendientes = []; 
let codEntregaGlobal = null;
let codEmpresaGlobal = null;

$(document).ready(function () {
            const token = localStorage.getItem("token");
        if (!token) {
            Swal.fire("Error", "No hay token, inicia sesión nuevamente", "error");
            return;
        }

        if (validar_permisos(8) !== 'S') {
        Swal.fire({
        title: "Acceso denegado",
        text: "No tienes permiso para Crear Entregas",
        icon: "warning",
        confirmButtonText: "OK"
        }).then(() => {
        window.location.href = "inicio.html";
        });
        return;
  }

    cargarEmpresas();
    cargarDocumentosPendientes();
    cargarUsuariosEntrega();

    $("#btnAsignarDetalles").on("click", function () {
        const seleccionados = obtenerSeleccionados();

        if (seleccionados.length === 0) {
            Swal.fire("Aviso", "Debes seleccionar al menos un detalle", "warning");
            return;
        }

        if (!codEntregaGlobal) {
            const dataEncabezado = {
                cod_empresa: $("#cod_empresa").val(),
                fecha_entrega: $("#fecha_entrega").val(),
                cod_usuario_entrega: $("#cod_usuario_entrega").val()
            };

            if (!dataEncabezado.cod_empresa || !dataEncabezado.fecha_entrega || !dataEncabezado.cod_usuario_entrega) {
                Swal.fire("Error", "Debes completar todos los campos del encabezado", "warning");
                return;
            }

            $.ajax({
                url: "/entregas/crear-documento",
                method: "POST",
                contentType: "application/json",
                headers: { "Authorization": "Bearer " + token },
                data: JSON.stringify(dataEncabezado),
                success: function (resp) {
                    codEntregaGlobal = resp.cod_entrega;
                    codEmpresaGlobal = resp.cod_empresa;
                    console.log("Encabezado creado:", resp);

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

function cargarUsuariosEntrega(token){
    $.ajax({
        url: "/entregas/usuarios",
        method: "GET",
        headers: { "Authorization": "Bearer " + token },
        success: function (usuarios) {
            const $select = $("#cod_usuario_entrega");
            $select.empty().append('<option value="">Seleccione Usuario</option>');
            usuarios.forEach(u => {
                $select.append(`<option value="${u.cod_usuario}">${u.nombre}</option>`);
            });
        },
        error: function (xhr) {
            Swal.fire("Error", "Error al cargar usuarios", "error");
        }
    });
}

function cargarDocumentosPendientes() {
    $.ajax({
        url: "/documentos/pendientes",
        method: "GET",
        dataType: "json",
        success: function (response) {
            if (response.success) {
                detallesPendientes = response.data;
                const $tbody = $("#tablaDetalles tbody");
                $tbody.empty();

                detallesPendientes.forEach((dv, index) => {
                    $tbody.append(`
                        <tr>
                            <td>
                                <input type="checkbox" 
                                    class="check-detalle" 
                                    data-index="${index}" 
                                    data-cod-documento="${dv.cod_documento}">
                            </td>
                            <td>${dv.empresa_nombre || ''}</td>
                            <td>${dv.cod_moneda || ''}</td>
                            <td>${dv.monto || ''}</td>
                            <td>${dv.estado || ''}</td>
                        </tr>
                    `);
                });
                console.log("Total registros:", response.total);
            } else {
                Swal.fire("Error", "No se pudieron cargar los documentos.", "error");
            }
        },
        error: function (xhr, status, error) {
            console.error("Error AJAX:", error);
            Swal.fire("Error", "Error al obtener los documentos pendientes.", "error");
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

    const payload = seleccionados.map(s => ({
        cod_entrega: codEntregaGlobal,
        cod_empresa: codEmpresaGlobal,
        cod_moneda: s.cod_moneda,
        monto: s.monto,
        estado: s.estado ? s.estado.charAt(0) : 'P',
        cod_documento: s.cod_documento
    }));


    console.log("Payload a enviar a /entregas/detalles-documentos:", payload);

    $.ajax({
        url: "/entregas/detalles-documentos",
        method: "POST",
        contentType: "application/json",
        headers: { "Authorization": "Bearer " + token },
        data: JSON.stringify(payload),
        success: function (resp) {
            Swal.fire("Éxito", resp.mensaje || "Detalles asignados correctamente", "success");
            cargarDocumentosPendientes(); // refresca tabla
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