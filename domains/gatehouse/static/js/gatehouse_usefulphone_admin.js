document.addEventListener("DOMContentLoaded", function () {
    function formatPhoneInput(el) {
        if (typeof BrasilCondoUtils === "undefined" || !BrasilCondoUtils.masks.phone) {
            return;
        }
        el.value = BrasilCondoUtils.masks.phone(el.value);
    }

    document.addEventListener("input", function (e) {
        var el = e.target;
        if (el && el.classList && el.classList.contains("mask-phone")) {
            formatPhoneInput(el);
        }
    });

    document.querySelectorAll("input.mask-phone").forEach(formatPhoneInput);
});
