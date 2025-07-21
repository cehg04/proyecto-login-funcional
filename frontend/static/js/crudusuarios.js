$(function () {
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
                            <button class="btn btn-warning btn-sm btn-editar">Editar</button>
                        </td>
                    </tr>
                `);
            });
        }).fail(() => alert("Error al cargar usuarios"));
    }

    cargarUsuarios();

    const modalEditarUsuario = new bootstrap.Modal(document.getElementById("modalEditarUsuario"));

    // Delegamos el evento click en la tabla
    $("#tablaUsuarios").on("click", ".btn-editar", function () {
        console.log("Botón editar presionado"); // Para depurar
        const fila = $(this).closest("tr");
        const cod_usuario = fila.data("id");

        $("#edit_cod_usuario").val(cod_usuario);
        $("#edit_nombre").val(fila.find("td").eq(1).text());
        $("#edit_usuario").val(fila.find("td").eq(2).text());
        $("#edit_correo").val(fila.find("td").eq(3).text());
        $("#edit_estado").val(fila.find("td").eq(4).text() === "Activo" ? "A" : "I");

        // Limpiar y cargar permisos
        const contenedor = $("#edit_permisos").empty();
        $.get("/api/usuarios/opciones", function (opciones) {
            $.get(`/api/usuarios/permisos/${cod_usuario}`, function (permisos_actuales) {
                const permisos_map = {};
                permisos_actuales.forEach(p => permisos_map[p.cod_opcion] = p.permiso === "S");

                opciones.forEach(op => {
                    const checked = permisos_map[op.cod_opcion] ? "checked" : "";
                    contenedor.append(`
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="edit_permiso" value="${op.cod_opcion}" id="permiso_${op.cod_opcion}" ${checked}>
                            <label class="form-check-label" for="permiso_${op.cod_opcion}">
                                ${op.nombre_opcion}
                            </label>
                        </div>
                    `);
                });
                modalEditarUsuario.show();
            });
        });
    });

    // Guardar cambios
    $("#btnGuardarCambios").click(function () {
        const cod_usuario = $('#edit_cod_usuario').val();
        const datosUsuario = {
            nombre: $('#edit_nombre').val().trim(),
            usuario: $('#edit_usuario').val().trim(),
            correo: $('#edit_correo').val().trim(),
            estado: $('#edit_estado').val()
        };

        if (!datosUsuario.nombre || !datosUsuario.usuario) {
            alert("Nombre y Usuario son obligatorios.");
            return;
        }

        $.ajax({
            url: `/api/usuarios/${cod_usuario}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(datosUsuario),
            success: function () {
                const permisos = [];
                $("input[name='edit_permiso']:checked").each(function () {
                    permisos.push(parseInt($(this).val()));
                });

                $.ajax({
                    url: `/api/usuarios/permisos/${cod_usuario}`,
                    method: 'PUT',
                    contentType: 'application/json',
                    data: JSON.stringify({ permisos }),
                    success: function () {
                        modalEditarUsuario.hide();
                        cargarUsuarios();
                    },
                    error: () => alert('Error al actualizar permisos')
                });
            },
            error: () => alert('Error al actualizar usuario')
        });
    });
});
