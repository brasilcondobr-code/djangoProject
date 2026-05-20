(function($){
    function maskCPF(v){
        v = v.replace(/\D/g, '');
        if (v.length <= 3) return v;
        if (v.length <= 6) return v.replace(/(\d{3})(\d+)/, '$1.$2');
        if (v.length <= 9) return v.replace(/(\d{3})(\d{3})(\d+)/, '$1.$2.$3');
        return v.replace(/(\d{3})(\d{3})(\d{3})(\d{3})/, '$1.$2.$3-$4').slice(0, 14);
    }

    function maskPhone(v){
        v = v.replace(/\D/g, '');
        if (v.length <= 2) return v;
        if (v.length <= 6) return v.replace(/(\d{2})(\d+)/, '($1) $2');
        if (v.length <= 10) return v.replace(/(\d{2})(\d{4})(\d+)/, '($1) $2-$3');
        return v.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3').slice(0, 15);
    }

    function maskDecimal(v){
        v = v.replace(/\D/g, '');
        if (v.length === 0) return '';
        var amount = (parseInt(v) / 100).toFixed(2).replace(".", ",");
        amount = amount.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        return amount;
    }

    $(document).ready(function(){
        console.log('O arquivo custom-administrative-bank.js está carregado');

        $('.mask-compe').on('input', function(){
            var value = $(this).val().replace(/[^0-9]/g, '').slice(0, 4);
            $(this).val(value);
        });

        $('.mask-currency').on('input', function(){
            $(this).val(maskDecimal($(this).val()));
        });

        $('.mask-currency').each(function() {
            $(this).val(maskDecimal($(this).val()));
        });

        $('.mask-cpf-drawn').on('input', function(){
            $(this).val(maskCPF($(this).val()));
        });

        $('.mask-cpf-drawn').each(function() {
            $(this).val(maskCPF($(this).val()));
        });

        $('.mask-phone').on('input', function(){
            $(this).val(maskPhone($(this).val()));
        });

        $('.mask-phone').each(function() {
            $(this).val(maskPhone($(this).val()));
        });
    });
})(django.jQuery);



