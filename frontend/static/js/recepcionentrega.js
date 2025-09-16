$(document).ready(function() {

      if (validar_permisos(10) !== 'S') {
    Swal.fire({
      title: "Acceso denegado",
      text: "No tienes permiso para Recepcionar entregas",
      icon: "warning",
      confirmButtonText: "OK"
    }).then(() => {
      window.location.href = "inicio.html";
    });
    return;
  }

    $('#filtrosContainer').html(`
        <div class="row mb-3">
            <div class="col-md-4">
                <label for="fechaInicio">Fecha Inicio:</label>
                <input type="date" id="fechaInicio" class="form-control">
            </div>
            <div class="col-md-4">
                <label for="fechaFin">Fecha Fin:</label>
                <input type="date" id="fechaFin" class="form-control">
            </div>  
            <div class="col-md-4 d-flex align-items-end">
                <button id="btnFiltrar" class="btn btn-primary">Buscar</button>
            </div>
        </div>
    `);

    const today = new Date().toISOString().split('T')[0];
    $('#fechaInicio').val(today);
    $('#fechaFin').val(today);

    cargarEntregas();

    $('#btnFiltrar').click(function() {
        cargarEntregas();
    });
});

function obtenerTokenYUsuario() {
    let token = localStorage.getItem("token") || localStorage.getItem("jwt");
    if (!token) {
        console.error("No se encontró token en localStorage");
        return null;
    }

    try {
        let payloadBase64 = token.split('.')[1];
        let payloadJson = atob(payloadBase64);
        let payload = JSON.parse(payloadJson);

        console.log("Payload del token:", payload);

        let cod_usuario = payload.cod_usuario;
        console.log("cod_usuario extraído:", cod_usuario);

        return { token, cod_usuario };
    } catch (error) {
        console.error("Error al decodificar el token:", error);
        return null;
    }
}

function formatearFecha(fechaISO) {
    if (!fechaISO) return "";
    let partes = fechaISO.split("-"); // ["YYYY","MM","DD"]
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
}

function cargarEntregas() {
    let datosSesion = obtenerTokenYUsuario();
    if (!datosSesion) return;

    let fecha_inicio = $('#fechaInicio').val() || "";
    let fecha_fin = $('#fechaFin').val() || "";

    $.ajax({
        url: `/entregas/pendientes/${datosSesion.cod_usuario}`,
        method: "GET",
        headers: {
            "Authorization": `Bearer ${datosSesion.token}`
        },
        data: { fecha_inicio, fecha_fin }, // 🔹 ahora mandamos filtros al backend
        success: function(response) {
            console.log("Respuesta del backend:", response);
            mostrarEntregas(response);
        },
        error: function(err) {
            console.error("Error al cargar entregas:", err);
        }
    });
}

function mostrarEntregas(entregas) {
    let tabla = $("#tablaEntregas tbody");
    tabla.empty();

    if (entregas.length === 0) {
        // Mostrar mensaje de tabla vacía
        let fila = `<tr>
            <td colspan="4" class="text-center fw-bold">Tabla sin entregas</td>
        </tr>`;
        tabla.append(fila);
        return;
    }

    entregas.forEach(function(entrega) {
        let fila = `<tr>
            <td style="text-align: center;">${formatearFecha(entrega.fecha_entrega)}</td>
            <td style="text-align: center;">${entrega.usuario_creacion}</td>
            <td style="text-align: center;">${entrega.estado}</td>
            <td>
                <button class="btn btn-success btn-sm btnRecibir" 
                        data-cod_entrega="${entrega.cod_entrega}" 
                        data-cod_empresa="${entrega.cod_empresa}">
                    Recibir
                </button>
            </td>
        </tr>`;
        tabla.append(fila);
    });

$(document).on("click", ".btnRecibir", function() {
    let cod_entrega = $(this).data("cod_entrega");
    let cod_empresa = $(this).data("cod_empresa");

    if (!cod_entrega || !cod_empresa) {
        console.error("No se encontraron los datos necesarios en el botón");
        return;
    }

    window.location.href = `/recepcioncompleta.html?cod_entrega=${cod_entrega}&cod_empresa=${cod_empresa}`;
});


}












