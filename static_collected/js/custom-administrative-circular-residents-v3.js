(function($) {
    'use strict';

    function log(message, data) {
        console.log('[Circular AJAX] ' + message, data || '');
    }

    function warn(message, data) {
        console.warn('[Circular AJAX] ' + message, data || '');
    }

    // Função para extrair o valor de qualquer forma possível
    function getTypeValue($typeSelect) {
        log('--- TENTANDO EXTRAIR VALOR ---');
        
        // 1. Tenta o valor do elemento nativo (se sincronizado)
        const nativeValue = $typeSelect[0]?.value;
        if (nativeValue && nativeValue !== '' && nativeValue !== '---------') {
            log('Sucesso via DOM Nativo:', nativeValue);
            return nativeValue;
        }

        // 2. Tenta o .val() do jQuery
        const jVal = $typeSelect.val();
        const finalJVal = Array.isArray(jVal) ? (jVal[0] || '') : jVal;
        if (finalJVal && finalJVal !== '' && finalJVal !== '---------') {
            log('Sucesso via jQuery .val():', finalJVal);
            return finalJVal;
        }

        // 3. Tenta a opção selecionada no DOM
        const selectedOpt = $typeSelect.find('option:selected');
        const optVal = selectedOpt.val();
        if (optVal && optVal !== '' && optVal !== '---------') {
            log('Sucesso via Option Selected:', optVal);
            return optVal;
        }

        // 4. Tenta extrair o texto VISÍVEL do widget Select2 (A solução definitiva para dessincronia)
        try {
            const s2Container = $typeSelect.next('.select2-container');
            if (s2Container.length) {
                const visibleText = s2Container.find('.select2-selection__rendered').text().trim();
                log('Tentativa via Texto Visível do Widget:', visibleText);
                if (visibleText && visibleText !== '' && visibleText !== '---------') {
                    log('Sucesso via Texto Visível!');
                    return visibleText; 
                }
            }
        } catch (e) {
            warn('Erro ao ler texto do Select2', e);
        }

        log('--- FALHA TOTAL: Nenhum valor identificado ---');
        return '';
    }

    function refreshSelect2($select) {
        $select.trigger('change');
    }

    function clearResidents($residentSelect) {
        log('Limpando campo Residentes');
        $residentSelect.empty();
        refreshSelect2($residentSelect);
    }

    function setResidentsState($residentSelect, state) {
        if (state === 'loading') {
            log('Estado: CARREGANDO...');
            $residentSelect.prop('disabled', true);
        } else if (state === 'enabled') {
            log('Estado: HABILITADO');
            $residentSelect.prop('disabled', false);
        } else {
            log('Estado: DESABILITADO');
            $residentSelect.prop('disabled', true);
        }
        refreshSelect2($residentSelect);
    }

    function appendResidents($residentSelect, residents) {
        log(' Populando ' + residents.length + ' residentes');
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
        const url = $typeSelect.data('residents-url');
        return url || '/administrative/ajax/get-residents-by-type/';
    }

    let lastLoadedType = null;
    let currentRequest = null;

    function loadResidentsByType(typeValue, options) {
        options = options || {};
        const force = Boolean(options.force);
        const $typeSelect = $('#id_types_residents');
        const $residentSelect = $('#id_residents');

        if (!$typeSelect.length || !$residentSelect.length) return;

        if (!typeValue) {
            warn('Valor vazio. Desabilitando residentes.');
            clearResidents($residentSelect);
            setResidentsState($residentSelect, 'disabled');
            lastLoadedType = null;
            return;
        }

        if (!force && String(lastLoadedType) === String(typeValue)) {
            return;
        }

        lastLoadedType = typeValue;
        const ajaxUrl = getAjaxUrl($typeSelect);

        log('DISPARANDO AJAX -> Tipo: ' + typeValue + ' | URL: ' + ajaxUrl);

        clearResidents($residentSelect);
        setResidentsState($residentSelect, 'loading');

        if (currentRequest && currentRequest.readyState !== 4) {
            currentRequest.abort();
        }

        currentRequest = $.ajax({
            url: ajaxUrl,
            method: 'GET',
            dataType: 'json',
            data: { type_id: typeValue },
            success: function(response) {
                log('Resposta AJAX recebida:', response);
                if (response && response.success && response.residents && response.residents.length > 0) {
                    appendResidents($residentSelect, response.residents);
                    setResidentsState($residentSelect, 'enabled');
                } else {
                    warn(response.message || 'Nenhum residente encontrado.');
                    setResidentsState($residentSelect, 'disabled');
                }
            },
            error: function(xhr, status, error) {
                if (status === 'abort') return;
                setResidentsState($residentSelect, 'disabled');
            }
        });
    }

    // NOVA ABORDAGEM: MutationObserver
    // Monitora mudanças no HTML do widget Select2, ignorando a necessidade de eventos de 'change'
    function setupMutationObserver($typeSelect) {
        log('Configurando MutationObserver para detectar mudanças visuais...');
        
        const targetNode = $typeSelect.next('.select2-container').find('.select2-selection__rendered');
        
        if (!targetNode.length) {
            warn('Elemento visual do Select2 não encontrado para observação.');
            return;
        }

        const config = { childList: true, characterData: true, subtree: true };

        const callback = function(mutationsList, observer) {
            for (const mutation of mutationsList) {
                log('Mudança detectada no texto do Select2!');
                const val = getTypeValue($typeSelect);
                loadResidentsByType(val, { force: true });
                break; 
            }
        };

        const observer = new MutationObserver(callback);
        observer.observe(targetNode[0], config);
        log('MutationObserver ativo e monitorando o campo Tipo de Residente.');
    }

    function bindEvents() {
        $(document).off('.circularResidents');

        // Mantemos o change como fallback
        $(document).on('change', '#id_types_residents', function() {
            const val = getTypeValue($(this));
            loadResidentsByType(val, { force: true });
        });

        // Evento específico do Select2
        $(document).on('select2:select', '#id_types_residents', function() {
            const val = getTypeValue($(this));
            loadResidentsByType(val, { force: true });
        });
    }

    function initCircularResidentsAjax() {
        log('Iniciando sistema de filtragem...');

        const $typeSelect = $('#id_types_residents');
        const $residentSelect = $('#id_residents');

        if (!$typeSelect.length || !$residentSelect.length) {
            warn('Campos não encontrados.');
            return;
        }

        clearResidents($residentSelect);
        setResidentsState($residentSelect, 'disabled');

        bindEvents();
        
        // Tenta configurar o observador de mudanças visuais
        setupMutationObserver($typeSelect);

        const initialVal = getTypeValue($typeSelect);
        if (initialVal) {
            loadResidentsByType(initialVal, { force: true });
        }
    }

    if (typeof django !== 'undefined' && django.jQuery) {
        const $ = django.jQuery;
        $(document).ready(initCircularResidentsAjax);
        $(window).on('load', function() {
            setTimeout(initCircularResidentsAjax, 500);
        });
    }
})(django.jQuery);
