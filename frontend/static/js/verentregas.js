$(document).ready(function () {

    //funcion para extraer el cod_usuario
    function getUsuarioIdFromToken() {
        const token = localStorage.getItem('token');
        if (!token) return null;

        try {
            const payload = token.split('.')[1];
            const decoded = JSON.parse(atob(payload));
            return decoded.cod_usuario;
        } catch (e) {
            console.error("Error al decodificar token:", e);
            return null;
        }
    }

    // Agregar filtros
    $('#filtrosContainer').html(`
        <div class="row mb-3">
            <div class="col-md-3">
                <label for="fechaInicio">Fecha Inicio:</label>
                <input type="date" id="fechaInicio" class="form-control">
            </div>
            <div class="col-md-3">
                <label for="fechaFin">Fecha Fin (opcional):</label>
                <input type="date" id="fechaFin" class="form-control">
            </div>  
            <div class="col-md-3">
                <label for="empresaSelect">Empresa:</label>
                <select id="empresaSelect" class="form-select">
                    <option value="">Todas</option>
                </select>
            </div>
            <div class="col-md-3 d-flex align-items-end">
                <button id="btnFiltrar" class="btn btn-primary">Buscar</button>
            </div>
        </div>
    `);

    // Fecha por defecto hoy
    const today = new Date().toISOString().split('T')[0];
    $('#fechaInicio').val(today);
    $('#fechaFin').val(today);

    // Cargar empresas
    $.get('/contrasenias/empresas', function(data) {
        const select = $('#empresaSelect');
        data.forEach(empresa => {
            select.append(`<option value="${empresa.cod_empresa}">${empresa.nombre}</option>`);
        });
    });

    // Inicializar DataTable
    const table = $("#tablaEntregas").DataTable({
        ajax: {
            url: "/entregas/encabezados",
            dataSrc: "",
            data: function(d) {
                // Enviar filtros al backend
                d.fecha_inicio = $('#fechaInicio').val();
                d.fecha_fin = $('#fechaFin').val() || "";
                d.cod_empresa = $('#empresaSelect').val() || "";
                console.log("Filtros enviados:", $.param(d)); // <--- depuración
            }
        },
        columns: [
            { data: "num_entrega", title: "Número de Entrega" },
            { data: "empresa_nombre", title: "Empresa" },
            { 
                data: "fecha_entrega", 
                title: "Fecha Entrega",
                render: function(data) {
                    // data = "YYYY-MM-DD"
                    if(!data) return "";
                    const partes = data.split('-'); // ["2025","08","26"]
                    return `${partes[2]}/${partes[1]}/${partes[0]}`; // "26/08/2025"
                }
            },
            { data: "tipo_entrega", title: "Tipo de Entrega" },
            { 
                data: "estado", 
                title: "Estado",
                render: function (data) {
                    switch (data) {
                        case "Pendiente": return '<span class="badge bg-warning">Pendiente</span>';
                        case "Recibido": return '<span class="badge bg-success">Recibido</span>';
                        case "Anulado": return '<span class="badge bg-danger">Anulado</span>';
                        default: return data;
                    }
                }
            },
            {
                data: null,
                title: "Acciones",
                orderable: false,
                render: function (data, type, row) {
                    return `
                        <div class= "btn-group" role="group">
                        <button class="btn btn-primary btn-sm ver-detalle" data-cod="${row.cod_entrega}" data-empresa="${row.cod_empresa}"> Mostrar </button>
                        <button class="btn btn-danger btn-sm anular-entrega" data-cod="${row.cod_entrega}" data-empresa="${row.cod_empresa}">Anular</button>
                        </div>
                    `;
                }
            }
        ],
        responsive: true,
        pageLength: 10
    });

    //Funcion para anular la entrega
    function anularEntrega(cod_entrega, cod_empresa) {
        const usuario_x = getUsuarioIdFromToken();
        if (!usuario_x) {
            Swal.fire({
                title: "Error",
                text: "No se encontró usuario, inicia sesión nuevamente",
                icon: "error",
                confirmButtonText: "OK"
            }).then(() => {
                window.location.href = "/";
            });
            return;
        }

        const data = {
            cod_entrega: cod_entrega,
            cod_empresa: cod_empresa,
            usuario_x: usuario_x
        };

        $.ajax({
            url: '/entregas/anular',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message || "Entrega anulada correctamente",
                    icon: "success",
                    confirmButtonText: "OK"
                }).then(() => {
                    table.ajax.reload(null, false); // recarga manteniendo la paginación
                });
            },
            error: function(error) {
                console.error("Error al anular entrega:", error);
                Swal.fire({
                    title: "Error",
                    text: error.responseJSON?.message || "Error al anular la entrega",
                    icon: "error",
                    confirmButtonText: "OK"
                });
            }
});
    }

    // Botón filtrar
    $('#btnFiltrar').click(function() {
        table.ajax.reload();
    });

    // Botón Mostrar
    $('#tablaEntregas').on('click', '.ver-detalle', function() {
        const codEntrega = $(this).data('cod');
        const codEmpresa = $(this).data('empresa');
        window.location.href = `/verentregacompleta.html?cod_entrega=${codEntrega}&cod_empresa=${codEmpresa}`;
    });

    // Acción al hacer click en "Anular"
$('#tablaEntregas').on('click', '.anular-entrega', function () {
    const codEntrega = $(this).data('cod');
    const codEmpresa = $(this).data('empresa');

    Swal.fire({
        title: '¿Anular entrega?',
        text: "Esta acción no se puede deshacer",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, anular',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            anularEntrega(codEntrega, codEmpresa); // tu función ya lista
        }
    });
});



});


