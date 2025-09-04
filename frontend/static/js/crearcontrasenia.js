$(document).ready(function () {

  if (validar_permisos(5) !== 'S') {
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

  let codContrasenia = null;
  let detalles = [];

  cargarEmpresas();
  cargarMonedas();

  function cargarEmpresas() {
    $.get("/contrasenias/empresas", function (data) {
      const $empresa = $("#cod_empresa");
      $empresa.empty().append('<option value="">Seleccione Empresa</option>');
      data.forEach(emp => {
        $empresa.append(`<option value="${emp.cod_empresa}">${emp.nombre}</option>`);
      });
    });
  }

  function cargarMonedas() {
    $.get("/contrasenias/monedas", function (data) {
      const select = $("#cod_moneda");
      select.empty().append('<option value="">Selecciona moneda</option>');
      data.forEach(m => {
        select.append(`<option value="${m.cod_moneda}">${m.abreviatura}</option>`);
      });
    });
  }

  $("#cod_empresa").on("change", function () {
    $("#proveedor_nombre").val("");
    $("#cod_proveedor").val("");
  });

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

  // Agregar detalle a lista y tabla
$("#btnGuardarDetalle").click(function () {
    const detalle = {
      cod_contrasenia: codContrasenia,
      num_factura: $("#num_factura").val(),
      fecha_factura: $("#fecha_factura").val(), 
      cod_moneda: $("#cod_moneda").val(),
      monto: parseFloat($("#monto").val()),
      retension_iva: $("#retension_iva").is(":checked"),
      retension_isr: $("#retension_isr").is(":checked"),
      numero_retension_iva: $("#numero_retension_iva").val(),
      numero_retension_isr: $("#numero_retension_isr").val()
    };

    if (!detalle.num_factura || !detalle.cod_moneda || !detalle.fecha_factura || isNaN(detalle.monto)) {
      Swal.fire("Campos incompletos", "Completa todos los campos obligatorios en detalle.", "warning");
      return;
    }

    const facturaExiste = detalles.some(d => d.num_factura === detalle.num_factura);
    if (facturaExiste) {
      Swal.fire("Duplicado", "Ya existe una factura con ese número en la lista.", "error");
      return;
    }

    detalles.push(detalle);
    agregarDetalleATabla(detalle);
    $('#formulario-detalle')[0].reset();
});
function agregarDetalleATabla(detalle) {
    const fila = `
      <tr>
        <td>${detalle.num_factura}</td>
        <td>${detalle.fecha_factura}</td> 
        <td>${detalle.cod_moneda}</td>
        <td>${detalle.monto.toFixed(2)}</td>
        <td>${detalle.retension_iva ? 'Sí' : 'No'}</td>
        <td>${detalle.retension_isr ? 'Sí' : 'No'}</td>
        <td>${detalle.numero_retension_iva || '-'}</td>
        <td>${detalle.numero_retension_isr || '-'}</td>
        <td><button class="btn btn-danger btn-sm btn-eliminar">Eliminar</button></td>
      </tr>
    `;

    $("#tabla-detalles tbody").append(fila);

    $("#tabla-detalles tbody tr:last .btn-eliminar").click(function () {
      const index = $(this).closest("tr").index();
      detalles.splice(index, 1);
      $(this).closest("tr").remove();
    });
}

  // Enviar encabezado + detalles
  $("#btnEnviarTodo").click(function () {
    const $btn = $(this);

    if (detalles.length === 0) {
      Swal.fire("Sin detalles", "No hay detalles para enviar.", "warning");
      return;
    }

    const dataEncabezado = {
      fecha_contrasenia: $("#fecha_contrasenia").val(),
      cod_empresa: $("#cod_empresa").val(),
      cod_proveedor: $("#cod_proveedor").val()
    };

    if (!dataEncabezado.cod_empresa || !dataEncabezado.cod_proveedor || !dataEncabezado.fecha_contrasenia) {
      Swal.fire("Campos incompletos", "Completa todos los campos del encabezado.", "warning");
      return;
    }

    $btn.prop('disabled', true).text('Enviando...');

    $.ajax({
      url: "/contrasenias/crear-contrasenia",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(dataEncabezado),
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      success: function (response) {
        codContrasenia = response.cod_contrasenia;
        if (!codContrasenia) {
          Swal.fire("Error", "No se recibió código de contraseña del servidor.", "error");
          $btn.prop('disabled', false).text('Enviar Todo');
          return;
        }

        $('#cod_contrasenia').val(codContrasenia);

        let errores = 0;

        function enviarDetalleIndice(i) {
          if (i >= detalles.length) {
            $btn.prop('disabled', false).text('Enviar Todo');
            if (errores === 0) {
              Swal.fire("¡Éxito!", "Encabezado y detalles guardados exitosamente.", "success");
              detalles = [];
              $("#tabla-detalles tbody").empty();
              $("#formulario-contrasenia")[0].reset();
              $("#formulario-detalle")[0].reset();
              codContrasenia = null;
            } else {
              Swal.fire("Atención", `Proceso completado con ${errores} error(es).`, "warning");
            }
            return;
          }

          const det = detalles[i];
          const payload = {
              cod_contrasenia: codContrasenia,
              cod_empresa: parseInt(dataEncabezado.cod_empresa),
              num_factura: parseInt(det.num_factura),
              fecha_factura: det.fecha_factura,
              cod_moneda: det.cod_moneda,
              monto: parseFloat(det.monto),
              retension_iva: det.retension_iva ? 'S' : 'N',
              retension_isr: det.retension_isr ? 'S' : 'N',
              numero_retension_iva: det.numero_retension_iva ? parseInt(det.numero_retension_iva) : null,
              numero_retension_isr: det.numero_retension_isr ? parseInt(det.numero_retension_isr) : null
          };

          if (!payload.num_factura || !payload.cod_moneda || isNaN(payload.monto) || !payload.cod_empresa) {
            console.error('Detalle inválido, se omite:', payload);
            errores++;
            enviarDetalleIndice(i + 1);
            return;
          }

          $.ajax({
            url: "/contrasenias/detalle",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(payload),
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
            success: function () {
              enviarDetalleIndice(i + 1);
            },
            error: function (xhr) {
              let mensaje = "Error desconocido";
              if (xhr.responseJSON?.detail) {
                mensaje = xhr.responseJSON.detail;
              } else if (xhr.responseText) {
                mensaje = xhr.responseText;
              }
              Swal.fire("Error en detalle", mensaje, "error");
              errores++;
              enviarDetalleIndice(i + 1);
            }
          });
        }

        enviarDetalleIndice(0);
      },
      error: function (xhr) {
        Swal.fire("Error", "Error al guardar el encabezado: " + xhr.responseText, "error");
        $btn.prop('disabled', false).text('Enviar Todo');
      }
    });

  });
    const hoy = new Date().toISOString().split('T')[0];
  $("#fecha_contrasenia").val(hoy);


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










