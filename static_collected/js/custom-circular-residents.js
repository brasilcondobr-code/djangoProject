(function($) {
    $(document).ready(function() {
        const $typeSelect = $('#id_types_residents');
        const $residentSelect = $('#id_residents');

        if (!$typeSelect.length || !$residentSelect.length) {
            console.error('Circular residents JS: Required fields not found.');
            return;
        }

        $typeSelect.on('change', function() {
            const typeId = $(this).val();

            // Clear current residents
            $residentSelect.empty().trigger('change');

            if (!typeId) {
                // If no type selected, you might want to show a message or just keep it empty
                return;
            }

            // Indicate loading
            $residentSelect.prop('disabled', true);
            // If using Select2 (common in Jazzmin/Django Admin)
            if ($residentSelect.hasClass('select2-hidden-accessible')) {
                $residentSelect.prop('disabled', true).trigger('change');
            }

            $.ajax({
                url: '/administrative/ajax/get-residents-by-type/',
                data: {
                    'type_id': typeId
                },
                success: function(data) {
                    // Clear current options
                    $residentSelect.empty();

                    if (data.length === 0) {
                        // Optionally add a placeholder option
                        const $option = $('<option></option>')
                            .val('')
                            .text('Nenhum residente encontrado para o tipo selecionado.');
                        $residentSelect.append($option);
                    } else {
                        data.forEach(function(resident) {
                            const $option = $('<option></option>')
                                .val(resident.id)
                                .text(resident.name);
                            $residentSelect.append($option);
                        });
                    }

                    // Re-enable and update
                    $residentSelect.prop('disabled', false);
                    if ($residentSelect.hasClass('select2-hidden-accessible')) {
                        $residentSelect.trigger('change');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching residents:', error);
                    alert('Não foi possível carregar os residentes neste momento. Tente novamente.');
                    $residentSelect.prop('disabled', false);
                    if ($residentSelect.hasClass('select2-hidden-accessible')) {
                        $residentSelect.trigger('change');
                    }
                }
            });
        });
    });
})(django.jQuery);
