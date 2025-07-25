function validar_permisos (numero_opcion) {
        const token = localStorage.getItem('token');
        const decodifica_token = JSON.parse(atob(token.split('.')[1]));
        var indice = decodifica_token.permisos.findIndex(opcion => opcion.cod_opcion === numero_opcion);
        var respuesta = decodifica_token.permisos[indice].permiso;
        return respuesta;
}
