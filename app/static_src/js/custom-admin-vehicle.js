
// Inicio do script
(function($) {
    'use strict';

    if (!$) {
        console.error("django.jQuery não encontrado.");
        return;
    }

    $(document).ready(function() {
        var unitSelect = '#id_condo_unit';
        var garageInput = '#id_garage_space';

        function getUnitSelectionValue($element) {
            var rawValue = $element.val();
            var selectedOpt = $element.find('option:selected').attr('value');
            var select2Data = null;

            if ($element.data('select2')) {
                try {
                    select2Data = $element.select2('data');
                } catch (err) {
                    console.warn('select2("data") falhou', err);
                }
            }

            if (rawValue) {
                return rawValue;
            }

            if (selectedOpt) {
                return selectedOpt;
            }

            if (select2Data && select2Data.length > 0) {
                return select2Data[0].id || select2Data[0].text || '';
            }

            return '';
        }

        function processUnitSelection(selectedId) {
            if (selectedId) {
                buscarIdentificacaoAjax(selectedId);
            }
        }

        $('body').on('select2:select', unitSelect, function(e) {
            processUnitSelection(e.params && e.params.data ? e.params.data.id : getUnitSelectionValue($(this)));
        });

        $(document).on('change', unitSelect, function() {
            processUnitSelection(getUnitSelectionValue($(this)));
        });

        var $unitField = $(unitSelect);
        if ($unitField.length > 0) {
            var lastUnitValue = getUnitSelectionValue($unitField);
            setInterval(function() {
                var currentValue = getUnitSelectionValue($unitField);
                if (currentValue && currentValue !== lastUnitValue) {
                    lastUnitValue = currentValue;
                    processUnitSelection(currentValue);
                }
            }, 500);
        }

        function buscarIdentificacaoAjax(unitId) {
            $.ajax({
                url: '/ajax/get-unit-identification/',
                data: { 'unit_id': unitId },
                dataType: 'json',
                success: function(data) {
                    if (data.identification) {
                        $(garageInput).val(data.identification);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Erro no AJAX:', status, error);
                }
            });
        }

        $('.mask-license-plate').on('input', function(){
            var value = $(this).val().replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
            $(this).val(value);
        });

        $('.mask-year').on('input', function(){
            var value = $(this).val().replace(/[^0-9]/g, '').slice(0, 4);
            $(this).val(value);
        });
    });

})(window.django ? django.jQuery : jQuery);
//# Final do script