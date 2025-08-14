$(document).ready(function () {
    
    // Validar permisos 
    if (validar_permisos(4) !== 'S') {
        alert("No tienes permiso para ver Contrasenias.");
        window.location.href = "inicio.html"; 
        return;
    }
    if (validar_permisos(5) !== 'S') {
        $("#btnCrearContrasenia").hide();
    }

    $('#filtrosContainer').append(`
        <div class="row mb-3">
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
                    <!-- Las opciones se llenarán dinámicamente -->
                </select>
            </div>
            <div class="col-md-3 d-flex align-items-end">
                <button id="btnFiltrar" class="btn btn-primary">Buscar</button>
            </div>
        </div>
    `);
    
    // Setear fecha actual por defecto
    const today = new Date().toISOString().split('T')[0];
    $('#fechaInput').val(today);
    
    // Cargar empresas para el select 
    cargarEmpresas();
    
    function cargarEmpresas() {
        $.get('/contrasenias/empresas', function(data) {
            const select = $('#empresaSelect');
            data.forEach(empresa => {
                select.append(`<option value="${empresa.cod_empresa}">${empresa.nombre}</option>`);
            });
        });
    }

    // Inicializamos DataTable
        let table = $('#tablaContrasenias').DataTable({
        ajax: {
            url: '/contrasenias/ver-encabezados',
            data: function(d) {
                return {
                    cod_contrasenia: $('#filtroCodContrasenia').val(),
                    cod_empresa: $('#empresaSelect').val(),
                    fecha_inicio: $('#fechaInicio').val(),
                    fecha_fin: $('#fechaFin').val() || null
                };
            },
            dataSrc: ''
        },
        columns: [
            { data: 'num_contrasenia', title: 'N° Contraseña' },
            { data: 'fecha_contrasenia', title: 'Fecha Contraseña' },
            { data: 'empresa_nombre', title: 'Empresa' },
            { data: 'proveedor_nombre', title: 'Proveedor' },
            { data: 'estado', title: 'Estado' },
            {
                data: null,
                title: 'Acciones',
                orderable: false,
                render: function(data, type, row) {
                    return `
                        <button class="btn btn-success btn-completa" data-cod="${row.cod_contrasenia}" data-empresa="${row.cod_empresa}">Mostrar</button>
                        <button class="btn btn-danger btn-anular" data-cod="${row.cod_contrasenia}" data-empresa="${row.cod_empresa}">Anular</button>
                    `;
                }
            }
        ],
    });

       // Botón para aplicar filtros
    $('#btnFiltrar').click(function() {
        table.ajax.reload();
    });

    // Botón Mostrar 
    $('#tablaContrasenias').on('click', '.btn-completa', function() {
        const codContrasenia = $(this).data('cod');
        const codEmpresa = $(this).data('empresa');
        window.location.href = `/contrasenia_completa.html?cod_contrasenia=${codContrasenia}&cod_empresa=${codEmpresa}`;
    });

    


});


