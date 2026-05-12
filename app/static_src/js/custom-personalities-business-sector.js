(function($) {
    'use strict';

    $(document).ready(function() {

        console.log('O arquivo custom-personalities-business-sector.js está carregado');

        if ($().jquery) {
            console.log('O jQuery está carregado corretamente');
        } else {
            console.log('O jQuery não está sendo carregado corretamente');
        }

        $('.mask-description').on('input', function() {
            let value = $(this).val();
            value = value.replace(/\s+/g, ' ');
            value = value.replace(/^\s+/g, '');

            $(this).val(value);
        });

    });

})(window.django && window.django.jQuery || jQuery);