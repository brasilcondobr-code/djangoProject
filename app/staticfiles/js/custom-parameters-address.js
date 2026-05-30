window.addEventListener('load', function() {
    // Garante que o jQuery do Django está disponível e isolado
    (function($) {
        'use strict';
        
        console.log('--- DEBUG: custom-admin-address.js carregado com sucesso ---');

        var fieldCep = $('.mask-zip-code');
        var fieldStreet = $('.mask-street');
        var fieldNeighborhood = $('.mask-neighborhood');
        var fieldCity = $('.mask-city');
        var fieldState = $('.mask-state');
        var fieldNumber = $('.mask-number');

        // Configurações de atributos físicos
        fieldNumber.attr('type', 'text').attr('maxlength', '6');
        fieldCep.attr('maxlength', '9');

        // --- 1. MÁSCARAS DE ENTRADA ---
        fieldCep.on('input', function() {
            var value = $(this).val().replace(/\D/g, ''); 
            if (value.length > 5) {
                value = value.replace(/^(\d{5})(\d)/, '$1-$2');
            }
            $(this).val(value.slice(0, 9));
        });

        // --- 2. LÓGICA VIACEP ---
        fieldCep.on('blur', function() {
            var cep = $(this).val().replace(/\D/g, '');

            if (cep !== "" && cep.length === 8) {
                // Feedback visual de carregamento
                fieldStreet.val("...");
                fieldNeighborhood.val("...");
                fieldCity.val("...");

                $.getJSON("https://viacep.com.br/ws/"+ cep +"/json/?callback=?", function(dados) {
                    if (!("erro" in dados)) {
                        fieldStreet.val(dados.logradouro);
                        fieldNeighborhood.val(dados.bairro);
                        fieldCity.val(dados.localidade);

                        var ufBusca = dados.uf.toUpperCase().trim();
                        var idParaSelecionar = null;

                        // Localiza o ID (value) correspondente à sigla (texto) nas options
                        fieldState.find('option').each(function() {
                            var textoOption = $(this).text().toUpperCase().trim();
                            if (textoOption.includes("(" + ufBusca + ")") || textoOption === ufBusca) {
                                idParaSelecionar = $(this).val();
                                return false; 
                            }
                        });

                        if (idParaSelecionar) {
                            console.log("Forçando seleção visual do ID: " + idParaSelecionar);

                            // 1. Define o valor no select original
                            fieldState.val(idParaSelecionar);

                            // 2. Verifica se o Select2 está ativo e força a atualização
                            if (fieldState.hasClass("select2-hidden-accessible")) {
                                // Notifica o Select2 da mudança
                                fieldState.trigger('change.select2');
                                
                                // Se ainda assim não mudar, forçamos o texto manualmente na caixa do Select2
                                var selectedText = fieldState.find("option:selected").text();
                                $('.select2-selection__rendered[id*="id_state"]').text(selectedText);
                                $('.select2-selection__rendered[id*="id_state"]').attr('title', selectedText);
                            } else {
                                // Caso não seja Select2, apenas o change resolve
                                fieldState.trigger('change');
                            }

                            console.log("Sucesso! Selecionado ID: " + idParaSelecionar + " para UF: " + ufBusca);
                        }
                        
                        fieldNumber.focus();
                    } else {
                        alert("CEP não encontrado.");
                        fieldStreet.val("");
                        fieldNeighborhood.val("");
                        fieldCity.val("");
                    }
                });
            }
        });

    })(django.jQuery);
});
