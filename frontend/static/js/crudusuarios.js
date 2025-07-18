$(document).ready(function () {
    // Función para cargar todos los usuarios y mostrarlos en la tabla
    function cargarUsuarios() {
        $.get("/api/usuarios", function (usuarios) {
            const tbody = $("#tablaUsuarios tbody");
            tbody.empty();

            usuarios.forEach(u => {
                tbody.append(`
                    <tr data-id="${u.cod_usuario}">
                        <td>${u.cod_usuario}</td>
                        <td>${u.nombre}</td>
                        <td>${u.usuario}</td>
                        <td>${u.correo ?? ""}</td>
                        <td>${u.estado === "A" ? "Activo" : "Inactivo"}</td>
                        <td>
                            <button class="btn btn-warning btn-editar">Editar</button>
                        </td>
                    </tr>
                `);
            });
        });
    }

    cargarUsuarios();

    // Evento click en botón "Editar" abre modal con los datos
    $("#tablaUsuarios").on("click", ".btn-editar", function () {
        const fila = $(this).closest("tr");
        const cod_usuario = fila.data("id");
        const nombre = fila.find("td").eq(1).text();
        const usuario = fila.find("td").eq(2).text();
        const correo = fila.find("td").eq(3).text();
        const estado = fila.find("td").eq(4).text() === "Activo" ? "A" : "I";

        $("#edit_cod_usuario").val(cod_usuario);
        $("#edit_nombre").val(nombre);
        $("#edit_usuario").val(usuario);
        $("#edit_correo").val(correo);
        $("#edit_estado").val(estado);

        const modal = new bootstrap.Modal(document.getElementById("modalEditarUsuario"));
        modal.show();
    });

    // Botón "Guardar Cambios" envía PUT al backend
    $("#btnGuardarCambios").click(function () {
        const cod_usuario = $("#edit_cod_usuario").val();
        const data = {
            nombre: $("#edit_nombre").val(),
            usuario: $("#edit_usuario").val(),
            correo: $("#edit_correo").val(),
            estado: $("#edit_estado").val()
        };

        $.ajax({
            url: `/api/usuarios/${cod_usuario}`,
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function () {
                alert("Usuario actualizado correctamente");
                cargarUsuarios();
                const modalEl = document.getElementById("modalEditarUsuario");
                const modal = bootstrap.Modal.getInstance(modalEl);
                modal.hide();
            },
            error: function () {
                alert("Error al actualizar usuario");
            }
        });
    });
});
