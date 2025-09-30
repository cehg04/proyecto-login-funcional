$(document).ready(function () {
    
    if (validar_permisos(14) !== 'S') {
    Swal.fire({
      title: "Acceso denegado",
      text: "No tienes permiso para ver reportes de contraseñas",
      icon: "warning",
      confirmButtonText: "OK"
    }).then(() => {
      window.location.href = "inicio.html";
    });
    return;
  }

    let dataTable;
    const $tabla = $("#tablaReportesContrasenias");

    // Fecha actual en formato yyyy-mm-dd
    const hoy = new Date().toISOString().split("T")[0];
    $("#fechaInicio").val(hoy);
    $("#fechaFin").val(hoy);

    // Cargar empresas en el combo
    function cargarEmpresas() {
        $.ajax({
            url: "/reportes/empresas-con-contrasenias",
            type: "GET",
            success: function (data) {
                console.log("Empresas cargadas:", data);
                let select = $("#selectEmpresas");
                select.empty();
                select.append('<option value="">Todas las empresas</option>');
                data.forEach(emp => {
                    select.append(`<option value="${emp.cod_empresa}">${emp.nombre_empresa}</option>`);
                });
            },
            error: function (xhr) {
                console.error("Error cargando empresas:", xhr);
                Swal.fire("Error", "No se pudieron cargar las empresas", "error");
            }
        });
    }

    cargarEmpresas();

    // Cargar DataTable con filtros
    function cargarTabla(fecha_inicio = hoy, fecha_fin = hoy, cod_empresa = "") {        
        if (dataTable) {
            dataTable.destroy();
            $tabla.find("tbody").empty();
        }

        dataTable = $tabla.DataTable({
            serverSide: false,
            ajax: {
                url: "/reportes/contrasenias-todas",
                type: "GET",
                dataSrc: "",
                data: function(d) {
                    return {
                        fecha_inicio: fecha_inicio,
                        fecha_fin: fecha_fin,
                        cod_empresa: cod_empresa
                    };
                },
                error: function(xhr, error, thrown) {
                    console.error("Error AJAX completo:", xhr);
                    Swal.fire("Error", "No se pudieron cargar los datos", "error");
                }
            },
            columns: [
                { data: "cod_empresa", visible: false },
                { data: "num_contrasenia", title: "No. Contraseña" },
                {
                    data: "fecha_creacion",
                    title: "Fecha Creación",
                    render: function(data) {
                        if (!data) return "";
                        const [anio, mes, dia] = data.split("-");
                        return `${dia}/${mes}/${anio}`; 
                    }
                },
                { data: "num_factura", title: "No. Factura" },
                { data: "monto", title: "Monto" },
                { 
                    data: "estado", 
                    title: "Estado",
                    render: function(data) {
                        if (data === "Entregado") return `<span class="badge bg-success">${data}</span>`;
                        if (data === "Pendiente") return `<span class="badge bg-warning text-dark">${data}</span>`;
                        return `<span class="badge bg-secondary">${data}</span>`;
                    }
                }
            ],
            responsive: true,
            dom: 'Bfrtip', // mostrar botones arriba de la tabla
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: 'Exportar a Excel',
                    title: 'Reporte_Contraseñas',
                    exportOptions: {
                        columns: ':visible' // exporta solo columnas visibles
                    }
                }
            ]
        });

        // Debug más detallado
        dataTable.on('xhr.dt', function (e, settings, json, xhr) {
            console.log('Datos recibidos:', json);
        });

        dataTable.on('error.dt', function (e, settings, techNote, message) {
            console.error('Error DataTables:', message);
        });
    }

    // Inicializar tabla con hoy y todas las empresas
    cargarTabla();

    // Botón Filtrar
    $("#btnFiltrar").click(function () {
        const fecha_inicio = $("#fechaInicio").val();
        const fecha_fin = $("#fechaFin").val();
        const cod_empresa = $("#selectEmpresas").val();

        if (fecha_inicio && fecha_fin && fecha_inicio > fecha_fin) {
            Swal.fire("Error", "La fecha de inicio no puede ser mayor que la fecha fin", "error");
            return;
        }

        cargarTabla(fecha_inicio, fecha_fin, cod_empresa);
    });
});






