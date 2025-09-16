$(document).ready(function () {
    const urlParams = new URLSearchParams(window.location.search);
    const codEntrega = parseInt(urlParams.get("cod_entrega"));
    const codEmpresa = parseInt(urlParams.get("cod_empresa"));

    if (!codEntrega || !codEmpresa) {
        Swal.fire("Error", "Parámetros faltantes: cod_entrega y cod_empresa", "error");
        return;
    }

    function obtenerClaseBadgeEncabezado(estado) {
        switch ((estado || "").toLowerCase()) {
            case "pendiente": return "bg-warning text-dark";
            case "recibido": return "bg-success text-white";
            case "anulado": return "bg-danger text-white";
            default: return "bg-secondary text-white";
        }
    }

    function obtenerClaseBadgeDetalle(estado) {
        switch ((estado || "").toLowerCase()) {
            case "pendiente": return "bg-warning text-dark";
            case "confirmado": return "bg-success text-white";
            case "no confirmado": return "bg-danger text-white";
            default: return "bg-secondary text-white";
        }
    }

    function cargarRecepcion() {
        $.ajax({
            url: `/entregas/recepcion/${codEntrega}/${codEmpresa}`,
            method: "GET",
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
    }

    function mostrarEncabezado(encabezado) {
        $("#empresa_nombre").text(encabezado.empresa_nombre || "");
        $("#num_entrega").text(encabezado.num_entrega || "");
        $("#tipo_entrega").text(encabezado.tipo_entrega || "");
        $("#usuario_entrega").text(encabezado.nombre_usuario_entrega || "N/A");

        const claseBadge = obtenerClaseBadgeEncabezado(encabezado.estado);
        $("#estado").html(`<span class="badge ${claseBadge}">${encabezado.estado || ""}</span>`);
    }

    function mostrarDetalles(encabezado, detalles) {
        let hayPendientes = false;
        let hayConfirmados = false;

        if (encabezado.tipo_entrega === "Documento con Contraseña") {
            $("#tablaDCContainer").show();
            $("#tablaDSContainer").hide();
            const tbody = $("#tablaDC tbody").empty();

            if (!detalles || detalles.length === 0) {
                tbody.append(`<tr><td colspan="9" class="text-center">No hay detalles</td></tr>`);
            } else {
                detalles.forEach((d) => {
                    const estadoNorm = (d.estado || "").trim().toLowerCase();
                    if (estadoNorm === "pendiente") hayPendientes = true;
                    if (estadoNorm === "confirmado") hayConfirmados = true;

                    const claseBadge = obtenerClaseBadgeDetalle(d.estado);
                    const isConfirmed = estadoNorm === "confirmado";

                    tbody.append(`
                        <tr>
                            <td><input type="checkbox" class="detalle-check" data-linea="${d.linea}" ${isConfirmed ? "disabled checked" : ""}></td>
                            <td>${d.num_factura || "N/A"}</td>
                            <td>${d.proveedor_nombre || "N/A"}</td>
                            <td>${d.monto_con_moneda || "0.00"}</td>
                            <td>${d.retension_iva || "N/A"}</td>
                            <td>${d.retension_isr || "N/A"}</td>
                            <td>${d.numero_retension_iva || "N/A"}</td>
                            <td>${d.numero_retension_isr || "N/A"}</td>
                            <td><span class="badge ${claseBadge}">${d.estado || "Sin estado"}</span></td>
                        </tr>
                    `);
                });
            }

            $("#btnGuardarDC").off("click").on("click", function () { guardarLineas(); });
            $("#btnRecibirDC").off("click").on("click", function () { abrirModalParcial(); });

            if (hayPendientes && hayConfirmados) $("#btnRecibirDC").show();
            else $("#btnRecibirDC").hide();

        } else {
            $("#tablaDCContainer").hide();
            $("#tablaDSContainer").show();
            const tbody = $("#tablaDS tbody").empty();

            if (!detalles || detalles.length === 0) {
                tbody.append(`<tr><td colspan="10" class="text-center">No hay detalles</td></tr>`);
            } else {
                detalles.forEach((d) => {
                    const estadoNorm = (d.estado || "").trim().toLowerCase();
                    if (estadoNorm === "pendiente") hayPendientes = true;
                    if (estadoNorm === "confirmado") hayConfirmados = true;

                    const claseBadge = obtenerClaseBadgeDetalle(d.estado);
                    const isConfirmed = estadoNorm === "confirmado";

                    tbody.append(`
                        <tr>
                            <td><input type="checkbox" class="detalle-check" data-linea="${d.linea}" ${isConfirmed ? "disabled checked" : ""}></td>
                            <td>${d.tipo_documento || "N/A"}</td>
                            <td>${d.proveedor_nombre || "N/A"}</td>
                            <td>${d.nombre_solicitud || "N/A"}</td>
                            <td>${d.numero_documento || "N/A"}</td>
                            <td>${d.monto_con_moneda || "0.00"}</td>
                            <td>${d.numero_retension_iva || "N/A"}</td>
                            <td>${d.numero_retension_isr || "N/A"}</td>
                            <td title="${d.observaciones || "Sin observaciones"}">
                                ${d.observaciones && d.observaciones.length > 20 ? d.observaciones.substring(0,20)+"..." : (d.observaciones || "Sin observaciones")}
                            </td>
                            <td><span class="badge ${claseBadge}">${d.estado || "Sin estado"}</span></td>
                        </tr>
                    `);
                });
            }

            $("#btnGuardarDS").off("click").on("click", function () { guardarLineas(); });
            $("#btnRecibirDS").off("click").on("click", function () { abrirModalParcial(); });

            if (hayPendientes && hayConfirmados) $("#btnRecibirDS").show();
            else $("#btnRecibirDS").hide();
        }

        $('#selectAllDC').off('change').on('change', function() {
            $('#tablaDC tbody input.detalle-check:not(:disabled)').prop('checked', $(this).is(':checked'));
        });
        $('#selectAllDS').off('change').on('change', function() {
            $('#tablaDS tbody input.detalle-check:not(:disabled)').prop('checked', $(this).is(':checked'));
        });

        $(document).off('change', '#tablaDC tbody .detalle-check').on('change', '#tablaDC tbody .detalle-check', function() {
            const total = $("#tablaDC tbody .detalle-check:not(:disabled)").length;
            const marcados = $("#tablaDC tbody .detalle-check:checked").length;
            $("#selectAllDC").prop("checked", total > 0 && total === marcados);
        });
        $(document).off('change', '#tablaDS tbody .detalle-check').on('change', '#tablaDS tbody .detalle-check', function() {
            const total = $("#tablaDS tbody .detalle-check:not(:disabled)").length;
            const marcados = $("#tablaDS tbody .detalle-check:checked").length;
            $("#selectAllDS").prop("checked", total > 0 && total === marcados);
        });
    }

    function guardarLineas() {
        let lineas = $("input.detalle-check:checked").map(function () { return $(this).data("linea"); }).get();

        if (lineas.length === 0) {
            Swal.fire("Atención", "Debes seleccionar al menos un detalle", "warning");
            return;
        }

        $.ajax({
            url: "/entregas/guardar",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ cod_entrega: codEntrega, cod_empresa: codEmpresa, lineas: lineas }),
            success: function () {
                Swal.fire("Éxito", "Detalles guardados correctamente", "success").then(() => {
                    window.location.href = "/recepcionentrega.html";
                });
            },
            error: function (xhr) {
                Swal.fire("Error", "No se pudo guardar: " + (xhr.responseJSON?.detail || xhr.statusText), "error");
            }
        });
    }

    function abrirModalParcial() {
        let pendientesSeleccionados = $("input.detalle-check:not(:disabled):checked").length;
        if (pendientesSeleccionados > 0) {
            Swal.fire("Atención", "No se debe seleccionar ningún detalle pendiente para confirmar parcialmente.", "warning");
            return;
        }

        $("#comentarioParcial").val("");
        $("#modalConfirmarParcial").modal("show");
    }

    $("#btnGuardarComentarioParcial").off("click").on("click", function () {
        let comentario = $("#comentarioParcial").val().trim();
        if (!comentario) {
            Swal.fire("Atención", "El comentario es obligatorio para confirmar parcialmente.", "warning");
            return;
        }

        $.ajax({
            url: "/entregas/confirmar-parcial",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ cod_entrega: codEntrega, cod_empresa: codEmpresa, comentario: comentario }),
            success: function () {
                $("#modalConfirmarParcial").modal("hide");
                Swal.fire("Éxito", "Entrega parcial confirmada con éxito", "success").then(() => {
                    window.location.href = "/recepcionentrega.html";
                });
            },
            error: function (xhr) {
                Swal.fire("Error", "No se pudo confirmar parcialmente: " + (xhr.responseJSON?.detail || xhr.statusText), "error");
            }
        });
    });

    cargarRecepcion();
});




