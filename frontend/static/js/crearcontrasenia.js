$(document).ready(function () {
    let detalles = [];

    cargarEmpresas(); // Cargar empresas al iniciar

    // Cuando cambia la empresa, cargar los proveedores asociados
    $("#cod_empresa").on("change", function () {
        const cod_empresa = $(this).val();
        if (cod_empresa) {
            cargarProveedores(cod_empresa);
        }
    });

    // Agregar un nuevo detalle a la tabla temporal
    $("#agregarDetalle").click(function () {
        const cod_documento = $("#cod_documento").val();
        const cod_usuario = $("#cod_usuario").val();
        const contrasenia = $("#contrasenia").val();

        if (!cod_documento || !cod_usuario || !contrasenia) {
            alert("Completa todos los campos del detalle.");
            return;
        }

        const nuevoDetalle = {
            cod_documento,
            cod_usuario,
            contrasenia
        };

        detalles.push(nuevoDetalle);
        mostrarDetalles();
        limpiarFormularioDetalle();
    });

    // Enviar todo al backend
    $("#guardarContrasenia").click(function () {
        const encabezado = {
            numero_contrasenia: $("#numero_contrasenia").val(),
            cod_empresa: $("#cod_empresa").val(),
            cod_proveedor: $("#cod_proveedor").val(),
            
        };


        if (detalles.length === 0) {
            alert("Agrega al menos un detalle.");
            return;
        }

        const datos = {
            encabezado,
            detalles
        };

        $.ajax({
            url: "/contrasenias/crear",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(datos),
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
                    <td>${item.cod_documento}</td>
                    <td>${item.cod_usuario}</td>
                    <td>${item.contrasenia}</td>
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
        $("#cod_documento").val("");
        $("#cod_usuario").val("");
        $("#contrasenia").val("");
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
        $.get(`/contrasenias/proveedores?cod_empresa=${cod_empresa}`, function (data) {
            $("#cod_proveedor").empty().append('<option value="">Seleccione Proveedor</option>');
            data.forEach(prov => {
                $("#cod_proveedor").append(`<option value="${prov.cod_proveedor}">${prov.nombre}</option>`);
            });
        });
    }
});



