/**
 * Módulo 08. Malotes — máscara monetária dos itens (###.###,##).
 * A máscara é apenas visual: o backend valida e converte o valor.
 */
(function ($) {
    function applyCurrencyMask($el) {
        $el.val(BrasilCondoUtils.masks.decimal($el.val()));
    }

    $(document).ready(function () {
        // Linhas já renderizadas (criação e edição)
        applyCurrencyMask($('.inline-related .mask-currency'));
        // Delegação: linhas novas adicionadas pelo inline do admin
        $(document).on(
            'input',
            '.inline-related .mask-currency',
            function () {
                applyCurrencyMask($(this));
            }
        );
    });
})(django.jQuery);
