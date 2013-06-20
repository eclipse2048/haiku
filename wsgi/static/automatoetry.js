// Disclaimer etc.

jQuery(document).ready( function() {

	console.log("ready() Function: Hi"); //DEBUG

	// fügt die Kinder der jüngsten Generation zur Tabelle hinzu
	function addTableRow(jsonData) {
		console.log("addTableRow(): Hi"); //DEBUG
		jQuery("tr.latest")
			// Kind-Haikus nebeneinander in 'latest'-Zeile einfügen (mit Tooltips)
			.html("<td align=\"center\" title=\"Seedwort: " + jsonData[0][0][0] + "\nGene: " + jsonData[0][0][1] + "\">" + jsonData[0][1] + "</td><td align=\"center\" title=\"Seedwort: " + jsonData[1][0][0] + "\nGene: " + jsonData[1][0][1] + "\">" + jsonData[1][1] + "</td>")
			// tr.latest wird zu tr.older
			.attr("class", "older")
			// neue jüngste Tabellenzeile erzeugen
			.after("<tr class=\"empty\"><br /></tr><tr class=\"latest\" />");
	};

	// Initialen Ajax-Request abschicken
	jQuery.ajax({
		type: "POST",
		data: {child: 0},
		dataType: "json",
		success: function(jsonData) {
			console.log("Initialer Request/Success-Function: jsonData ist", jsonData); //DEBUG
			addTableRow(jsonData); // Kinder-Zeile hinzufügen

			// Button-Zeile hinzufügen
			jQuery("tr.latest").after('<tr class="button-row"><td><form method="post"><input class="button" type="submit" value="Linkes Tochter-Gedicht" id="l" /></form></td><td><form method="post"><input class="button" type="submit" value="Rechtes Tochter-Gedicht" id="r" /></td></form></tr>');
		},
	});

	// Definiere Event-Handler für die Kind-Buttons
	// Bemerke: .on() ordnet Handler auch bei nachträglicher Button-Erstellung zu
	jQuery("table").on("click", "tr.button-row input.button", function() {
		var callButton = jQuery(this).attr("id");
		console.log("input.button click()-Handler: callButton ist", callButton); //DEBUG

		// nichtausgewähltes Kind löschen
		switch (callButton) {
			case "l":
				// @TODO Haiku mit .hide("slow", function... ) ausblenden, ebenso bei case "r"
				jQuery("tr.older:last td").eq(1).remove();
				break;
			case "r":
				jQuery("tr.older:last td").eq(0).hide("slow").remove();
				break;
		};
		// überlebende Tabellenzeile verbreitern und zentrieren
		// @TODO überlebendes Haiku mit .animate() in die Mitte sliden
		jQuery("tr.older:last td").attr("colspan", "2").attr("align", "center");

		// Warteanimation einfügen
		// @TODO kann ich das Ladebildchen auch via CSS anzeigen? Dann könnte ich auf den <img>-Tag verzichten (desgleichen im Template)
		jQuery("tr.latest").html("<td colspan=\"2\"><div align=\"center\" id=\"loading\"><img src=\"/static/ajax-loader.gif\" /></div></td>");

		// Sende AJAX-Request an Python-Backend
		// Ich übergebe die ID des Buttons ("l" oder "r") und erhalte dafür ein JSON-Objekt mit den neuen Kindern
		jQuery.ajax({
			type: "POST",
			data: {child: callButton},
			dataType: "json",
			success: function(jsonData) {
				console.log("input.button click()-Handler Success-Function: jsonData ist", jsonData); //DEBUG
				addTableRow(jsonData);
				jQuery("html,body").animate({ scrollTop: jQuery("body").css("height") }); // nach unten scrollen
			},
		});
		return false;
	});

	// Event-Handler für die Warteanimation setzen
	jQuery("#loading").ajaxStart(function(){
		jQuery(this).show();
	}).ajaxStop(function(){
		jQuery(this).hide();
	});
});
