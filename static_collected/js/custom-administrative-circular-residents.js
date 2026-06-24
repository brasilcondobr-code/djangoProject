(function($) {
    $(document).ready(function() {
        const $typeSelect = $('#id_types_residents');
        const $residentSelect = $('#id_residents');

        function log(message, data = '') {
            if (typeof data === 'object') {
                console.log(`[Circular AJAX] ${message}`, data);
            } else {
                console.log(`[Circular AJAX] ${message} ${data}`);
            }
        }

        console.log('[Circular AJAX] DOM carregado');

        if (!$typeSelect.length) {
            console.error('[Circular AJAX] Campo Tipo de Residente localizado: NÃO');
            return;
        }
        log('Campo Tipo de Residente localizado', {
            id: $typeSelect.attr('id'),
            name: $typeSelect.attr('name'),
            value: $typeSelect.val()
        });

        if (!$residentSelect.length) {
            console.error('[Circular AJAX] Campo Residentes localizado: NÃO');
            return;
        }
        log('Campo Residentes localizado', {
            id: $residentSelect.attr('id'),
            name: $residentSelect.attr('name'),
            multiple: $residentSelect.prop('multiple')
        });

        function loadResidentsByType(typeId) {
            log('Disparando carregamento de residentes');
            
            // Limpar seleções e lista atuais
            log('Limpando residentes anteriores');
            $residentSelect.empty().trigger('change');

            // Aplicar estado de carregamento
            log('Aplicando estado de carregamento');
            $residentSelect.prop('disabled', true);
            log('Atualizando componente visual Select2/Jazzmin');
            if ($residentSelect.hasClass('select2-hidden-accessible')) {
                $residentSelect.trigger('change');
            }

            const url = '/administrative/ajax/get-residents-by-type/';
            log('Iniciando chamada Ajax', url);

            $.ajax({
                url: url,
                data: {
                    'type_id': typeId
                },
                dataType: 'json',
                success: function(response) {
                    log('Retorno Ajax recebido', response);

                    $residentSelect.prop('disabled', false);

                    if (response.success && response.residents && response.residents.length > 0) {
                        log(`Quantidade de residentes retornados ${response.count}`);
                        log('Populando campo Residentes');
                        
                        response.residents.forEach(function(resident) {
                            const $option = $('<option></option>')
                                .val(resident.id)
                                .text(resident.name);
                            $residentSelect.append($option);
                        });
                    } else {
                        log('Nenhum residente encontrado');
                        const placeholderText = response.message || 'Nenhum residente encontrado para o tipo selecionado.';
                        const $option = $('<option></option>')
                            .val('')
                            .text(placeholderText);
                        $residentSelect.append($option);
                    }

                    // Atualizar componente visual Select2/Jazzmin
                    log('Atualizando componente visual Select2/Jazzmin');
                    if ($residentSelect.hasClass('select2-hidden-accessible')) {
                        $residentSelect.trigger('change');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('[Circular AJAX] Erro ao carregar residentes:', error);
                    log('Erro ao carregar residentes', error);
                    alert('Não foi possível carregar os residentes neste momento. Tente novamente.');
                    
                    $residentSelect.prop('disabled', false);
                    if ($residentSelect.hasClass('select2-hidden-accessible')) {
                        $residentSelect.trigger('change');
                    }
                }
            });
        }

        // Escutar evento change
        $typeSelect.on('change', function() {
            const typeId = $(this).val();
            if (typeId) {
                log(`Tipo selecionado: ${typeId}`);
                loadResidentsByType(typeId);
            } else {
                log('Tipo selecionado: vazio. Limpando residentes.');
                $residentSelect.empty().trigger('change');
            }
        });

        // Lógica de carregamento inicial (para edição)
        const initialTypeId = $typeSelect.val();
        if (initialTypeId) {
            log('Tipo de Residente já preenchido no carregamento inicial', initialTypeId);
            log('Disparando carregamento inicial de residentes');
            loadResidentsByType(initialTypeId);
        }
    });
})(django.jQuery);
