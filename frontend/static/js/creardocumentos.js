$(document).ready(function () {

    if (validar_permisos(14) !== 'S') {
    Swal.fire({
      title: "Acceso denegado",
      text: "No tienes permiso para Crear Contraseñas",
      icon: "warning",
      confirmButtonText: "OK"
    }).then(() => {
      window.location.href = "inicio.html";
    });
    return;
  }

    // === Cargar combos al iniciar ===
    cargarEmpresas();
    cargarTipos();
    cargarMonedas();


    // Guardar documento
    $("#btnGuardarDocumento").click(function () {

        const documento = {
            cod_empresa: $("#cod_empresa").val(),
            cod_tipo_documento: $("#cod_tipo_documento").val(),
            cod_proveedor: $("#cod_proveedor").val() || null,
            nombre_solicitud: $("#nombre_solicitud").val(),
            numero_documento: $("#numero_documento").val() || null,
            cod_moneda: $("#cod_moneda").val(),
            monto: parseFloat($("#monto").val()),
            observaciones: $("#observaciones").val(),
            estado: "P",
            retension_iva: $("#retension_iva").is(":checked") ? "S" : "N",
            retension_isr: $("#retension_isr").is(":checked") ? "S" : "N",
            numero_retension_iva: $("#numero_retension_iva").val() ? parseInt($("#numero_retension_iva").val()) : null,
            numero_retension_isr: $("#numero_retension_isr").val() ? parseInt($("#numero_retension_isr").val()) : null,

        };

        // Validaciones simples
        if (!documento.cod_empresa || !documento.cod_tipo_documento || !documento.cod_moneda || isNaN(documento.monto)) {
            Swal.fire("Campos incompletos", "Llena todos los campos obligatorios.", "warning");
            return;
        }

        $.ajax({
            url: "/documentos/crear",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(documento),
            success: function (response) {
                Swal.fire("Éxito", response.mensaje, "success");
                $("#formDocumento")[0].reset();

            },
            error: function (xhr) {
                Swal.fire("Error", xhr.responseJSON?.detail || "Error al guardar documento", "error");
            }
        });
    });
      // Inicialmente deshabilitar los inputs
      $("#numero_retension_iva").prop("disabled", true);
      $("#numero_retension_isr").prop("disabled", true);

      // Toggle para IVA
      $("#retension_iva").change(function () {
        if ($(this).is(":checked")) {
          $("#numero_retension_iva").prop("disabled", false);
        } else {
          $("#numero_retension_iva").prop("disabled", true).val("");
        }
      });

      // Toggle para ISR
      $("#retension_isr").change(function () {
        if ($(this).is(":checked")) {
          $("#numero_retension_isr").prop("disabled", false);
        } else {
          $("#numero_retension_isr").prop("disabled", true).val("");
        }
      });

});



// funcion para cargar las empresas
  function cargarEmpresas() {
    $.get("/contrasenias/empresas", function (data) {
      const $empresa = $("#cod_empresa");
      $empresa.empty().append('<option value="">Seleccione Empresa</option>');
      data.forEach(emp => {
        $empresa.append(`<option value="${emp.cod_empresa}">${emp.nombre}</option>`);
      });
    });
  }

  // funcion para cargar las monedas
    function cargarMonedas() {
    $.get("/contrasenias/monedas", function (data) {
      const select = $("#cod_moneda");
      select.empty().append('<option value="">Selecciona moneda</option>');
      data.forEach(m => {
        select.append(`<option value="${m.cod_moneda}">${m.abreviatura}</option>`);
      });
    });
  }

// funcion para cargar los tipos de documentos
function cargarTipos() {
    $.get("/documentos/tipos", function (data) {
        let opciones = '<option value="">Seleccione un tipo de documento</option>';
        data.forEach(t => {
            opciones += `<option value="${t.cod_tipo_documento}">${t.nombre_documento}</option>`;
        });
        $("#cod_tipo_documento").html(opciones);
    });
}

// Cuando cambie la empresa, cargar proveedores de esa empresa
    $("#cod_empresa").change(function () {
        const codEmpresa = $(this).val();
        if (codEmpresa) {
            cargarProveedores(codEmpresa);
        } else {
            $("#cod_proveedor").empty().append('<option value="">Seleccione un proveedor</option>');
        }
    });

// funcion para cargar los proveedores de la empresa seleccionada
  $("#proveedor_nombre").autocomplete({
    source: function (request, response) {
      const cod_empresa = $("#cod_empresa").val();
      if (!cod_empresa) {
        response([]);
        return;
      }
      $.ajax({
        url: `/contrasenias/proveedores-autocomplete`,
        dataType: "json",
        data: { q: request.term, cod_empresa: cod_empresa },
        success: function (data) {
          response(data.map(prov => ({
            label: `${prov.nit} - ${prov.cod_proveedor} - ${prov.nombre}`,
            value: prov.nombre,
            cod_proveedor: prov.cod_proveedor
          })));
        }
      });
    },
    minLength: 2,
    select: function (event, ui) {
      $("#cod_proveedor").val(ui.item.cod_proveedor);
    },
    focus: function (event, ui) {
      $("#proveedor_nombre").val(ui.item.label);
      return false;
    }
  });

  $("#proveedor_nombre").on("input", function () {
    $("#cod_proveedor").val("");
  });

