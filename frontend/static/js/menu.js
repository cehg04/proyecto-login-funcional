function mostrarSesionUsuario() {
    const token = localStorage.getItem('token');

    if (!token) {
        window.location.href = "/login.html";
        return;
    }

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));

        const nombre = payload.nombre || payload.usuario || "Usuario";
        const rol = payload.rol === "admin" ? "Administrador" : "Usuario";

        $('#nombre-usuario').text(nombre);
        $('#rol-usuario').text(rol);
        $('#user-avatar').text(nombre.charAt(0).toUpperCase());

    } catch (e) {
        console.error("Error al decodificar el token:", e);
        cerrarSesion();
    }
}

function cerrarSesion() {
    localStorage.removeItem('token');
    window.location.href = "/";
}

function cargarVista(pagina) {
    if (!localStorage.getItem('token')) {
        window.location.href = "/";
        return;
    }

    $(".menu-item").removeClass("active");
    $(`[data-page="${pagina}"]`).addClass("active");

    $("#contenido-dinamico").load(`/static/fragmentos/${pagina}.html`, function (response, status) {
        if (status === "error") {
            $("#contenido-dinamico").html(`
                <div class="alert alert-danger m-3">
                    <strong>Error:</strong> No se pudo cargar la vista <code>${pagina}.html</code>
                </div>
            `);
        }
    });
}

$(document).ready(function () {
    mostrarSesionUsuario(); // Mostrar datos al cargar el menú
    cargarVista("inicio"); // Cargar vista por defecto

    $(document).on('click', '.menu-item', function (e) {
        e.preventDefault();
        const pagina = $(this).data("page");
        if (pagina) {
            cargarVista(pagina);
        }
    });

    $(document).on('click', '#cerrarSesion', function (e) {
        e.preventDefault();
        cerrarSesion();
    });
});


