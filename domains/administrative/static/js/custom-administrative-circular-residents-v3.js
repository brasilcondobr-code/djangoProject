(function($) {
    'use strict';

    function log(message, data) {
        if (typeof data !== 'undefined') {
            console.log('[Circular AJAX] ' + message, data);
        } else {
            console.log('[Circular AJAX] ' + message);
        }
    }

    function warn(message, data) {
        if (typeof data !== 'undefined') {
            console.warn('[Circular AJAX] ' + message, data);
        } else {
            console.warn('[Circular AJAX] ' + message);
        }
    }

    function getSelect2Text($select) {
        try {
            if ($select.hasClass('select2-hidden-accessible') && typeof $select.select2 === 'function') {
                const data = $select.select2('data');

                if (data && data.length > 0 && data[0].text) {
                    const text = String(data[0].text).trim();

                    if (text && text !== '---------' && text !== '---------') {
                        return text;
                    }
                }
            }
        } catch (e) {
            warn('Não foi possível ler texto do Select2.', e);
        }

        return '';
    }

    function getTypeValue($typeSelect) {
        let value = $typeSelect.val();

        if (Array.isArray(value)) {
            value = value.length > 0 ? value[0] : '';
        }

        if (value) {
            return value;
        }

        const selectedOptionValue = $typeSelect.find('option:selected').val();

        if (selectedOptionValue) {
            return selectedOptionValue;
        }

        const select2Text = getSelect2Text($typeSelect);

        if (select2Text) {
            warn('O campo Tipo de Residente está sem value. Usando texto como fallback.', select2Text);
            return select2Text;
        }

        return '';
    }

    function refreshSelect2($select) {
        $select.trigger('change');

        if ($select.hasClass('select2-hidden-accessible')) {
            $select.trigger('change.select2');
        }
    }

    function clearResidents($residentSelect) {
        log('Limpando residentes anteriores');

        $residentSelect.empty();
        refreshSelect2($residentSelect);
    }

    function setResidentsLoading($residentSelect, loading) {
        if (loading) {
            log('Aplicando estado de carregamento');
        } else {
            log('Removendo estado de carregamento');
        }

        $residentSelect.prop('disabled', loading);
        refreshSelect2($residentSelect);
    }

    function appendResidents($residentSelect, residents) {
        log('Populando campo Residentes');

        residents.forEach(function(resident) {
            const option = new Option(
                resident.name || resident.text,
                resident.id,
                false,
                false
            );

            $residentSelect.append(option);
        });

        refreshSelect2($residentSelect);
    }

    function getAjaxUrl($typeSelect) {
        const urlFromField = $typeSelect.data('residents-url');

        if (urlFromField) {
            return urlFromField;
        }

        return '/administrative/ajax/get-residents-by-type/';
    }

    let lastLoadedType = null;
    let currentRequest = null;

    function loadResidentsByType(typeValue, options) {
        options = options || {};

        const force = Boolean(options.force);
        const $typeSelect = $('#id_types_residents');
        const $residentSelect = $('#id_residents');

        if (!$typeSelect.length) {
            console.error('[Circular AJAX] Campo Tipo de Residente localizado: NÃO');
            return;
        }

        if (!$residentSelect.length) {
            console.error('[Circular AJAX] Campo Residentes localizado: NÃO');
            return;
        }

        if (!typeValue) {
            warn('Nenhum tipo informado. Residentes não serão carregados.');
            clearResidents($residentSelect);
            return;
        }

        if (!force && String(lastLoadedType) === String(typeValue)) {
            log('Tipo já carregado. Ignorando nova chamada.', typeValue);
            return;
        }

        lastLoadedType = typeValue;

        const ajaxUrl = getAjaxUrl($typeSelect);

        log('Disparando carregamento de residentes', {
            type_id: typeValue
        });

        clearResidents($residentSelect);
        setResidentsLoading($residentSelect, true);

        if (currentRequest && currentRequest.readyState !== 4) {
            log('Cancelando requisição AJAX anterior');
            currentRequest.abort();
        }

        const fullUrlForLog = ajaxUrl + '?type_id=' + encodeURIComponent(typeValue);
        log('Iniciando chamada Ajax ' + fullUrlForLog);

        currentRequest = $.ajax({
            url: ajaxUrl,
            method: 'GET',
            dataType: 'json',
            data: {
                type_id: typeValue
            },
            success: function(response) {
                log('Retorno Ajax recebido', response);

                setResidentsLoading($residentSelect, false);

                if (response && response.success && response.residents && response.residents.length > 0) {
                    log('Quantidade de residentes retornados ' + response.count);
                    appendResidents($residentSelect, response.residents);
                } else {
                    warn(response.message || 'Nenhum residente encontrado para o tipo selecionado.');
                    refreshSelect2($residentSelect);
                }
            },
            error: function(xhr, status, error) {
                if (status === 'abort') {
                    return;
                }

                console.error('[Circular AJAX] Erro ao carregar residentes:', {
                    status: status,
                    error: error,
                    responseText: xhr.responseText
                });

                setResidentsLoading($residentSelect, false);

                alert('Não foi possível carregar os residentes neste momento. Tente novamente.');
            }
        });
    }

    let scheduledInitialLoad = null;

    function scheduleInitialLoad(delay) {
        window.setTimeout(function() {
            const $typeSelect = $('#id_types_residents');
            const $residentSelect = $('#id_residents');

            if (!$typeSelect.length || !$residentSelect.length) {
                return;
            }

            const typeValue = getTypeValue($typeSelect);

            if (typeValue) {
                log('Tipo de Residente já preenchido no carregamento inicial ' + typeValue);
                log('Disparando carregamento inicial de residentes');
                loadResidentsByType(typeValue, { force: true });
            } else {
                log('Nenhum tipo preenchido no carregamento inicial.');
            }
        }, delay);
    }

    function bindEvents() {
        $(document).off('.circularResidents');

        $(document).on(
            'change.circularResidents select2:select.circularResidents',
            '#id_types_residents',
            function() {
                const $typeSelect = $(this);
                const typeValue = getTypeValue($typeSelect);

                if (scheduledInitialLoad) {
                    window.clearTimeout(scheduledInitialLoad);
                }

                if (typeValue) {
                    log('Tipo selecionado: ' + typeValue);
                    loadResidentsByType(typeValue, { force: true });
                } else {
                    log('Tipo selecionado: vazio. Limpando residentes.');
                    lastLoadedType = null;
                    clearResidents($('#id_residents'));
                }
            }
        );
    }

    function initCircularResidentsAjax() {
        log('DOM carregado');

        const $typeSelect = $('#id_types_residents');
        const $residentSelect = $('#id_residents');

        if (!$typeSelect.length) {
            console.error('[Circular AJAX] Campo Tipo de Residente localizado: NÃO');
            return;
        }

        log('Campo Tipo de Residente localizado', {
            id: $typeSelect.attr('id'),
            name: $typeSelect.attr('name'),
            value: $typeSelect.val(),
            select2Text: getSelect2Text($typeSelect)
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

        bindEvents();

        /*
         * Jazzmin/Select2 pode terminar a inicialização depois do DOM ready.
         * Por isso fazemos algumas tentativas leves.
         */
        scheduleInitialLoad(100);
        scheduleInitialLoad(500);
        scheduleInitialLoad(1000);
    }

    if (typeof django !== 'undefined' && django.jQuery) {
        $(document).ready(initCircularResidentsAjax);
        $(window).on('load', function() {
            scheduleInitialLoad(300);
        });
    } else {
        console.error('[Circular AJAX] django.jQuery não está disponível.');
    }

})(django.jQuery);
