$(function () {
    if (validar_permisos(1) !== 'S') {
        Swal.fire({
            title: "Acceso denegado",
            text: "No tines permiso para ver Usuarios",
            icon: "warning",
            confirmButtonText: "OK"
        }).then(() => {
            window.location.href = "inicio.html";
        });
        return;
    }

    // Ocultar botón "Crear Usuario" si no tiene permiso 2
    if (validar_permisos(2) !== 'S') {
        $("#btnCrearUsuario").hide();
    }

    if (validar_permisos(1) === 'S') {
        function cargarUsuarios() {
            $.get("/api/usuarios", function (usuarios) {
                const tbody = $("#tablaUsuarios tbody");
                tbody.empty();

                usuarios.forEach(u => {
                    const estadoTexto = u.estado === "A" ? "Activo" : "Inactivo";
                    const estadoBadgeClass = u.estado === "A" 
                    ? "bg-success text-white"   // verde
                    : "bg-danger text-white";   // rojo
                    const btnEditar = validar_permisos(3) === 'S'
                        ? `<a href="editar.html?cod_usuario=${u.cod_usuario}" class="btn btn-primary btn-sm">Editar</a>`
                        : "";
                    tbody.append(`
                        <tr data-id="${u.cod_usuario}">
                            <td>${u.cod_usuario}</td>
                            <td>${u.nombre}</td>
                            <td>${u.usuario}</td>
                            <td>${u.correo ?? ""}</td>
                            <td><span class="badge ${estadoBadgeClass}">${estadoTexto}</span></td>
                            <td>${btnEditar}</td>
                        </tr>
                    `);
                });

                // Inicializar DataTable después de llenar la tabla
                if ($.fn.DataTable.isDataTable('#tablaUsuarios')) {
                    $('#tablaUsuarios').DataTable().destroy(); // Destruye si ya existe
                }

                $('#tablaUsuarios').DataTable({
                    responsive: true,
                    language: {
                        url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
                    },
                    pageLength: 10,
                    lengthMenu: [5, 10, 25, 50],
                    columnDefs: [
                        { orderable: false, targets: 5 } // Columna de acciones sin orden
                    ]
                });
            }).fail(() => alert("Error al cargar usuarios"));
        }

        cargarUsuarios();
    }
});



