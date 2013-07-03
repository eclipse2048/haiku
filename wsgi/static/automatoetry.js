// Disclaimer etc.

jQuery(document).ready( function() {

	console.log("/do Document ist ready."); //DEBUG

	// Funktion, die die Kinder der juengsten Generation zur Tabelle hinzufuegt
	function addTableRow(jsonData) {
		// juengste Tabellenzeile auswaehlen
		jQuery("tr.latest")
			// Kind-Haikus einfuegen
			.html("\
				<td class=\"genCount\">" + jsonData[2] + "</td>\
				<td align=\"center\" class=\"phenotype\" title=\"Seedwort: " + jsonData[0][0] + " \nGene: " + jsonData[0][1] + "\">" + jsonData[0][2].split("\n").join("<br />") + "</td>\
				<td align=\"center\" class=\"phenotype\" title=\"Seedwort: " + jsonData[1][0] + " \nGene: " + jsonData[1][1] + "\">" + jsonData[1][2].split("\n").join("<br />") + "</td>")
			// tr.latest zu tr.older machen
			.attr("class", "older")
			// neue juengste Tabellenzeile erzeugen
			.after("<tr class=\"empty\"><br /></tr><tr class=\"latest\" />");

		// nach unten scrollen
		jQuery("html,body").animate({ scrollTop: jQuery("body").css("height") });
	};

	var finished1, finished2;
	jQuery("#loading").show();

	// Initialen Ajax-Request Teil 1 abschicken (Phaenotyp der Ausgangsgeneration)
	jQuery.ajax({
		type: "POST",
		data: {query: 0},
		dataType: "json",

		success: function(jsonData) {
			console.log("/do Initialer Ajax-Aufruf Teil 1 -> Success-Function: jsonData ist " + jsonData.split("\n").join("<br />")); //DEBUG
			jQuery("tr.parent td.phenotype").html(jsonData.split("\n").join("<br />"));
		},

		error: function(xhr, status, error) {
			console.log("/do Initialer AJAX-Aufruf Teil 1 fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
			jQuery("div.errorMsg").html('<p class="errorMsg">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte versuchen Sie es erneut.</p>'); // @TODO: Reload-Link angeben
		},

		complete: function() {
			finished1 = true;
			if (finished1 && finished2) { jQuery("#loading").hide(); };
		}
	});

	// Initialen Ajax-Request Teil 2 (Phaenotypen Ausgangsgeneration +1) abschicken
	jQuery.ajax({
		type: "POST",
		data: {query: 1},
		dataType: "json",

		success: function(jsonData) {
			console.log("/do Initialer Ajax-Aufruf Teil 2 -> Success-Function: jsonData ist", jsonData); //DEBUG
			addTableRow(jsonData); // Kinder-Zeile hinzufuegen

			// Button-Zeile hinzufuegen
			jQuery("tr.latest").after('<tr class="button-row"><td /><td><form method="post"><input class="button" type="submit" value="Linkes Kind-Gedicht" id="l" /></form></td><td><form method="post"><input class="button" type="submit" value="Rechtes Kind-Gedicht" id="r" /></td></form></tr>');
		},

		error: function(xhr, status, error) {
			console.log("/do Initialer AJAX-Aufruf Teil 2 fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
			jQuery("div.errorMsg").html('<p class="errorMsg">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte versuchen Sie es erneut.</p>'); // @TODO: Reload-Link angeben
		},

		complete: function() {
			finished2 = true;
			if (finished1 && finished2) { jQuery("#loading").hide(); };
		}
	});


	// Definiere Event-Handler fuer die Kind-Buttons
	jQuery("table").on("click", "tr.button-row input.button", function() {
		// evtl. Fehlermeldung loeschen
		jQuery("div.errorMsg").html("");

		// Warteanimation einfuegen
		jQuery("tr.latest").html("<td colspan=\"3\"><div align=\"center\" id=\"loading\" style=\"display:block\"><img src=\"/static/ajax-loader.gif\" /></div></td>");

		var callButton = jQuery(this).attr("id");
		var lr = (callButton == "l") ? 1 : 0;

		// nichtausgewaehltes Kind verstecken
		jQuery("tr.older:last td.phenotype").eq(lr).hide();
		jQuery("tr.older:last td.phenotype").eq(1-lr).attr("colspan", "2"); // mit .animate() in die Mitte sliden?

		// Sende AJAX-Request
		jQuery.ajax({
			type: "POST",
			data: {query: callButton},
			dataType: "json",

			success: function(jsonData) {
				console.log("input.button click()-Handler Success-Function: jsonData ist", jsonData); //DEBUG

				// verstecktes Kind loeschen
				jQuery("tr.older:last td.phenotype").eq(lr).remove();
				addTableRow(jsonData);
			},

			error: function(xhr, status, error) {
				console.log("/do AJAX-Aufruf fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
				jQuery("div.errorMsg").html('<p class="errorMsg">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte führen Sie Ihre Aktion erneut aus oder laden Sie neu.</p>');

				// verstecktes Kind wieder anzeigen
				jQuery("tr.older:last td.phenotype").eq(1-lr).removeAttr("colspan");
				jQuery("tr.older:last td.phenotype").eq(lr).show();
			},

			complete: function() {	jQuery("#loading").hide(); },
		});
		return false;
	});
});
