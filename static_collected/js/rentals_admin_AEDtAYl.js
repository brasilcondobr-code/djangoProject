/**
 * Módulo 01. Locações - melhorias de interação do Admin.
 *
 * As regras obrigatórias são validadas no servidor; este script apenas
 * melhora a experiência (máscara monetária, cobrança e datas).
 */
(function ($) {
    "use strict";

    function applyCurrencyMask() {
        $(this).val(BrasilCondoUtils.masks.decimal($(this).val()));
    }

    $(document).ready(function () {
        var $priceInput = $("#id_rentalPrice");
        var $startInput = $("#id_startDate");
        var $endInput = $("#id_endDate");

        if ($priceInput.length && typeof BrasilCondoUtils !== "undefined") {
            // Máscara apenas visual; o servidor converte e valida o valor.
            $priceInput.val(BrasilCondoUtils.masks.decimal($priceInput.val()));
            $priceInput.on("input", applyCurrencyMask);
        }

        function isChargeEnabled() {
            var $checked = $('input[name="charge_amount"]:checked');
            return !$checked.length || $checked.val() === "True";
        }

        function syncChargeState() {
            if (!$priceInput.length) {
                return;
            }
            var enabled = isChargeEnabled();
            $priceInput.prop("required", enabled);
            $priceInput.prop("disabled", !enabled);
            $priceInput
                .closest(".form-group, .mb-3")
                .css("opacity", enabled ? "1" : "0.55");
            if (!enabled) {
                $priceInput.val("");
            }
        }

        $('input[name="charge_amount"]').on("change", syncChargeState);
        syncChargeState();

        function validatePeriod() {
            if (!$startInput.length || !$endInput.length) {
                return true;
            }
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
