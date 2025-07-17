$(document).ready(function () {
    cargarUsuarios();

    function cargarUsuarios() {
        $.ajax({
            url: "http://127.0.0.1:8000/api/usuarios",
            method: "GET",
            success: function (data) {
                const tbody = $("#tablaUsuarios tbody");
                tbody.empty();
                data.forEach(usuario => {
                    const estado = usuario.estado === "A" ? "Activo" : "Inactivo";
                    const clase = usuario.estado === "A" ? "btn-danger" : "btn-success";
                    const texto = usuario.estado === "A" ? "Inactivar" : "Activar";

                    tbody.append(`
                        <tr>
                            <td>${usuario.cod_usuario}</td>
                            <td>${usuario.nombre}</td>
                            <td>${usuario.usuario}</td>
                            <td>${usuario.correo || ""}</td>
                            <td>${estado}</td>
                            <td>
                                <button class="btn btn-sm btn-warning btn-editar" data-id="${usuario.cod_usuario}">Editar</button>
                                <button class="btn btn-sm ${clase} btn-estado" data-id="${usuario.cod_usuario}" data-estado="${usuario.estado}">${texto}</button>
                            </td>
                        </tr>
                    `);
                });
            },
            error: () => alert("Error al cargar usuarios")
        });
    }

    // Activar/Inactivar
    $(document).on("click", ".btn-estado", function () {
        const id = $(this).data("id");
        const nuevoEstado = $(this).data("estado") === "A" ? "I" : "A";

        $.ajax({
            url: `http://127.0.0.1:8000/api/usuarios/${id}/estado`,
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify({ estado: nuevoEstado }),
            success: () => cargarUsuarios(),
            error: () => alert("No se pudo cambiar el estado")
        });
    });

    // Abrir modal de edición
    $(document).on("click", ".btn-editar", function () {
        const id = $(this).data("id");

        $.get(`http://127.0.0.1:8000/api/usuarios/${id}`, function (usuario) {
            $("#edit_cod_usuario").val(usuario.cod_usuario);
            $("#edit_nombre").val(usuario.nombre);
            $("#edit_usuario").val(usuario.usuario);
            $("#edit_correo").val(usuario.correo || "");

            const modal = new bootstrap.Modal(document.getElementById("modalEditarUsuario"));
            modal.show();
        });
    });

    // Guardar cambios del modal
    $("#formEditarUsuario").on("submit", function (e) {
        e.preventDefault();

        const id = $("#edit_cod_usuario").val();
        const datos = {
            nombre: $("#edit_nombre").val(),
            usuario: $("#edit_usuario").val(),
            correo: $("#edit_correo").val()
        };

        $.ajax({
            url: `http://127.0.0.1:8000/api/usuarios/${id}`,
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify(datos),
            success: function () {
                const modal = bootstrap.Modal.getInstance(document.getElementById("modalEditarUsuario"));
                modal.hide();
                cargarUsuarios();
            },
            error: () => alert("Error al guardar cambios")
        });
    });
});

