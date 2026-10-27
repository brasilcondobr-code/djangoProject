document.addEventListener("DOMContentLoaded", function () {
    function formatTimeInput(el) {
        if (typeof BrasilCondoUtils === "undefined" || !BrasilCondoUtils.masks.time) {
            return;
        }
        el.value = BrasilCondoUtils.masks.time(el.value);
    }

    document.addEventListener("input", function (e) {
        var el = e.target;
        if (el && el.classList && el.classList.contains("mask-time")) {
            formatTimeInput(el);
        }
    });

    document.querySelectorAll("input.mask-time").forEach(formatTimeInput);
});
