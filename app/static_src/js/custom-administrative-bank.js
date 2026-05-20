(function($){
    $(document).ready(function(){
        console.log('O arquivo custom-administrative-bank.js está carregado');

        // Custom logic for compe (specific length and digit only)
        $('.mask-compe').on('input', function(){
            var value = $(this).val().replace(/[^0-9]/g, '').slice(0, 4);
            $(this).val(value);
        });

        // Using centralized masks
        BrasilCondoUtils.applyMask('.mask-currency', 'decimal');
        BrasilCondoUtils.applyMask('.mask-cpf-drawn', 'cpf');
        BrasilCondoUtils.applyMask('.mask-phone', 'phone');
    });
})(django.jQuery);




