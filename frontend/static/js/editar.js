$(document).ready(function () {

    if (validar_permisos(3) !== 'S') {
        $("#contenido-dinamico").html('<div class="alert alert-danger">No tienes permiso para editar usuarios.</div>');
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const cod_usuario = params.get("cod_usuario");

    if (!cod_usuario) {
        Swal.fire({
            title: "Atención",
            text: "Código de usuario no proporcionado.",
            icon: "warning",
            confirmButtonText: "OK"
        }).then(() => {
            window.location.href = "crudusuarios.html";
        });
        return;
    }

    $.get(`/api/usuarios/${cod_usuario}`, function (usuario) {  
        $("#edit_cod_usuario").val(cod_usuario);
        $("#edit_usuario").val(usuario.usuario).prop("readonly", true);
        $("#edit_nombre").val(usuario.nombre);
        $("#edit_correo").val(usuario.correo);

        if (usuario.estado === "A" || usuario.estado === "I") {
            $("#edit_estado").val(usuario.estado);
        } else {
            console.warn("Estado inesperado:", usuario.estado);
        }

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
            });
        });
    });

    $("#formEditarUsuario").submit(function (e) {
        e.preventDefault();

        const datosUsuario = {
            nombre: $('#edit_nombre').val().trim(),
            usuario: $('#edit_usuario').val().trim(),
            correo: $('#edit_correo').val().trim(),
            estado: $('#edit_estado').val()
        };

        if (!datosUsuario.nombre || !datosUsuario.usuario) {
            Swal.fire({
                title: "Atención",
                text: "Nombre y Usuario son obligatorios.",
                icon: "warning",
                confirmButtonText: "OK"
            });
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
                        Swal.fire({
                            title: "¡Éxito!",
                            text: "Usuario actualizado correctamente.",
                            icon: "success",
                            confirmButtonText: "OK"
                        }).then(() => {
                            window.location.href = "crudusuarios.html";
                        });
                    },
                    error: function () {
                        Swal.fire({
                            title: "Error",
                            text: "Error al actualizar permisos",
                            icon: "error",
                            confirmButtonText: "OK"
                        });
                    }
                });
            },
            error: function () {
                Swal.fire({
                    title: "Error",
                    text: "Error al actualizar un usuario",
                    icon: "error",
                    confirmButtonText: "OK"
                });
            }
        });
    });

});

