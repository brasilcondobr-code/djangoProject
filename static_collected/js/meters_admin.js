(function ($) {
    "use strict";

    function applyCompositionMask() {
        const $field = $("#id_composition");

        if (!$field.length) {
            return;
        }

        $field.on("input", function () {
            let value = $(this).val().replace(/\D/g, "");

            if (value.length > 6) {
                value = value.substring(0, 6);
            }

            if (value.length >= 3) {
                value = value.substring(0, 2) + "/" + value.substring(2);
            }

            $(this).val(value);
        });
    }

    function parseDecimal(value) {
        if (!value) {
            return null;
        }

        return parseFloat(String(value).replace(",", "."));
    }

    function calculateConsumption() {
        const $previous = $("#id_previousValue");
        const $current = $("#id_currentValue");
        const $consumption = $("#id_Consumption");

        if (!$previous.length || !$current.length || !$consumption.length) {
            return;
        }

        function updateConsumption() {
            const previousValue = parseDecimal($previous.val());
            const currentValue = parseDecimal($current.val());

            if (
                previousValue === null ||
                currentValue === null ||
                isNaN(previousValue) ||
                isNaN(currentValue)
            ) {
                return;
            }

            const consumption = currentValue - previousValue;

            if (consumption >= 0) {
                $consumption.val(consumption.toFixed(3));
            }
        }

        $previous.on("input change", updateConsumption);
        $current.on("input change", updateConsumption);
    }

    $(document).ready(function () {
        applyCompositionMask();
        calculateConsumption();
    });
})(django.jQuery);
