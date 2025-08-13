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

    // Inicializamos DataTable
    let table = $('#tablaContrasenias').DataTable({
        ajax: {
            url: '/contrasenias/ver-encabezados',
            data: function(d) {
                // Agregar filtros como parámetros
                d.cod_contrasenia = $('#filtroCodContrasenia').val();
                d.cod_empresa = $('#filtroCodEmpresa').val();
            },
            dataSrc: ''
        },
        columns: [
            { data: 'num_contrasenia', title: 'N° Contraseña' },
            { data: 'fecha_creacion', title: 'Fecha Creación' },
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
      $('#tablaContrasenias').on('click', '.btn-completa', function() {
        const codContrasenia = $(this).data('cod');
        const codEmpresa = $(this).data('empresa');

        window.location.href = `/contrasenia_completa.html?cod_contrasenia=${codContrasenia}&cod_empresa=${codEmpresa}`;
    });
});


