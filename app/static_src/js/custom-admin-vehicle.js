(function($){
    $(function(){
        console.log('O arquivo custom-admin-vehicle.js está carregado');

        if ($().jquery) {
            console.log('O jQuery está carregado corretamente');
        } else {
            console.log('O jQuery não está sendo carregado corretamente');
        }

        // Máscara para placa (letras maiúsculas + números)
        $('.mask-license-plate').on('input', function(){
            var input = $(this);
            var value = input.val();

            // Remove caracteres inválidos (mantém letras e números)
            value = value.replace(/[^a-zA-Z0-9]/g, '');

            // Converte para maiúsculas
            value = value.toUpperCase();

            input.val(value);
        });

        // Máscara para ano (apenas números, máximo 4 dígitos)
        $('.mask-year').on('input', function(){
            var input = $(this);
            var value = input.val().replace(/[^0-9]/g, '');

            if (value.length > 4) {
                value = value.slice(0, 4); // Limita a 4 caracteres
            }

            input.val(value);
        });

    });
})(jQuery);