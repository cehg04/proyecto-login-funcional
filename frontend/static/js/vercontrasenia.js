$(document).ready(function () {

    function getUsuarioIdFromToken() {
        const token = localStorage.getItem('token');
        if (!token) return null;

        try {
            const payload = token.split('.')[1];
            const decoded = JSON.parse(atob(payload));
            return decoded.cod_usuario; // usuario_x
        } catch (e) {
            console.error("Error al decodificar token:", e);
            return null;
        }
    }
 
    if (validar_permisos(4) !== 'S') {
                Swal.fire({
            title: "Acceso denegado",
            text: "No tines permiso para ver Contraseñas",
            icon: "warning",
            confirmButtonText: "OK"
        }).then(() => {
            window.location.href = "inicio.html";
        });
        return;
    }
    if (validar_permisos(5) !== 'S') {
        $("#btnCrearContrasenia").hide();
    }

    $('#filtrosContainer').append(`
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

    const today = new Date().toISOString().split('T')[0];
    $('#fechaInicio').val(today);

    const today1 = new Date().toISOString().split('T')[0];
    $('#fechaFin').val(today);

    function cargarEmpresas() {
        $.get('/contrasenias/empresas', function(data) {
            const select = $('#empresaSelect');
            data.forEach(empresa => {
                select.append(`<option value="${empresa.cod_empresa}">${empresa.nombre}</option>`);
            });
        });
    }
    cargarEmpresas();

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
            {
            data: 'fecha_contrasenia',
            title: 'Fecha Contraseña',
            render: function(d) {
                if (!d) return '';
                let fecha = d.split(' ')[0];
                const partes = fecha.split('-');
                if (partes.length === 3) {
                    return `${partes[2]}/${partes[1]}/${partes[0]}`;
                }
                return fecha;
            }
        },  
            { data: 'empresa_nombre', title: 'Empresa' },
            { data: 'proveedor_nombre', title: 'Proveedor' },
            { 
                data: 'estado', 
                title: 'Estado',
                render: function(data, type, row) {
                    let badgeClass = '';
                    if (data === 'Realizado') badgeClass = 'bg-success text-white'; 
                    else if (data === 'Anulado') badgeClass = 'bg-danger text-white';
                    else badgeClass = 'bg-secondary text-white';

                    return `<span class="badge ${badgeClass}">${data}</span>`;
                }                
            },
            {
                data: null,
                title: 'Acciones',
                orderable: false,
                render: function(data, type, row) {
                    return `
                        <div class="btn-group" role="group">
                            <button class="btn btn-primary btn-completa" data-cod="${row.cod_contrasenia}" data-empresa="${row.cod_empresa}">Mostrar</button>
                            <button class="btn btn-danger btn-anular" data-cod="${row.cod_contrasenia}" data-empresa="${row.cod_empresa}">Anular</button>
                            <button class="btn btn-warning btn-imprimir" data-cod="${row.cod_contrasenia}" data-empresa="${row.cod_empresa}">Imprimir</button>
                        </div>
                    `;
                    
                }
            }
        ],
        language: {
            emptyTable: "No hay datos disponibles"
        } 
    });

    table.on('draw', function () {
        if (validar_permisos(6) !== 'S') {
            $(".btn-anular").remove();
        }
    });

    function anularContrasenia(cod_contrasenia, cod_empresa, comentario) {
        const usuario_x = getUsuarioIdFromToken();
        if (!usuario_x) {
            alert("No se encontró el usuario. Por favor, inicia sesión de nuevo.");
            window.location.href = "/login.html";
            return;
        }

        const data = {
            cod_contrasenia: cod_contrasenia,
            cod_empresa: cod_empresa,
            usuario_x: usuario_x,
            comentario: comentario || null
        };

        $.ajax({
            url: '/contrasenias/anular',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
            Swal.fire({
            title: "¡Éxito!",
            text: response.message || "Contraseña anulada correctamente",
            icon: "success",
            confirmButtonText: "OK"
        }).then(() => {
                table.ajax.reload(null, false);
                  });
          
        },
        error: function(error) {
            Swal.fire({
                title: "Error",
                text: error.responseJSON?.message || "Error al anular la contraseña",
                icon: "error",
                confirmButtonText: "OK"
            });
        }

});
    }

    $('#btnFiltrar').click(function() {
        table.ajax.reload();
    });

    $('#tablaContrasenias').on('click', '.btn-completa', function() {
        const codContrasenia = $(this).data('cod');
        const codEmpresa = $(this).data('empresa');
        window.location.href = `/contrasenia_completa.html?cod_contrasenia=${codContrasenia}&cod_empresa=${codEmpresa}`;
    });

    $('#tablaContrasenias').on('click', '.btn-anular', function() {
        const codContrasenia = $(this).data('cod');
        const codEmpresa = $(this).data('empresa');

        $('#modalCodContrasenia').val(codContrasenia);
        $('#modalCodEmpresa').val(codEmpresa);
        $('#modalComentario').val('');

        const modal = new bootstrap.Modal(document.getElementById('modalAnularContrasenia'));
        modal.show();
    });

    $('#btnConfirmarAnular').click(function() {
        const codContrasenia = $('#modalCodContrasenia').val();
        const codEmpresa = $('#modalCodEmpresa').val();
        const comentario = $('#modalComentario').val();

        anularContrasenia(codContrasenia, codEmpresa, comentario);

        const modalEl = document.getElementById('modalAnularContrasenia');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();
    });

$('#tablaContrasenias').on('click', '.btn-imprimir', function() {
    let cod = $(this).data('cod');
    let empresa = $(this).data('empresa');
    window.open(`/contrasenias/imprimir-encabezado/${cod}/${empresa}`, '_blank');
});

});



