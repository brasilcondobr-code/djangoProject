(function($){
    'use strict';

    $(document).ready(function(){

        console.log('O arquivo custom-condominium-documentcondominium.js está carregado');    

        if ($().jquery) {
            console.log('jQuery está funcionando corretamente.');
        } else {
            console.log('O jQuery não está sendo carregado corretamente.');
        }

        // Faz com que o link da foto abra em nova aba
        django.jQuery('.field-file a').attr('target', '_blank');

    });
  
})(django.jQuery);