(function ($) {
    "use strict";

    function parseDecimal(value) {
        var text = String(value || "").trim();
        if (!text) {
            return null;
        }
        text = text.replace(/\./g, "").replace(",", ".");
        var parsed = parseFloat(text);
        return isNaN(parsed) ? null : parsed;
    }

    function formatMoney(value) {
        return value.toFixed(2).replace(".", ",").replace(
            /\B(?=(\d{3})+(?!\d))/g,
            "."
        );
    }

    function setReadonly(fieldName, value) {
        var $field = $(".field-" + fieldName + " .readonly");
        if ($field.length) {
            $field.text(value);
        }
    }

    function applyMask(selector, mask, options) {
        var $element = $(selector);
        if (!$element.length) {
            return $element;
        }
        if ($.fn.mask) {
            $element.mask(mask, options || {});
        }
        return $element;
    }

    function updatePreview() {
        var $originalInput = $("#id_originalValue");
        // Em páginas somente leitura não há input; preserva os valores
        // calculados exibidos pelo servidor.
        if (!$originalInput.length) {
            return;
        }

        var original = parseDecimal($originalInput.val());
        if (original === null) {
            setReadonly("discountAmount", "-");
            setReadonly("fineAmount", "-");
            setReadonly("interestAmount", "-");
            setReadonly("chargesAmount", "-");
            setReadonly("totalAmount", "-");
            setReadonly("balance", "-");
            return;
        }

        var percents = {
            discountAmount: parseDecimal($("#id_discountPercent").val()),
            fineAmount: parseDecimal($("#id_penaltyPercent").val()),
            interestAmount: parseDecimal($("#id_feesPercent").val()),
            chargesAmount: parseDecimal($("#id_chargesPercent").val()),
        };

        var amounts = {};
        var total = original;
        Object.keys(percents).forEach(function (field) {
            var percent = percents[field];
            var amount = percent === null ? null : original * percent / 100;
            amounts[field] = amount;
            if (field === "discountAmount") {
                total -= amount || 0;
            } else {
                total += amount || 0;
            }
            setReadonly(
                field,
                amount === null ? "-" : "R$ " + formatMoney(amount)
            );
        });

        var formattedTotal = "R$ " + formatMoney(total);
        setReadonly("totalAmount", formattedTotal);
        // Sem recebimentos, o saldo apresentado acompanha o valor total.
        setReadonly("balance", formattedTotal);
    }

    $(document).ready(function () {
        applyMask("#id_originalValue", "###.###,##", { reverse: true });
        applyMask("#id_amountReceived", "###.###,##", { reverse: true });
        applyMask(".mask-percent", "##0,00", { reverse: true });
        applyMask(
            "#id_scope",
            "99-8888",
            { translation: { "8": { pattern: /\d/ } } }
        );

        $("#id_originalValue, #id_discountPercent, #id_penaltyPercent, " +
            "#id_feesPercent, #id_chargesPercent")
            .on("input change keyup blur", updatePreview);

        updatePreview();
    });
})(django.jQuery);
