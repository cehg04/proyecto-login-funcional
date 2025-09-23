$(document).ready(function () {
    let dataTable;
    const $tabla = $("#tablaReportes");

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
                let select = $("#selectEmpresas");
                select.empty();
                select.append('<option value="">Todas las empresas</option>');
                data.forEach(emp => {
                    select.append(`<option value="${emp.cod_empresa}">${emp.nombre_empresa}</option>`);
                });
            },
            error: function (xhr) {
                Swal.fire("Error", "No se pudieron cargar las empresas", "error");
                console.error(xhr.responseText);
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
                url: "/reportes/documentos-todos",
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
                    console.error("Error AJAX:", xhr, error, thrown);
                    Swal.fire("Error", "No se pudieron cargar los datos", "error");
                }
            },
            columns: [
                { data: "cod_empresa", visible: false },
                { data: "cod_documento", title: "Cod Documento" },
                {
                    data: "fecha_creacion",
                    title: "Fecha Creación",
                    render: function(data) {
                        if (!data) return "";
                        const [anio, mes, dia] = data.split("-");
                        return `${dia}/${mes}/${anio}`;
                    }
                },
                { data: "tipo_documento", title: "Tipo Documento" },
                { data: "numero_documento", title: "No. Documento" },
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
            dom: 'Bfrtip',
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: 'Exportar a Excel',
                    title: 'Reporte_Documentos',
                    exportOptions: {
                        columns: ':visible'
                    }
                }
            ]
        });

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


