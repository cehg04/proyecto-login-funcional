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
    cargarUsuariosEntrega(token);
    renderTablaDetalles([]);

    $("#cod_empresa").on("change", function () {
        const codEmpresa = $(this).val();

        // Reiniciar globales al cambiar empresa
        codEntregaGlobal = null;
        codEmpresaGlobal = null;

        if (!codEmpresa) {
            renderTablaDetalles([]);
            return;
        }

        codEmpresaGlobal = parseInt(codEmpresa);
        cargarDetallesPendientes(codEmpresaGlobal);
    });

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
                url: "/entregas/crear-contrasenia",
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

// Función para renderizar tabla de detalles
function renderTablaDetalles(detalles) {
    const $tbody = $("#tablaDetalles tbody");
    $tbody.empty();

    if (!detalles || detalles.length === 0) {
        $tbody.html('<tr><td colspan="9" class="text-center">No hay detalles disponibles</td></tr>');
        return;
    }

    detalles.forEach((d, index) => {
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
                <td>${d.retension_iva === 'S' ? 'Si Tiene' : (d.retension_iva === 'N' ? 'No Tiene' : '')}</td>
                <td>${d.retension_isr === 'S' ? 'Si Tiene' : (d.retension_isr === 'N' ? 'No Tiene' : '')}</td>
                <td>${d.numero_retension_iva || ''}</td>
                <td>${d.numero_retension_isr || ''}</td>
                <td>${d.estado || ''}</td>
            </tr>
        `);
    });
}

// Cargar empresas en el select
function cargarEmpresas() {
    $.get("/contrasenias/empresas", function (data) {
        const $empresa = $("#cod_empresa");
        $empresa.empty().append('<option value="">Seleccione Empresa</option>');
        data.forEach(emp => {
            $empresa.append(`<option value="${emp.cod_empresa}">${emp.nombre}</option>`);
        });
    });
}

// Cargar usuarios en el select
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
        error: function () {
            Swal.fire("Error", "Error al cargar usuarios", "error");
        }
    });
}

// Cargar detalles pendientes de la empresa seleccionada
function cargarDetallesPendientes(codEmpresa) {
    $.ajax({
        url: "/contrasenias/detalles-pendientes",
        method: "GET",
        data: { cod_empresa: codEmpresa },
        dataType: "json",
        success: function (response) {
            if (response.success) {
                detallesPendientes = response.data;
                renderTablaDetalles(detallesPendientes);
            } else {
                Swal.fire("Error", "No se pudieron cargar los detalles.", "error");
                renderTablaDetalles([]);
            }
        },
        error: function () {
            Swal.fire("Error", "Error al obtener los detalles pendientes.", "error");
            renderTablaDetalles([]);
        }
    });
}

// Obtener detalles seleccionados
function obtenerSeleccionados() {
    let seleccionados = [];
    $("#tablaDetalles tbody .check-detalle:checked").each(function () {
        const index = $(this).data("index");
        seleccionados.push(detallesPendientes[index]);
    });
    return seleccionados;
}

// Enviar detalles a la entrega
function enviarDetalles(seleccionados, token) {
    if (seleccionados.length === 0) return;

    const payload = seleccionados.map(s => ({
        cod_contrasenia: s.cod_contrasenia,
        cod_empresa_contrasenia: s.cod_empresa,
        linea_contrasenia: s.linea ?? s.linea_contrasenia ?? 0,
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

$.ajax({
    url: "/entregas/detalles-contrasenia",
    method: "POST",
    contentType: "application/json",
    headers: { "Authorization": "Bearer " + token },
    data: JSON.stringify(payload),
    success: function (resp) {
        Swal.fire({
            title: "Éxito",
            text: resp.mensaje || "Detalles asignados correctamente",
            icon: "success"
        }).then(() => {
            // Abrir PDF en otra pestaña
            if (codEntregaGlobal && codEmpresaGlobal) {
                window.open(`/entregas/imprimir-entrega/${codEntregaGlobal}/${codEmpresaGlobal}`, '_blank');
            }

            // Reiniciar variables y limpiar tabla para nueva entrega
            codEntregaGlobal = null;
            codEmpresaGlobal = null;
            detallesPendientes = [];
            $("#tablaDetalles tbody").empty();
            $("#cod_empresa").val(""); 
            $("#fecha_entrega").val(""); 
            $("#cod_usuario_entrega").val("");
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





