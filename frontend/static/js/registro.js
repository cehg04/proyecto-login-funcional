$(document).ready(function() {
    $("#formRegistro").on("submit", function(e) {
        e.preventDefault();

        const datos = {
            nombre: $("input[name='nombre']").val(),
            usuario: $("input[name='usuario']").val(),
            contrasenia: $("input[name='contrasenia']").val(),
            correo: $("input[name='correo']").val()
        };

        $.ajax({
            url: "http://127.0.0.1:8000/api/usuarios",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(datos),
            success: function(res) {
                if (res.mensaje) {
                    $("#msg").html(`<div class="alert alert-success">${res.mensaje}</div>`);
                } else {
                    $("#msg").html(`<div class="alert alert-warning">Operación completada, pero sin respuesta clara.</div>`);
                }
            },
            error: function(xhr, status, error) {
                $("#msg").html(`<div class="alert alert-danger">Error del servidor: ${xhr.responseText}</div>`);
            }
        });
    });
});
