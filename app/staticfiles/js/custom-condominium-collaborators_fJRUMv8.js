(function($){
    $(document).ready(function(){
        BrasilCondoUtils.applyMask('.mask-cpf', 'cpf');
        BrasilCondoUtils.applyMask('.mask-email', 'email');
        BrasilCondoUtils.applyMask('.mask-phone', 'phone');

        // Faz com que o link da foto abra em nova aba
        $('.field-photo a').attr('target', '_blank');
        
        // Faz com que o link do arquivo da certidão abra em nova aba
        $('.field-certificate_file a').attr('target', '_blank');
    });
})(django.jQuery);
