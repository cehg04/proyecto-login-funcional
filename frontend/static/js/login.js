$(document).ready(function(){
    $("#formLogin").on("submit", function (e) {
        e.preventDefault();

        const usuario = $("input[name='usuario']").val().trim();
        const contrasenia = $("input[name='contrasenia']").val().trim();

        if (!usuario || !contrasenia){
            $("#msg").html(`<div class="alert alert-warning">Por favor, Primero completa los campos.</div>`);
            return;
        }

        const datos = { usuario, contrasenia };

        $.ajax({
            url: "http://127.0.0.1:8000/api/login",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(datos),
            success: function (res) {
                if (res.token) {
                    // Guardar token en cookie y localStorage
                    document.cookie = `token=${res.token}; path=/; max-age=3600; samesite=strict`;
                    localStorage.setItem("token", res.token);

                    $("#msg").html(`<div class="alert alert-success">Bienvenido ${res.usuario}</div>`);
                    setTimeout(() => {
                        // redirecciona a donde queremos que vaya
                        window.location.href = "/menu.html";
                    }, 1000);
                } else {
                    $("#msg").html(`<div class="alert alert-danger">${res.error || "Credenciales incorrectas"}</div>`);
                }
            },
            error: function () {
                $("#msg").html(`<div class="alert alert-danger">Error al iniciar sesión</div>`);
            }
        });
    });
});



