// Disclaimer etc.

jQuery(document).ready( function() {

	console.log("/do Document ist ready."); //DEBUG

	var genCount = 0;

	// fuegt die Kinder der juengsten Generation zur Tabelle hinzu
	function addTableRow(jsonData) {
		console.log("/do This is addTableRow()"); //DEBUG
		genCount += 1;
		jQuery("tr.latest")
			// Kind-Haikus nebeneinander in 'latest'-Zeile einfuegen (mit Tooltips)
			.html("\
				<td class=\"genCount\">" + genCount + "</td>\
				<td align=\"center\" class=\"child\" title=\"Seedwort: " + jsonData[0][0][0] + "\nGene: " + jsonData[0][0][1] + "\">" + jsonData[0][1] + "</td><td align=\"center\" class=\"child\" title=\"Seedwort: " + jsonData[1][0][0] + "\nGene: " + jsonData[1][0][1] + "\">" + jsonData[1][1] + "</td>")
			// tr.latest wird zu tr.older
			.attr("class", "older")
			// neue juengste Tabellenzeile erzeugen
			.after("<tr class=\"empty\"><br /></tr><tr class=\"latest\" />");
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
			jQuery("div.errorMsg").html('<p class="errorMsg">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte versuchen Sie es erneut.</p>');
		},
		complete: function() {	jQuery("#loading").hide(); },
	});

	// Definiere Event-Handler fuer die Kind-Buttons
	// Bemerke: .on() ordnet Handler auch bei nachtraeglicher Button-Erstellung zu
	jQuery("table").on("click", "tr.button-row input.button", function() {
		var callButton = jQuery(this).attr("id");
		console.log("/do input.button click()-Handler: callButton ist", callButton); //DEBUG

		// nichtausgewaehltes Kind loeschen
		switch (callButton) {
			case "l":
				// @TODO Haiku mit .hide("slow", function... ) ausblenden, ebenso bei case "r"
				jQuery("tr.older:last td.child").eq(1).remove();
				break;
			case "r":
				jQuery("tr.older:last td.child").eq(0).hide("slow").remove();
				break;
		};
		// ueberlebende Tabellenzeile verbreitern und zentrieren
		// @TODO ueberlebendes Haiku mit .animate() in die Mitte sliden
		jQuery("tr.older:last td.child").attr("colspan", "2").attr("align", "center");

		// Warteanimation einfuegen
		jQuery("tr.latest").html("<td colspan=\"3\"><div align=\"center\" id=\"loading\"><img src=\"/static/ajax-loader.gif\" /></div></td>");

		// Sende AJAX-Request an Python-Backend
		// Ich uebergebe die ID des Buttons ("l" oder "r") und erhalte dafuer ein JSON-Objekt mit den neuen Kindern
		jQuery.ajax({
			type: "POST",
			data: {child: callButton},
			dataType: "json",
			success: function(jsonData) {
				console.log("input.button click()-Handler Success-Function: jsonData ist", jsonData); //DEBUG
				addTableRow(jsonData);
				jQuery("html,body").animate({ scrollTop: jQuery("body").css("height") }); // nach unten scrollen
			},
			error: function(xhr, status, error) {
				console.log("/do Initialer AJAX-Aufruf fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
				jQuery("div.errorMsg").html('<p class="errorMsg">Ein Fehler ist aufgetreten: ' + error + '<br /> Bitte versuchen Sie es erneut.</p>');
			},
			complete: function() {	jQuery("#loading").hide(); },
		});
		return false;
	});
});
