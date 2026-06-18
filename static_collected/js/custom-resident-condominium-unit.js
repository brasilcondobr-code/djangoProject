(function($) {
    'use strict';

    function updateIdentification() {
        // Busca os elementos usando o jQuery do Django
        var $tower = $('.mask-tower');
        var $unit = $('.mask-unit-number');
        var $identification = $('#id_identification');

        // Pega o valor ou string vazia se não existir, então remove espaços
        var towerVal = ($tower.val() || "").trim();
        var unitVal = ($unit.val() || "").trim();

        // Lógica de combinação (Torre - Unidade)
        var combined = "";
        if (towerVal && unitVal) {
            combined = towerVal + ' - ' + unitVal;
        } else {
            combined = towerVal || unitVal; // Pega o que estiver preenchido
        }

        // Define o valor no campo de identificação
        $identification.val(combined);
    }

    $(document).ready(function() {
        // Seletores para os campos
        var $tower = $('.mask-tower');
        var $unit = $('.mask-unit-number');
        var $moneyFields = $('.mask-sale-price, .mask-rent-price, .mask-area-total');

        // Monitora digitação nos campos de Torre e Unidade
        $tower.on('input', updateIdentification);
        $unit.on('input', updateIdentification);

        // Executa uma vez ao carregar para garantir consistência
        updateIdentification();

        // Lógica para campos de preço (moeda)
        $moneyFields.on('input', function() {
            var value = $(this).val().replace(/\D/g, '');
            if (value) {
                value = (parseInt(value) / 100).toFixed(2);
                $(this).val(value);
            } else {
                $(this).val('');
            }
        });
    });

})(django.jQuery);
