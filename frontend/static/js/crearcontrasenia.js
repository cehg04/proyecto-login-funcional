$(document).ready(function () {
    let detalles = [];
    let contadorLinea = 0;

    cargarEmpresas();
 

    $("#cod_empresa").on("change", function () {
        const cod_empresa = $(this).val();
        if (cod_empresa) {
            cargarProveedores(cod_empresa);
        }
    });

    // Habilitar o deshabilitar inputs de retención según checkbox
    $("#retension_isr").on("change", function () {
        $("#numero_retension_isr").prop("disabled", !this.checked).val("");
    });

    $("#retension_iva").on("change", function () {
        $("#numero_retension_iva").prop("disabled", !this.checked).val("");
    });

    cargarMonedas();

    $("#agregarDetalle").click(function () {
        const cod_moneda = $("#cod_moneda").val();
        const monto = parseFloat($("#monto").val());
        const retension_iva = $("#retension_iva").is(":checked");
        const retension_isr = $("#retension_isr").is(":checked");
        const numero_retension_iva = retension_iva ? $("#numero_retension_iva").val() : null;
        const numero_retension_isr = retension_isr ? $("#numero_retension_isr").val() : null;

        if (!cod_moneda || isNaN(monto)) {
            alert("Completa todos los campos obligatorios del detalle.");
            return;
        }

        const nuevoDetalle = {
            linea: contadorLinea++,
            cod_moneda,
            monto,
            retension_iva,
            retension_isr,
            numero_retension_iva,
            numero_retension_isr,
            estado: "P"
        };

        detalles.push(nuevoDetalle);
        mostrarDetalles();
        limpiarFormularioDetalle();
    });

    $("#guardarContrasenia").click(function () {
        const data = {
            fecha_contrasenia: $("#fecha_contrasenia").val(),
            cod_empresa: $("#cod_empresa").val(),
            cod_proveedor: $("#cod_proveedor").val(),
            detalles
        };

        if (!data.cod_empresa || !data.cod_proveedor || !data.fecha_contrasenia) {
            alert("Completa todos los campos del encabezado.");
            return;
        }

        if (detalles.length === 0) {
            alert("Agrega al menos un detalle.");
            return;
        }

        $.ajax({
            url: "/contrasenias/crear",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (response) {
                alert("Contraseña creada correctamente.");
                location.reload();
            },
            error: function (xhr) {
                alert("Error al guardar: " + xhr.responseText);
            }
        });
    });

    function mostrarDetalles() {
        const cuerpoTabla = $("#tablaDetalles tbody");
        cuerpoTabla.empty();

        detalles.forEach((item, index) => {
            cuerpoTabla.append(`
                <tr>
                    <td>${item.cod_moneda}</td>
                    <td>${item.monto.toFixed(2)}</td>
                    <td>${item.retension_isr ? 'Sí' : 'No'}</td>
                    <td>${item.retension_iva ? 'Sí' : 'No'}</td>
                    <td>
                        ISR: ${item.numero_retension_isr || '-'}<br>
                        IVA: ${item.numero_retension_iva || '-'}
                    </td>
                    <td>${item.estado}</td>
                    <td><button class="btn btn-danger btn-sm" onclick="eliminarDetalle(${index})">Eliminar</button></td>
                </tr>
            `);
        });
    }

    window.eliminarDetalle = function (index) {
        detalles.splice(index, 1);
        mostrarDetalles();
    };

    function limpiarFormularioDetalle() {
        $("#cod_moneda").val("");
        $("#monto").val("");
        $("#retension_iva").prop("checked", false);
        $("#retension_isr").prop("checked", false);
        $("#numero_retension_iva").val("").prop("disabled", true);
        $("#numero_retension_isr").val("").prop("disabled", true);
    }

        function cargarMonedas() {
            $.get("/contrasenias/monedas", function (data) {
                $("#cod_moneda").empty().append('<option value="">Seleccione</option>');
                data.forEach(mon => {
                    $("#cod_moneda").append(`<option value="${mon.cod_moneda}">${mon.abreviatura}</option>`);
                });
            });
        }


    function cargarEmpresas() {
        $.get("/contrasenias/empresas", function (data) {
            $("#cod_empresa").empty().append('<option value="">Seleccione Empresa</option>');
            data.forEach(emp => {
                $("#cod_empresa").append(`<option value="${emp.cod_empresa}">${emp.nombre}</option>`);
            });
        });
    }

    function cargarProveedores(cod_empresa) {
        $("#proveedor_nombre").val("");
        $("#cod_proveedor").val("");
    }

    // Autocompletado para proveedor
    $("#proveedor_nombre").autocomplete({
        source: function (request, response) {
            const cod_empresa = $("#cod_empresa").val();
            if (!cod_empresa) {
                response([]);
                return;
            }

            $.ajax({
                url: `/contrasenias/proveedores-autocomplete`,
                dataType: "json",
                data: {
                    q: request.term,
                    cod_empresa: cod_empresa
                },
                success: function (data) {
                    response(data.map(prov => ({
                        label: `${prov.nit} - ${prov.cod_proveedor} - ${prov.nombre}`,
                        value: prov.nombre,
                        cod_proveedor: prov.cod_proveedor
                    })));
                }
            });
        },
        minLength: 2,
        select: function (event, ui) {
            $("#cod_proveedor").val(ui.item.cod_proveedor);
        },
        focus: function (event, ui) {
            $("#proveedor_nombre").val(ui.item.label);
            return false;
        }
    });
});







