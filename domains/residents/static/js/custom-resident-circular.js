(function($) {
	'use strict';

	$(document).ready(function() {
		console.group("Circular Residents Filter Debug");
		console.log("JS carregado: custom-circular-residents.js");
		console.log("jQuery disponível:", typeof $ !== "undefined");
		console.log("django.jQuery disponível:", typeof django !== "undefined" && !!django.jQuery);
		console.log("URL atual:", window.location.href);

		var typeSelector = "#id_types_residents";
		var residentSelector = "#id_residents";
		var ajaxUrl = "/administrative/ajax/get-residents-by-type/";

		var $typeField = $(typeSelector);
		var $residentField = $(residentSelector);

		console.log("Seletor Tipo de Residente:", typeSelector);
		console.log("Campo Tipo encontrado?", $typeField.length);
		console.log("Seletor Residentes:", residentSelector);
		console.log("Campo Residentes encontrado?", $residentField.length);
		console.log("URL AJAX configurada:", ajaxUrl);

		if (!$typeField.length) {
			console.error("ERRO: Campo Tipo de Residente não encontrado no DOM!");
		}

		if (!$residentField.length) {
			console.error("ERRO: Campo Residentes não encontrado no DOM!");
		}

		console.groupEnd();

		function clearResidents() {
			var $residentSelect = $(residentSelector);
			console.log("Limpando campo Residentes...");
			$residentSelect.empty().trigger("change");

			if ($residentSelect.data("select2")) {
				$residentSelect.trigger("change.select2");
			}
		}

		function populateResidents(data) {
			var $residentSelect = $(residentSelector);
			console.group("Populando Residentes");
			console.log("Dados recebidos:", data);
			console.log("Total:", data.length);

			$residentSelect.empty();

			$.each(data, function(index, resident) {
				var displayText = resident.name + (resident.email ? " (" + resident.email + ")" : "");
				var option = new Option(displayText, resident.id, false, false);
				$residentSelect.append(option);
			});

			$residentSelect.trigger("change");

			if ($residentSelect.data("select2")) {
				$residentSelect.trigger("change.select2");
			}

			console.groupEnd();
		}

		$(document).on("change", typeSelector, function(e) {
			console.group("🚀 EVENTO DETECTADO: Mudança no Tipo de Residente");
			console.log("Evento original:", e.type);

			var $typeSelect = $(this);
			var typeId = $typeSelect.val();
			console.log("ID Selecionado (val):", typeId);
			console.log("Texto Selecionado (text):", $typeSelect.find("option:selected").text());

			clearResidents();

			if (!typeId) {
				console.warn("Nenhum ID detectado. Abortando AJAX.");
				console.groupEnd();
				return;
			}

			console.log("Iniciando requisição AJAX para:", ajaxUrl, "com type_id:", typeId);

			$.ajax({
				url: ajaxUrl,
				method: "GET",
				dataType: "json",
				data: {
					"type_id": typeId
				},
				success: function(data) {
					console.log("AJAX Sucesso!");
					populateResidents(data);
				},
				error: function(xhr, status, error) {
					console.error("❌ AJAX Erro!");
					console.error("Status:", xhr.status);
					console.error("Resposta:", xhr.responseText);
				},
				complete: function() {
					console.groupEnd();
				}
			});
		});
	});
})(typeof django !== "undefined" && django.jQuery ? django.jQuery : jQuery);
