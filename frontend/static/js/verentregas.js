$(document).ready(function () {

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
                        <button class="btn btn-info btn-sm ver-detalle" 
                                data-cod="${row.cod_entrega}" 
                                data-empresa="${row.cod_empresa}">
                            Ver
                        </button>
                        <button class="btn btn-danger btn-sm anular-entrega" 
                                data-cod="${row.cod_entrega}" 
                                data-empresa="${row.cod_empresa}">
                            Anular
                        </button>
                    `;
                }
            }
        ],
        responsive: true,
        pageLength: 10
    });

    // Botón filtrar
    $('#btnFiltrar').click(function() {
        table.ajax.reload();
    });
});


