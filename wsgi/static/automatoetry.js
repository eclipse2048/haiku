// Disclaimer etc.

jQuery(document).ready( function() {

	console.log("/do Document ist ready."); //DEBUG

	// fuegt die Kinder der juengsten Generation zur Tabelle hinzu
	function addTableRow(jsonData) {
		console.log("/do This is addTableRow()"); //DEBUG
		jQuery("tr.latest")
			// Kind-Haikus nebeneinander in 'latest'-Zeile einfuegen (mit Tooltips)
			.html("\
				<td class=\"genCount\">" + jsonData[2] + "</td>\
				<td align=\"center\" class=\"child\" title=\"Seedwort: " + jsonData[0][0] + "\nGene: " + jsonData[0][1] + "\">" + jsonData[0][2] + "</td><td align=\"center\" class=\"child\" title=\"Seedwort: " + jsonData[1][0] + "\nGene: " + jsonData[1][1] + "\">" + jsonData[1][2] + "</td>")
			// tr.latest wird zu tr.older
			.attr("class", "older")
			// neue juengste Tabellenzeile erzeugen
			.after("<tr class=\"empty\"><br /></tr><tr class=\"latest\" />");

		// nach unten scrollen
		jQuery("html,body").animate({ scrollTop: jQuery("body").css("height") });
	};


	// Initialen Ajax-Request abschicken
	jQuery.ajax({
		type: "POST",
		data: {child: 0},
		dataType: "json",

		success: function(jsonData) {
			console.log("/do Initialer Request -> Success-Function: jsonData ist", jsonData); //DEBUG
			addTableRow(jsonData); // Kinder-Zeile hinzufuegen

			// Button-Zeile hinzufuegen
			jQuery("tr.latest").after('<tr class="button-row"><td /><td><form method="post"><input class="button" type="submit" value="Linkes Kind-Gedicht" id="l" /></form></td><td><form method="post"><input class="button" type="submit" value="Rechtes Kind-Gedicht" id="r" /></td></form></tr>');
		},

		error: function(xhr, status, error) {
			console.log("/do Initialer AJAX-Aufruf fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
			jQuery("div.errorMsg").html('<p class="errorMsg">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte versuchen Sie es erneut.</p>'); // @TODO: Reload-Link angeben
		},

		complete: function() {	jQuery("#loading").hide(); },
	});


	// Definiere Event-Handler fuer die Kind-Buttons
	jQuery("table").on("click", "tr.button-row input.button", function() {
		// evtl. Fehlermeldung loeschen
		jQuery("div.errorMsg").html("");

		// Warteanimation einfuegen
		jQuery("tr.latest").html("<td colspan=\"3\"><div align=\"center\" id=\"loading\"><img src=\"/static/ajax-loader.gif\" /></div></td>");

		var callButton = jQuery(this).attr("id");
		var lr = (callButton == "l") ? 1 : 0;

		// nichtausgewaehltes Kind verstecken
		jQuery("tr.older:last td.child").eq(lr).hide();
		jQuery("tr.older:last td.child").eq(1-lr).attr("colspan", "2"); // mit .animate() in die Mitte sliden?

		// Sende AJAX-Request an Python-Backend
		// Ich uebergebe die ID des Buttons ("l" oder "r") und erhalte dafuer ein JSON-Objekt mit den neuen Kindern
		jQuery.ajax({
			type: "POST",
			data: {child: callButton},
			dataType: "json",

			success: function(jsonData) {
				console.log("input.button click()-Handler Success-Function: jsonData ist", jsonData); //DEBUG

				// verstecktes Kind loeschen
				jQuery("tr.older:last td.child").eq(lr).remove();

				addTableRow(jsonData);
			},

			error: function(xhr, status, error) {
				console.log("/do Initialer AJAX-Aufruf fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
				jQuery("div.errorMsg").html('<p class="errorMsg">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte führen Sie Ihre Aktion erneut aus oder laden Sie neu.</p>');

				// verstecktes Kind wieder anzeigen
				jQuery("tr.older:last td.child").eq(1-lr).removeAttr("colspan");
				jQuery("tr.older:last td.child").eq(lr).show();
			},

			complete: function() {	jQuery("#loading").hide(); },
		});
		return false;
	});
});
