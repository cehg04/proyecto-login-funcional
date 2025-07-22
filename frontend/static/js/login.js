$(document).ready(function(){
    $("#formLogin").on("submit", function (e) {
        e.preventDefault();

        const usuario = $("input[name='usuario']").val().trim();
        const contrasenia = $("input[name='contrasenia']").val().trim();

        if (!usuario || !contrasenia){
            $("#msg").html(`<div class="alert alert-warning">Por favor, completa los campos.</div>`);
            return;
        }

        $.ajax({
            url: "http://127.0.0.1:8000/api/login",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ usuario, contrasenia }),
            success: function (res) {
                if (res.token) {
                    // 1. Guardar token en localStorage y cookies
                    localStorage.setItem("token", res.token);
                    document.cookie = `token=${res.token}; path=/; max-age=3600; samesite=strict`;
                    
                    // 2. Mostrar mensaje de éxito
                    $("#msg").html(`<div class="alert alert-success">Bienvenido ${res.usuario}</div>`);
                    
                    // 3. Redireccionar después de 1 segundo
                    setTimeout(() => {
                        window.location.href = "/menu.html";
                    }, 1000);
                } else {
                    $("#msg").html(`<div class="alert alert-danger">Error: No se recibió token</div>`);
                }
            },
            error: function (xhr) {
                let errorMsg = "Error al iniciar sesión";
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    errorMsg = xhr.responseJSON.detail;
                }
                $("#msg").html(`<div class="alert alert-danger">${errorMsg}</div>`);
            }
        });
    });
});



