(function ($) {
    "use strict";

    // Mesma máscara usada em "Valor original" no formulário de cobranças.
    if (!$ || !$.fn || !$.fn.mask) {
        return;
    }

    $(function () {
        $("#id_amountReceived").mask("###.###,##", { reverse: true });
    });
})(window.jQuery);
