(function($){
    $(document).ready(function(){
        console.log('O arquivo custom-condominium-condominium.js está carregado');

        $('.mask-code').on('input', function(){
            $(this).val($(this).val().toUpperCase());
        });

        BrasilCondoUtils.applyMask('.mask-cnpj', 'cnpj');
    });
})(django.jQuery);
