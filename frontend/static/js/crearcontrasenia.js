let codContraseniaActual = null;
let codEmpresaActual = null;

$(document).ready(function () {
    cargarEmpresas();

    // variables globales para el detalle
    

     // Intercepta el submit del formulario
    $("#formulario-contrasenia").on("submit", function (e) {
        e.preventDefault(); // 

        const data = {
            fecha_contrasenia: $("#fecha_contrasenia").val(),
            cod_empresa: $("#cod_empresa").val(),
            cod_proveedor: $("#cod_proveedor").val()
        };

        if (!data.cod_empresa || !data.cod_proveedor || !data.fecha_contrasenia) {
            alert("Completa todos los campos del encabezado.");
            return;
        }

        $.ajax({
            url: "/contrasenias/crear-contrasenia",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`
            },
            success: function (response) {
            alert(response.mensaje);

                $("#cod_contrasenia").val(response.cod_contrasenia);

                // Guardamos los valores globales
                codContraseniaActual = response.cod_contrasenia;
                codEmpresaActual = $("#cod_empresa").val();

                // Deshabilitamos los campos del encabezado para que no los cambien después
                $("#fecha_contrasenia").prop("disabled", true);
                $("#cod_empresa").prop("disabled", true);
                $("#cod_proveedor").prop("disabled", true);
                $("#guardarContrasenia").prop("disabled", true);

                // Mostramos el formulario de detalle si estaba oculto
                $("#formulario-detalle").show();
            },

            error: function (xhr) {
                alert("Error al guardar: " + xhr.responseText);
            }
        });

    });

    $("#cod_empresa").on("change", function () {
        const cod_empresa = $(this).val();
        if (cod_empresa) {
            cargarProveedores(cod_empresa);
        }
    });

    // Botón guardar solo encabezado
    $("#guardarContrasenia").click(function () {
        const data = {
            fecha_contrasenia: $("#fecha_contrasenia").val(),
            cod_empresa: $("#cod_empresa").val(),
            cod_proveedor: $("#cod_proveedor").val()
        };

        if (!data.cod_empresa || !data.cod_proveedor || !data.fecha_contrasenia) {
            alert("Completa todos los campos del encabezado.");
            return;
        }

        $.ajax({
            url: "/contrasenias/crear-contrasenia",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}` 
            },
            success: function (response) {
                alert(response.mensaje);
                location();
            },
            error: function (xhr) {
                alert("Error al guardar: " + xhr.responseText);
            }
        });

    });

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
// --------------------------------------------------------------------------------------------------------

$(document).ready(function () {
    $("#btnGuardarDetalle").on("click", function (e) {
        e.preventDefault();

        // Usamos variables globales
        if (!codContraseniaActual || !codEmpresaActual) {
            alert("Debe seleccionar una contraseña y una empresa antes de agregar un detalle.");
            return;
        }

        const detalle = {
            cod_contrasenia: codContraseniaActual,
            cod_empresa: codEmpresaActual,
            num_factura: parseInt($("#num_factura").val()),
            cod_moneda: $("#cod_moneda").val(),
            monto: parseFloat($("#monto").val()),
            retension_iva: $("#retension_iva").is(":checked") ? "S" : "N",
            retension_isr: $("#retension_isr").is(":checked") ? "S" : "N",
            numero_retension_iva: $("#numero_retension_iva").val() || null,
            numero_retension_isr: $("#numero_retension_isr").val() || null
        };

        // Paso 1: obtener la siguiente línea disponible
        $.get(`/contrasenias/linea`, {
            cod_contrasenia: detalle.cod_contrasenia,
            cod_empresa: detalle.cod_empresa
        }, function (response) {
            detalle.linea = response.linea;

            // Paso 2: enviar el detalle al backend
            $.ajax({
                type: "POST",
                url: "/contrasenias/detalle",
                data: JSON.stringify(detalle),
                contentType: "application/json",
                success: function (data) {
                    alert("Detalle guardado exitosamente");

                    // Limpiar campos
                    $("#num_factura").val("");
                    $("#cod_moneda").val("");
                    $("#monto").val("");
                    $("#retension_iva").prop("checked", false);
                    $("#retension_isr").prop("checked", false);
                    $("#numero_retension_iva").val("");
                    $("#numero_retension_isr").val("");
                },
                error: function (xhr) {
                    console.error(xhr.responseText);
                    alert("Error al guardar el detalle");
                }
            });
        }).fail(function () {
            alert("Error al calcular la línea del detalle");
        });
    });
});





