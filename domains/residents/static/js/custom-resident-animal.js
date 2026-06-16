
// Inicio do script
(function($) {
    'use strict';

    if (!$) {
        console.error("django.jQuery não encontrado.");
        return;
    }

    $(document).ready(function() {
        // Faz com que o link da foto abra em nova aba
        $('.field-photo a').attr('target', '_blank');

    });

})(window.django ? django.jQuery : jQuery);
//# Final do script