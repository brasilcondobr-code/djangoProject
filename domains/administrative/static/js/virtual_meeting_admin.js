(function($) {
    'use strict';
    function bindRow($row) {
        const $typeSelect = $row.find('.resident-type-select');
        const $residentSelect = $row.find('.resident-select');

        if (!$typeSelect.length || !$residentSelect.length) {
            return;
        }

        const url = $typeSelect.attr('data-residents-url') ||
            '/administrative/ajax/residents-by-type/';

        function loadResidents(typeId) {
            $residentSelect.empty();
            $residentSelect.prop('disabled', true);

            if (!typeId) {
                $residentSelect.prop('disabled', false);
                return;
            }

            $.ajax({
                url: url,
                data: { type_id: typeId },
                dataType: 'json',
                success: function(response) {
                    $residentSelect.prop('disabled', false);
                    if (response.success && response.residents) {
                        response.residents.forEach(function(resident) {
                            $residentSelect.append(
                                $('<option></option>')
                                    .val(resident.id)
                                    .text(resident.name)
                            );
                        });
                    }
                    $residentSelect.trigger('change');
                },
                error: function() {
                    $residentSelect.prop('disabled', false);
                    $residentSelect.trigger('change');
                }
            });
        }

        $typeSelect.off('change.virtual-meeting').on('change.virtual-meeting', function() {
            loadResidents($(this).val());
        });

        loadResidents($typeSelect.val());
    }

    $(document).ready(function() {
        $('.resident-type-select').each(function() {
            bindRow($(this).closest('tr'));
        });

        $(document).on('formset:added', function(event, $row, formsetName) {
            if (formsetName === 'participants' || $row.find('.resident-type-select').length) {
                bindRow($row);
            }
        });
    });
})(django.jQuery || jQuery);