(function($) {
    'use strict';

    $(document).ready(function() {
        console.log('O arquivo custom-parameters-types-visitor-restrictions.js está carregado');

        if ($().jquery) {
            console.log('O jQuery está carregado corretamente');
        } else {
            console.log('O jQuery não está sendo carregado corretamente');
        }
        
    });
})(window.django ? django.jQuery : jQuery);
