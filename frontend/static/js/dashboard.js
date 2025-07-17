$(document).ready(function () {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Acceso denegado. Por favor inicia sesión.");
        window.location.href = "/";
    }

    // Mostrar nombre del usuario desde token
    function parseJwt(token) {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(c =>
            '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        ).join(''));
        return JSON.parse(jsonPayload);
    }

    const payload = parseJwt(token);
    $("#nombreUsuario").text(payload.usuario || "Usuario");

    // Cerrar sesión
    $("#cerrarSesion").on("click", function () {
        localStorage.removeItem("token");
        document.cookie = "token=; path=/; max-age=0";
        window.location.href = "/";
    });

    // Navegación
    $("#linkInicio").on("click", function () {
        $("#vistaInicio").show();
        $("#vistaUsuarios").hide();
    });

    $("#linkUsuarios").on("click", function () {
        $("#vistaInicio").hide();
        $("#vistaUsuarios").show();
        cargarUsuarios();
    });

    // Mostrar/ocultar formulario de nuevo usuario
    $("#btnNuevoUsuario").on("click", function () {
        $("#formRegistroUsuario").toggle();
    });

    // Registrar nuevo usuario
    $("#guardarNuevoUsuario").on("click", function () {
        const nombre = $("#regNombre").val().trim();
        const usuario = $("#regUsuario").val().trim();
        const correo = $("#regCorreo").val().trim();
        const contrasenia = $("#regContrasenia").val().trim();

        if (!nombre || !usuario || !correo || !contrasenia) {
            alert("Por favor, completa todos los campos.");
            return;
        }

        $.ajax({
            url: "/api/usuarios/",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ nombre, usuario, correo, contrasenia }),
            success: function () {
                alert("Usuario registrado correctamente.");
                $("#formRegistroUsuario input").val("");
                $("#formRegistroUsuario").hide();
                cargarUsuarios();
            },
            error: function () {
                alert("Error al registrar usuario.");
            }
        });
    });

    // Cargar usuarios
    function cargarUsuarios() {
        $.ajax({
            url: "/api/usuarios/",
            method: "GET",
            success: function (usuarios) {
                const tbody = $("#tablaUsuarios tbody");
                tbody.empty();
                usuarios.forEach(user => {
                    const fila = `
                        <tr>
                            <td>${user.cod_usuario}</td>
                            <td><input type="text" value="${user.nombre}" class="form-control nombre"></td>
                            <td><input type="text" value="${user.usuario}" class="form-control usuario"></td>
                            <td><input type="email" value="${user.correo}" class="form-control correo"></td>
                            <td>
                                <button class="btn btn-${user.estado === 'A' ? 'success' : 'secondary'} btn-sm btn-estado" data-id="${user.cod_usuario}">
                                    ${user.estado}
                                </button>
                            </td>
                            <td>
                                <button class="btn btn-primary btn-sm btn-guardar" data-id="${user.cod_usuario}">Guardar</button>
                            </td>
                        </tr>`;
                    tbody.append(fila);
                });
            }
        });
    }

    // Guardar cambios
    $(document).on("click", ".btn-guardar", function () {
        const fila = $(this).closest("tr");
        const id = $(this).data("id");
        const nombre = fila.find(".nombre").val();
        const usuario = fila.find(".usuario").val();
        const correo = fila.find(".correo").val();

        $.ajax({
            url: `/api/usuarios/${id}`,
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify({ nombre, usuario, correo }),
            success: function () {
                alert("Usuario actualizado correctamente.");
                cargarUsuarios();
            },
            error: function () {
                alert("Error al actualizar usuario.");
            }
        });
    });

    // Cambiar estado
    $(document).on("click", ".btn-estado", function () {
        const id = $(this).data("id");
        $.ajax({
            url: `/api/usuarios/estado/${id}`,
            method: "PUT",
            success: function () {
                cargarUsuarios();
            }
        });
    });

    // Mostrar bienvenida inicial
    $("#vistaInicio").show();
    $("#vistaUsuarios").hide();
});
