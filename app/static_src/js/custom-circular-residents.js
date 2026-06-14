(function($) {
    $(document).ready(function() {
        var typeSelect = '#id_types_residents';
        var residentSelect = '#id_residents';

        $(document).on('change', typeSelect, function() {
            var typeId = $(this).val();
            if (typeId) {
                $.ajax({
                    url: '/administrative/ajax/get-residents-by-type/',
                    data: { 'type_id': typeId },
                    dataType: 'json',
                    success: function(data) {
                        var $residentSelect = $(residentSelect);
                        $residentSelect.empty();
                        $residentSelect.append('<option value="">---------</option>');
                        $.each(data, function(index, resident) {
                            var text = resident.name + ' (' + resident.email + ')';
                            $residentSelect.append($('<option>', {
                                value: resident.id,
                                text: text
                            }));
                        });
                        // If using Select2, trigger change to refresh UI
                        if ($residentSelect.data('select2')) {
                            $residentSelect.trigger('change');
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Erro no AJAX para residentes:', status, error);
                    }
                });
            } else {
                $(residentSelect).empty().append('<option value="">---------</option>');
                if ($(residentSelect).data('select2')) {
                    $(residentSelect).trigger('change');
                }
            }
        });
    });
})(django.jQuery);
