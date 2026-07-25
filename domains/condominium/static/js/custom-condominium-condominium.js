(function($){
    $(document).ready(function(){
        BrasilCondoUtils.applyMask('.mask-cnpj', 'cnpj');
        BrasilCondoUtils.applyMask('.mask-code', 'code');
        BrasilCondoUtils.applyMask('.mask-state-registration', 'state_registration');
        BrasilCondoUtils.applyMask('.mask-municipal', 'municipal');

        $('.mask-code').on('input', function(){
            $(this).val($(this).val().toUpperCase());
        });
    });
})(django.jQuery);
