window.addEventListener('load', function() {
    // Garante que o jQuery do Django está disponível e isolado
    (function($) {
        'use strict';
        
        console.log('--- DEBUG: custom-admin-states.js carregado com sucesso ---');

        // Seleciona o campo pela classe que definimos no StatesForm
        var fieldAbbreviation = $('.mask-abbreviation');

        // 1. Força maiúsculas e remove caracteres inválidos enquanto o usuário digita
        fieldAbbreviation.on('input', function() {
            var start = this.selectionStart;
            var end = this.selectionEnd;
            
            // Converte para maiúsculas e remove qualquer coisa que não seja letra (A-Z)
            var value = $(this).val().toUpperCase().replace(/[^A-Z]/g, '');
            
            // Garante o limite de 2 caracteres (padrão de UF)
            $(this).val(value.slice(0, 2));
            
            // Mantém a posição do cursor para uma digitação fluida
            this.setSelectionRange(start, end);
        });

        // 2. Garantia extra ao perder o foco (limpa espaços em branco)
        fieldAbbreviation.on('blur', function() {
            $(this).val($(this).val().trim().toUpperCase());
        });

    })(django.jQuery);
});
