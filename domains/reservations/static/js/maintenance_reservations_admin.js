/**
 * Módulo 02. Manutenções - melhorias de interação do Admin.
 *
 * As regras obrigatórias são validadas no servidor. Este script apenas
 * fornece feedback imediato para o período.
 */
(function ($) {
    "use strict";

    $(document).ready(function () {
        var $startInput = $("#id_startDate");
        var $endInput = $("#id_endDate");

        if (!$startInput.length || !$endInput.length) {
            return;
        }

        function validatePeriod() {
            var start = $startInput.val();
            var end = $endInput.val();
            if (start && end && end < start) {
                $endInput[0].setCustomValidity(
                    "A data final deve ser maior ou igual à data inicial."
                );
                $endInput[0].reportValidity();
                return false;
            }
            $endInput[0].setCustomValidity("");
            return true;
        }

        $startInput.on("change", validatePeriod);
        $endInput.on("change", validatePeriod);
    });
})(django.jQuery);
