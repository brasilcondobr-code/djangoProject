(function($){
    function updateIdentification(){
        var tower = django.jQuery('.mask-tower').val ? django.jQuery('.mask-tower').val().trim() : '';
        var unit  = django.jQuery('.mask-unit-number').val ? django.jQuery('.mask-unit-number').val().trim() : '';
        var combined = (tower && unit) ? (tower + ' - ' + unit) : (tower || unit);
        django.jQuery('#id_identification').val(combined);
    }

    django.jQuery(function(){
        // Atualiza quando qualquer um dos campos mudar
        django.jQuery('.mask-tower').on('input', updateIdentification);
        django.jQuery('.mask-unit-number').on('input', updateIdentification);

        updateIdentification();

        django.jQuery('.mask-sale-price, .mask-rent-price').on('input', function(){
            var value = django.jQuery(this).val().replace(/\D/g, '');
            if(value){
                value = (parseInt(value) / 100).toFixed(2);
                django.jQuery(this).val(value);
            } else {
                django.jQuery(this).val('');
            }
        });
     });
     
})(jQuery);