(function ($) {
    "use strict";

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function emptyOptions() {
        return '<option value="">---------</option>';
    }

    var residentsRequestSeq = 0;

    function refreshPaymasterSelect2($paymaster) {
        // Atualiza a exibição do Select2, inclusive quando ele foi
        // inicializado pela instância global de jQuery do Jazzmin.
        $paymaster.trigger("change.select2");
        if (window.jQuery && window.jQuery !== $) {
            window.jQuery($paymaster[0]).trigger("change.select2");
        }
    }

    function loadResidents(unitId, selectedValue, keepMissing) {
        var $paymaster = $("#id_paymaster");
        if (!$paymaster.length) {
            return;
        }

        var url = $paymaster.attr("data-residents-url");
        if (!url) {
            return;
        }

        if (!unitId) {
            residentsRequestSeq++;
            $paymaster.html(emptyOptions());
            refreshPaymasterSelect2($paymaster);
            return;
        }

        var requestId = ++residentsRequestSeq;
        var selectedText = $paymaster.find("option:selected").text();
        $paymaster.html(emptyOptions());
        refreshPaymasterSelect2($paymaster);

        $.ajax({
            url: url,
            data: { unit_id: unitId },
            dataType: "json",
        })
            .done(function (data) {
                if (requestId !== residentsRequestSeq) {
                    return;
                }
                var results = (data && data.results) || [];
                var options = [emptyOptions()];
                var found = false;

                for (var i = 0; i < results.length; i++) {
                    var item = results[i];
                    if (
                        selectedValue &&
                        String(item.id) === String(selectedValue)
                    ) {
                        found = true;
                    }
                    options.push(
                        '<option value="' +
                            escapeHtml(item.id) +
                            '">' +
                            escapeHtml(item.text) +
                            "</option>"
                    );
                }

                if (
                    keepMissing &&
                    selectedValue &&
                    !found &&
                    selectedText
                ) {
                    options.push(
                        '<option value="' +
                            escapeHtml(selectedValue) +
                            '">' +
                            escapeHtml(selectedText) +
                            "</option>"
                    );
                }

                $paymaster.html(options.join(""));
                if (selectedValue) {
                    $paymaster.val(String(selectedValue));
                }
                refreshPaymasterSelect2($paymaster);
            })
            .fail(function () {
                if (requestId !== residentsRequestSeq) {
                    return;
                }
                $paymaster.html(emptyOptions());
                refreshPaymasterSelect2($paymaster);
            });
    }

    $(document).ready(function () {
        var $value = $("#id_value");
        if ($value.length) {
            if ($.fn.mask) {
                $value.mask("###.###,##", { reverse: true });
            } else {
                // Fallback para o caso de o plugin não ser carregado.
                $value.on("input", function () {
                    var digits = $(this).val().replace(/\D/g, "");
                    if (!digits) {
                        $(this).val("");
                        return;
                    }
                    var amount = (parseInt(digits, 10) / 100)
                        .toFixed(2)
                        .replace(".", ",")
                        .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
                    $(this).val(amount);
                });
            }
        }

        var $scope = $("#id_scope");
        if ($scope.length) {
            if ($.fn.mask) {
                // No jQuery Mask, "9" já é dígito opcional; "8" não é
                // placeholder por padrão. Registramos "8" como dígito para
                // que a máscara solicitada "99-8888" funcione como MM-AAAA.
                $scope.mask("99-8888", {
                    translation: {
                        "8": { pattern: /\d/ },
                    },
                });
            } else {
                // Fallback para o caso de o plugin não ser carregado.
                $scope.on("input", function () {
                    var digits = $(this).val().replace(/\D/g, "").slice(0, 6);
                    if (digits.length > 2) {
                        digits = digits.slice(0, 2) + "-" + digits.slice(2);
                    }
                    $(this).val(digits);
                });
            }

            // O Título já vem preenchido com o texto sugerido e acompanha a
            // Competência ("Taxa condominial de: 11-2026"), mas nunca
            // sobrescreve um título digitado pelo usuário.
            var $title = $("#id_title");
            if ($title.length) {
                var autoTitle = null;

                var suggestedTitle = function () {
                    var scope = ($scope.val() || "").trim();
                    return "Taxa condominial de: " + (scope || "MM-AAAA");
                };

                var updateTitleDefault = function () {
                    var suggestion = suggestedTitle();
                    $title.attr("placeholder", suggestion);
                    if (!$title.val() || $title.val() === autoTitle) {
                        $title.val(suggestion);
                        autoTitle = suggestion;
                    }
                };

                var initialTitle = suggestedTitle();
                if (!$title.val() || $title.val() === initialTitle) {
                    $title.val(initialTitle);
                    autoTitle = initialTitle;
                }

                updateTitleDefault();
                $scope.on("input change keyup blur", updateTitleDefault);
            }
        }

        var $unit = $("#id_condominium");
        var $paymaster = $("#id_paymaster");
        if (!$unit.length || !$paymaster.length) {
            return;
        }

        // Inicializa o Select2 do pagador com a mesma instância de jQuery do
        // nosso código; assim o Jazzmin não o reinicializa com outra instância
        // e o refresh de opções funciona corretamente.
        if ($.fn.select2 && !$paymaster.hasClass("select2-hidden-accessible")) {
            $paymaster.select2({ width: "100%" });
        }

        var lastUnitId = $unit.val();

        function onUnitChanged() {
            var unitId = $unit.val();
            if (unitId === lastUnitId) {
                return;
            }
            lastUnitId = unitId;
            loadResidents(unitId, null, false);
        }

        // "change" cobre o select nativo; os eventos abaixo cobrem o Select2
        // usado pelo autocomplete do Admin.
        $unit.on("change select2:select select2:clear", onUnitChanged);

        loadResidents(lastUnitId, $paymaster.val(), true);
    });
})(django.jQuery);
