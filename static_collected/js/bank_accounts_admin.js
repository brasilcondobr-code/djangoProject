(function($){
    $(document).ready(function(){
        BrasilCondoUtils.applyMask('.mask-agency', 'agency');
        BrasilCondoUtils.applyMask('.mask-account-number', 'account_number');
        BrasilCondoUtils.applyMask('.mask-account-digit', 'account_digit');
        BrasilCondoUtils.applyMask('.mask-currency', 'decimal');

        $('.mask-agency').on('input', function(){
            var value = $(this).val().replace(/\D/g, '');
            if (value.length > 6) value = value.slice(0, 6);
            $(this).val(value);
        });

        $('.mask-account-number').on('input', function(){
            var value = $(this).val().replace(/\D/g, '');
            if (value.length > 10) value = value.slice(0, 10);
            $(this).val(value);
        });

        $('.mask-account-digit').on('input', function(){
            var value = $(this).val().replace(/[^0-9]/g, '');
            if (value.length > 3) value = value.slice(0, 3);
            $(this).val(value);
        });
    });
})(django.jQuery);
