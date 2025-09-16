function mostrarSesionUsuario() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = "/";
        return;
    }
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const nombre = payload.nombre || payload.usuario || "Usuario";
        $('#nombre-usuario').text(nombre);
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

$(document).ready(function () {
    mostrarSesionUsuario();

    // Cerrar sesión
    $(document).on('click', '#cerrarSesion', function (e) {
        e.preventDefault();
        cerrarSesion();
    });
});