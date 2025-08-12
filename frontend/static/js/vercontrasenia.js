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
            { data: 'fecha_creacion', title: 'Fecha Creación' },
            { data: 'empresa_nombre', title: 'Empresa' },
            { data: 'proveedor_nombre', title: 'Proveedor' },
            {
                data: null,
                title: 'Acciones',
                orderable: false,
                render: function(data, type, row) {
                    return `
                        <button class="btn btn-info btn-mostrar" data-cod="${row.cod_contrasenia}" data-empresa="${row.cod_empresa}">Mostrar</button>
                        <button class="btn btn-danger btn-anular" data-cod="${row.cod_contrasenia}" data-empresa="${row.cod_empresa}">Anular</button>
                    `;
                }
            }
        ],
    });
});


