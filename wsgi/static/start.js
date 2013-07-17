// Disclaimer etc.

jQuery(document).ready(function() {

	// Den Buttons Event-Handler zuweisen.
	jQuery("form").on("click", "button.button", function() {

		// evtl. Fehlermeldung loeschen
		jQuery("div.errorMsg").html("");

		// Los-Button: Formular abschicken
		if (jQuery(this).attr("id") == "Los") {
			jQuery("#geneForm").submit();
			return false;
		};

		// Warteanimation anzeigen
		jQuery("#loading").show();

		// Neue/s-Buttons: Ajax-Request abschicken
		var callButton = jQuery(this).attr("id");
		jQuery.ajax({
			type: "POST",
			data: {caller: callButton},

			success: function(data) {
				switch (callButton) {
					case "newSeedword":
						jQuery("input#seedword").val(data);
						break;
					case "newGenes":
						jQuery("input#genes").val(data);
						break;
					default:
						console.log("/ Fehler in der AJAX Success-function :-(");
				}
			},

			error: function(xhr, status, error) {
				console.log("/ AJAX-Aufruf fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
				jQuery("div.errorMsg").html('<p  class="highlight">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte versuchen Sie es erneut.</p>');
			},

			complete: function() {	jQuery("#loading").hide(); },
		});
		return false;
	});

	// Enter-Taste in einem der Textfelder sendet das Formular ebenfalls ab
	jQuery(".textfield").keypress(function(e) {
		if (e.which == 13) {
			jQuery("#geneForm").submit();
			return false;
		}
	});

});
