$(document).ready(function () {
    // Validación de permisos
    if (validar_permisos(2) !== 'S') {
        alert("No tienes permiso para registrar usuarios.");
        window.location.href = "inicio.html";
        return;
    }

    // El resto de tu código existente
    cargarOpciones();

    $("#formRegistro").on("submit", function (e) {
        e.preventDefault();
        const permisosSeleccionados = [];
        $("input.permiso-opcion:checked").each(function () {
            permisosSeleccionados.push(parseInt($(this).val()));
        });

        const datos = {
            nombre: $("#regNombre").val(),
            usuario: $("#regUsuario").val(),
            contrasenia: $("#regContrasenia").val(),
            correo: $("#regCorreo").val(),
            permisos: permisosSeleccionados
        };

        $.ajax({
            url: "http://127.0.0.1:8000/api/usuarios",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(datos),
            success: function (res) {
                Swal.fire({
                    title: "¡Éxito!",
                    text: res.mensaje || "Usuario registrado exitosamente.",
                    icon: "success",
                    confirmButtonText: "OK"
                }).then(() => {
                    // Limpiar formulario después de cerrar la alerta
                    limpiaformulario();
                });
            },
            error: function (xhr) {
                Swal.fire({
                    title: "Error",
                    text: xhr.responseJSON?.mensaje || "Error del servidor: " + xhr.responseText,
                    icon: "error",
                    confirmButtonText: "OK"
                });
            }
        });

    });
});

function cargarOpciones(){
    $.ajax({
        url: "/api/usuarios/opciones",
        method: "GET",
        success: function (opciones) {
            const contenedor = $("#opcionesChecklist");
            contenedor.empty();
            opciones.forEach(opcion => {
                contenedor.append(`
                    <div class="form-check">
                        <input class="form-check-input permiso-opcion" type="checkbox" value="${opcion.cod_opcion}" id="permiso_${opcion.cod_opcion}">
                        <label class="form-check-label" for="permiso_${opcion.cod_opcion}">
                            ${opcion.nombre_opcion}
                        </label>
                    </div>
                `);
            });
        },
        error: function () {
            $("#opcionesChecklist").html('<div class="alert alert-danger">Error al cargar las opciones.</div>');
        }
    });
}

function limpiaformulario() {
    $("#regNombre").val("");
    $("#regUsuario").val("");
    $("#regContrasenia").val("");
    $("#regCorreo").val("");
}





