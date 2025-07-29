let detalles = [];

$(document).ready(function () {

    // Agregar detalle a la lista
    $("#btnAgregarDetalle").click(function () {
        const usuario = $("#usuario").val().trim();
        const clave = $("#clave").val().trim();
        const descripcion = $("#descripcion").val().trim();

        if (usuario && clave && descripcion) {
            detalles.push({ usuario, clave, descripcion });
            actualizarTablaDetalles();

            // Limpiar inputs
            $("#usuario").val("");
            $("#clave").val("");
            $("#descripcion").val("");
        } else {
            alert("Todos los campos del detalle son requeridos.");
        }
    });

    // Eliminar fila de la tabla
    $(document).on("click", ".btnEliminar", function () {
        const index = $(this).data("index");
        detalles.splice(index, 1);
        actualizarTablaDetalles();
    });

    // Crear Contraseña (encabezado + todos los detalles)
    $("#btnCrearContrasenia").click(function () {
        const nombre_sitio = $("#nombre_sitio").val().trim();
        const observaciones = $("#observaciones").val().trim();

        if (!nombre_sitio) {
            alert("El nombre del sitio es obligatorio.");
            return;
        }

        if (detalles.length === 0) {
            alert("Agrega al menos un detalle.");
            return;
        }

        const payload = {
            encabezado: {
                nombre_sitio,
                observaciones
            },
            detalles: detalles
        };

        $.ajax({
            url: "/api/contrasenias/crear",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(payload),
            success: function (response) {
                alert("Contraseña creada correctamente.");
                // Reset
                $("#form-encabezado")[0].reset();
                detalles = [];
                actualizarTablaDetalles();
            },
            error: function (xhr) {
                alert("Error al crear la contraseña.");
                console.error(xhr.responseText);
            }
        });
    });

    function actualizarTablaDetalles() {
        const tbody = $("#tabla-detalles tbody");
        tbody.empty();
        detalles.forEach((item, index) => {
            tbody.append(`
                <tr>
                    <td>${item.usuario}</td>
                    <td>${item.clave}</td>
                    <td>${item.descripcion}</td>
                    <td><button class="btn btn-danger btn-sm btnEliminar" data-index="${index}">Eliminar</button></td>
                </tr>
            `);
        });
    }
});

