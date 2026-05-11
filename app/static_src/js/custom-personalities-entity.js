(function($) {
    'use strict';

    $(document).ready(function() {
        var kindSelect = '#id_kind';
        
        // Só executa se estiver no formulário de Adição ou Edição
        if ($(kindSelect).length === 0) return;

        var allFields = [
            'name', 'trade_name', 'cpf_cnpj', 'rg_ie', 
            'municipal_registration', 'date_of_birth_opening', 
            'sex', 'email', 'phone', 'address', 'observations', 'is_active'
        ];

        // Variável para evitar execuções repetidas desnecessárias
        var lastKindValue = null;

        function applyLogic() {
            var $field = $(kindSelect);
            
            // Tenta obter o valor de todas as formas possíveis no Jazzmin/Select2
            var kind = $field.val();
            
            // Se o valor estiver vazio, tenta ler diretamente do container do Select2
            if (!kind) {
                var selectedText = $('.select2-selection__rendered').last().text() || "";
                if (selectedText.includes("Física")) kind = "PF";
                else if (selectedText.includes("Jurídica")) kind = "PJ";
            }

            // Se o valor não mudou desde a última verificação, não faz nada (performance)
            if (kind === lastKindValue) return;
            lastKindValue = kind;

            console.log("--- BrasilCondo: Aplicando lógica para ->", kind || "Vazio");

            // 1. Esconde todos os containers
            $.each(allFields, function(i, f) {
                $('.field-' + f).closest('.form-group, .field-box').hide();
            });

            // 2. Mostra e ajusta conforme o Tipo selecionado
            if (kind === 'PF') {
                showFields(['name', 'trade_name', 'cpf_cnpj', 'rg_ie', 'date_of_birth_opening', 'sex', 'email', 'phone', 'address', 'observations', 'is_active']);
                updateLabel('trade_name', 'Apelido');
                updateLabel('cpf_cnpj', 'Nro CPF');
                applyMask('#id_cpf_cnpj', '000.000.000-00');
            } 
            else if (kind === 'PJ') {
                showFields(['name', 'trade_name', 'cpf_cnpj', 'rg_ie', 'municipal_registration', 'date_of_birth_opening', 'email', 'phone', 'address', 'observations', 'is_active']);
                updateLabel('trade_name', 'Nome Fantasia');
                updateLabel('cpf_cnpj', 'Nro CNPJ');
                applyMask('#id_cpf_cnpj', '00.000.000/0000-00');
            }

            // Máscaras que independem do tipo
            applyMask('#id_date_of_birth_opening', '00/00/0000');
            applyMask('#id_phone', '(00) 00000-0000');
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
                    return this.nodeType === 3; // Altera apenas o texto, preservando ícones/asteriscos
                }).first().replaceWith(text + ': ');
            }
        }

        function applyMask(selector, mask) {
            var $el = $(selector);
            if ($el.length && typeof $el.mask === 'function') {
                $el.unmask().mask(mask);
            }
        }

        // --- GATILHOS DE EXECUÇÃO ---
        
        // 1. Escuta mudanças manuais
        $(document).on('change', kindSelect, applyLogic);
        $('body').on('select2:select', kindSelect, applyLogic);

        // 2. MONITORAMENTO ATIVO (Polling)
        // O Jazzmin muitas vezes não dispara eventos de 'change' ao carregar.
        // Verificamos o valor a cada 500ms para garantir a sincronia.
        setInterval(applyLogic, 500);

        // Execução imediata
        applyLogic();
    });
})(window.django ? django.jQuery : jQuery);
