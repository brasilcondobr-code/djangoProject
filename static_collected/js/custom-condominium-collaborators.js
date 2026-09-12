(function($){
    $(document).ready(function(){
        BrasilCondoUtils.applyMask('.mask-cpf', 'cpf');
        BrasilCondoUtils.applyMask('.mask-email', 'email');
        BrasilCondoUtils.applyMask('.mask-phone', 'phone');
        BrasilCondoUtils.applyMask('.mask-date', 'date');
        BrasilCondoUtils.applyMask('.mask-name', 'name');
        BrasilCondoUtils.applyMask('.mask-rg', 'rg');

        $('.field-photo a').attr('target', '_blank');
        $('.field-certificate_file a').attr('target', '_blank');
    });
})(django.jQuery);
