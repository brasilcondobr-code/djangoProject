(function () {
    "use strict";

    function formatCurrency(value) {
        if (!value) return "";
        let digits = value.replace(/\D/g, "");
        if (digits === "") return "";
        let numberValue = parseInt(digits, 10) / 100;
        return numberValue.toFixed(2).replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    function formatPercentage(value) {
        if (!value) return "";
        let digits = value.replace(/\D/g, "");
        if (digits === "") return "";
        let numberValue = parseInt(digits, 10);
        if (numberValue > 100) numberValue = 100;
        return numberValue + "%";
    }

    function formatNumber(value) {
        if (!value) return "";
        return value.replace(/\D/g, "");
    }

    function applyMasks() {
        document.addEventListener("input", function (event) {
            const target = event.target;

            if (target.classList.contains("js-mask-currency")) {
                const start = target.selectionStart;
                const end = target.selectionEnd;
                target.value = formatCurrency(target.value);
                target.setSelectionRange(start, end);
            }

            if (target.classList.contains("js-mask-percentage")) {
                target.value = formatPercentage(target.value);
            }

            if (target.classList.contains("js-mask-number")) {
                target.value = formatNumber(target.value);
            }
        });

        document.addEventListener("blur", function (event) {
            const target = event.target;

            if (target.classList.contains("js-mask-currency")) {
                const cleaned = target.value.replace(/\./g, "").replace(",", ".");
                const val = parseFloat(cleaned);
                if (!isNaN(val)) {
                    target.value = val.toFixed(2).replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, ".");
                }
            }
        }, true);
    }

    function init() {
        applyMasks();
    }

    if (document.readyState === "complete" || document.readyState === "interactive") {
        init();
    } else {
        document.addEventListener("DOMContentLoaded", init);
    }
})();
