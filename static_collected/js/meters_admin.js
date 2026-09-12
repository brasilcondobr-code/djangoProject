/**
 * Meters Admin JS - Enhanced Masking
 * This script handles the masks for the Meters form in Django Admin.
 */

(function () {
    "use strict";

    console.log("Meters Admin JS: Loading script...");

    // --- Utility: Formatters ---

    function formatComposition(value) {
        // Remove all non-digits
        let digits = value.replace(/\D/g, "");
        if (digits.length > 6) digits = digits.substring(0, 6);
        
        if (digits.length >= 3) {
            return digits.substring(0, 2) + "/" + digits.substring(2);
        }
        return digits;
    }

    function formatMoneyMask(value, precision) {
        if (!value) return "";
        // Remove all non-digits
        let digits = value.replace(/\D/g, "");
        if (digits === "") return "";

        // Convert to number and divide by 10^precision to get the decimal
        let numberValue = parseInt(digits, 10) / Math.pow(10, precision);
        
        // Format to string with fixed precision and replace dot with comma
        return numberValue.toFixed(precision).replace(".", ",");
    }

    function parseDecimal(value) {
        if (!value) return null;
        let sanitized = String(value).replace(/[^0-9,.]/g, "");
        return parseFloat(sanitized.replace(",", "."));
    }

    // --- Masking Logic ---

    function applyMasks() {
        console.log("Meters Admin JS: Applying masks via event delegation");

        // Use event delegation on the document to ensure masks work even if elements are re-rendered
        document.addEventListener("input", function (event) {
            const target = event.target;

            // 1. Composição Mask (MM/AAAA)
            if (target.id === "id_composition" || target.classList.contains("js-mask-composition")) {
                const start = target.selectionStart;
                const end = target.selectionEnd;
                target.value = formatComposition(target.value);
                target.setSelectionRange(start, end);
            }

            // 2. Decimal Masks (3 digits) - Valor Anterior, Atual, Consumo
            if (
                target.id === "id_previousValue" || 
                target.id === "id_currentValue" || 
                target.id === "id_Consumption" || 
                target.classList.contains("js-mask-decimal-3")
            ) {
                target.value = formatMoneyMask(target.value, 3);
            }

            // 3. Decimal Mask (2 digits) - Valor
            if (target.id === "id_Value" || target.classList.contains("js-mask-decimal-2")) {
                target.value = formatMoneyMask(target.value, 2);
            }
        });

        // Blur event for precision formatting and consumption calculation
        document.addEventListener("blur", function (event) {
            const target = event.target;
            
            if (target.id === "id_previousValue" || target.id === "id_currentValue" || target.id === "id_Consumption") {
                const val = parseDecimal(target.value);
                if (!isNaN(val)) target.value = val.toFixed(3).replace(".", ",");
            } else if (target.id === "id_Value") {
                const val = parseDecimal(target.value);
                if (!isNaN(val)) target.value = val.toFixed(2).replace(".", ",");
            }

            // Trigger consumption calculation
            if (target.id === "id_previousValue" || target.id === "id_currentValue") {
                calculateConsumption();
            }
        }, true);
    }

    function calculateConsumption() {
        const $previous = document.getElementById("id_previousValue");
        const $current = document.getElementById("id_currentValue");
        const $consumption = document.getElementById("id_Consumption");

        if (!$previous || !$current || !$consumption) return;

        const p = parseDecimal($previous.value);
        const c = parseDecimal($current.value);

        if (!isNaN(p) && !isNaN(c)) {
            const res = c - p;
            if (res >= 0) {
                $consumption.value = res.toFixed(3).replace(".", ",");
            }
        }
    }

    // Initialization
    function init() {
        console.log("Meters Admin JS: Initializing...");
        applyMasks();
        calculateConsumption();
    }

    if (document.readyState === "complete" || document.readyState === "interactive") {
        init();
    } else {
        document.addEventListener("DOMContentLoaded", init);
    }

})();
