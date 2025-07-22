// Mostrar información de sesión
function mostrarSesionUsuario() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        // Decodificar token
        const payload = JSON.parse(atob(token.split('.')[1]));
        
        // Actualizar UI
        $('#nombre-usuario').text(payload.nombre || payload.usuario);
        $('#rol-usuario').text(payload.rol === "admin" ? "Administrador" : "Usuario");
        
        // Opcional: Mostrar tiempo restante de sesión
        const expDate = new Date(payload.exp * 1000);
        actualizarContadorSesion(expDate);
        
    } catch (e) {
        console.error("Error al decodificar token:", e);
        cerrarSesion();
    }
}

// Contador de sesión
function actualizarContadorSesion(expDate) {
    const timer = setInterval(() => {
        const ahora = new Date();
        const segundosRestantes = Math.floor((expDate - ahora) / 1000);
        
        if (segundosRestantes <= 0) {
            clearInterval(timer);
            cerrarSesion();
        } else {
            const minutos = Math.floor(segundosRestantes / 60);
            const segundos = segundosRestantes % 60;
            $('#contador-sesion').text(`Sesión activa (${minutos}m ${segundos}s)`);
        }
    }, 1000);
}

// Cerrar sesión
function cerrarSesion() {
    localStorage.removeItem('token');
    window.location.href = "/";
}

// Al cargar la página
$(document).ready(function() {
    mostrarSesionUsuario();
    
    // Manejador para el botón de cerrar sesión
    $('#cerrarSesion').click(cerrarSesion);
});