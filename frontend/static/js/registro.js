$(document).ready(function () {
    $("#formRegistro").on("submit", function (e) {
        e.preventDefault();

        const datos = {
            nombre: $("#regNombre").val(),
            usuario: $("#regUsuario").val(),
            contrasenia: $("#regContrasenia").val(),
            correo: $("#regCorreo").val()
        };

        $.ajax({
            url: "http://127.0.0.1:8000/api/usuarios",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(datos),
            success: function (res) {
                $("#msg").html(`<div class="alert alert-success">${res.mensaje || 'Usuario registrado exitosamente.'}</div>`);

                // Limpiar el formulario inmediatamente
                limpiaformulario();
            },
            error: function (xhr) {
                $("#msg").html(`<div class="alert alert-danger">Error del servidor: ${xhr.responseText}</div>`);
            }
        });
    });
});

function limpiaformulario() {
    $("#regNombre").val("");
    $("#regUsuario").val("");
    $("#regContrasenia").val("");
    $("#regCorreo").val("");
}





