(function($) {
    'use strict';

    $(document).ready(function() {
        var kindSelect = '#id_kind';
        
        if ($(kindSelect).length === 0) return;

        var allFields = [
            'name', 'trade_name', 'cpf_cnpj', 'rg_ie', 
            'municipal_registration', 'date_of_birth_opening', 
            'sex', 'email', 'phone', 'address', 'observations', 'is_active'
        ];

        var lastKindValue = null;

        function applyLogic() {
            var $field = $(kindSelect);
            var kind = $field.val();
            
            if (!kind) {
                var selectedText = $('.select2-selection__rendered').last().text() || "";
                if (selectedText.includes("Física")) kind = "PF";
                else if (selectedText.includes("Jurídica")) kind = "PJ";
            }

            if (kind === lastKindValue) return;
            lastKindValue = kind;

            $.each(allFields, function(i, f) {
                $('.field-' + f).closest('.form-group, .field-box').hide();
            });

            if (kind === 'PF') {
                showFields(['name', 'trade_name', 'cpf_cnpj', 'rg_ie', 'date_of_birth_opening', 'sex', 'email', 'phone', 'address', 'observations', 'is_active']);
                updateLabel('trade_name', 'Apelido');
                updateLabel('cpf_cnpj', 'Nro CPF');
                BrasilCondoUtils.applyMask('#id_cpf_cnpj', 'cpf');
            } 
            else if (kind === 'PJ') {
                showFields(['name', 'trade_name', 'cpf_cnpj', 'rg_ie', 'municipal_registration', 'date_of_birth_opening', 'email', 'phone', 'address', 'observations', 'is_active']);
                updateLabel('trade_name', 'Nome Fantasia');
                updateLabel('cpf_cnpj', 'Nro CNPJ');
                BrasilCondoUtils.applyMask('#id_cpf_cnpj', 'cnpj');
            }

            BrasilCondoUtils.applyMask('#id_date_of_birth_opening', 'date');
            BrasilCondoUtils.applyMask('#id_phone', 'phone');
        }

        function showFields(fieldsArray) {
            $.each(fieldsArray, function(i, f) {
                $('.field-' + f).closest('.form-group, .field-box').show();
            });
        }

        function updateLabel(field, text) {
            var $label = $('.field-' + field).find('label');
            if ($label.length) {
                $label.contents().filter(function() {
                    return this.nodeType === 3;
                }).first().replaceWith(text + ': ');
            }
        }

        $(document).on('change', kindSelect, applyLogic);
        $('body').on('select2:select', kindSelect, applyLogic);
        setInterval(applyLogic, 500);
        applyLogic();
    });
})(window.django ? django.jQuery : jQuery);
