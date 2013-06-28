// Disclaimer etc.

jQuery(document).ready(function() {

	console.log("/ Document is ready.");

	// Den "Neue/s..."-Buttons Event-Handler zuweisen.
	// Der "Los"-Button schickt das Formular von alleine ab
	jQuery("table").on("click", "tr .button", function() {
		var callButton = jQuery(this).attr("id");
		jQuery.ajax({
			type: "POST",
			data: {caller: callButton},
			beforeSend: function() {
				jQuery("div.errorMsg").html("");
				jQuery("#loading").show();
			},
			success: function(data) {
				switch (callButton) {
					case "newSeedword":
						jQuery("input#seedword").val(data);
						break;
					case "newGenes":
						jQuery("input#genes").val(data);
						break;
					default:
						console.log("Fehler in der AJAX Success-function :-(");
				}
			},
			error: function(xhr, status, error) {
				console.log("/ AJAX-Aufruf fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
				jQuery("div.errorMsg").html('<p class="errorMsg">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte versuchen Sie es erneut.</p>');
			},
			complete: function() {	jQuery("#loading").hide(); },
		});
		return false;
	});

	// Enter-Taste in einem der Textfelder sendet das Formular ab
	jQuery(".textfield").keypress(function(e) {
		if (e.which == 13) {
			jQuery("form#geneForm").trigger("submit");
			return false;
		}
	});

	// zusaetzlichen Event-Handler fuers Submitten des Formulars setzen
	jQuery("form#geneForm").submit( function() {
		jQuery("#loading").show();
		return true;
	});

});
