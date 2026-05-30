(function($){
    $(function(){
        console.log('O arquivo custom-admin-resident.js está carregado');

        BrasilCondoUtils.applyMask('.mask-email', 'email');
        BrasilCondoUtils.applyMask('.mask-phone', 'phone');
        BrasilCondoUtils.applyMask('.mask-date-of-birth', 'date');
        BrasilCondoUtils.applyMask('.mask-cpf', 'cpf');

        // Faz com que o link da foto abra em nova aba
        $('.field-photo a').attr('target', '_blank');
        
        // Faz com que o link do arquivo da certidão abra em nova aba
        $('.field-certificate_file a').attr('target', '_blank');
    });
})(django.jQuery);
