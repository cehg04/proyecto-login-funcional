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