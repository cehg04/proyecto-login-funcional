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
});