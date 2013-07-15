// Disclaimer etc.

jQuery.support.cors = true;

jQuery(document).ready( function() {

	var finished1, finished2, errorType, errorTarget;
	jQuery("#loading").show();

	// Fuegt die Kinder der juengsten Generation der Tabelle hinzu
	function addTableRow(jsonData) {
		jQuery("tr.latest")
			// Kind-Haikus einfuegen
			.html('<th class="genCount">' + jsonData[2] + '</th>\
				<td align="center" class="phenotype" title="Startwort: ' + jsonData[0][0] + ' \nGene: ' + jsonData[0][1] + '">' + jsonData[0][2].split('\n').join('<br />') + '</td>\
				<td align="center" class="phenotype" title="Startwort: ' + jsonData[1][0] + ' \nGene: ' + jsonData[1][1] + '">' + jsonData[1][2].split('\n').join('<br />') + '</td>\
				<td class="share"><form method="post"><input class="button" type="submit" value="andere Kinder erzeugen" id="newKids" /></form></td>')
			// tr.latest zu tr.older machen
			.attr("class", "older")
			// neue juengste Tabellenzeile erzeugen
			.after('<tr class="empty"><br /></tr><tr class="latest" />');

		// nach unten scrollen (aber nicht ganz)
		var heightStr = jQuery("div#pagecontent").css("height");
		var matches = heightStr.match(/\d+/);
		var height = parseInt(matches[0], 10);
		jQuery("html, body").animate({ scrollTop: (height-80) + "px" });
	};

	// Initialen Ajax-Request Teil 1 abschicken (Phaenotyp der Ausgangsgeneration)
	jQuery.ajax({
		type: "POST",
		data: {query: "genZero"},
		dataType: "json",

		success: function(jsonData) {
			console.log("/haiku Initialer Ajax-Aufruf Teil 1 -> Success-Function: jsonData ist " + jsonData.split("\n").join("<br />")); //DEBUG

			// Phaenotyp einfuegen
			jQuery("tr.genZero td.phenotype").html(jsonData.split("\n").join("<br />"));

			// Daten fuer die Share-Funktion sammeln
			var content = jQuery("tr.genZero td.phenotype").html();
			var generation = jQuery("tr.genZero th.genCount").html();
			var genotype = new String(jQuery("tr.genZero td.phenotype").attr("title"));
			var lineBreakPos = genotype.indexOf("\n")
			var seedword = genotype.substring(11, lineBreakPos-1);
			var genes = genotype.substring(lineBreakPos+7)

			// Share-Button einfuegen
			jQuery("tr.genZero td.share").html('<form method="post" action="/share" target="_blank">\
				<input name="content" type="hidden" value="' + content + '" />\
				<input name="generation" type="hidden" value="' + generation + '" />\
				<input name="seedword" type="hidden" value="' + seedword + '" />\
				<input name="genes" type="hidden" value="' + genes + '" />\
				<input class="button" type="submit" value="in Galerie aufnehmen" />\
			</form>');
		},

		error: function(xhr, status, error) {
			console.log("/haiku Initialer AJAX-Aufruf Teil 1 fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
			jQuery("div.errorMsg").html('<p class="highlight">\
				Ein Fehler ist aufgetreten: ' + error + '<br />\
				Bitte versuchen Sie es <a href="" class="errorReload">erneut</a>.\
			</p>');
		},

		complete: function() {
			finished1 = true;
			if (finished1 && finished2) { jQuery("#loading").hide(); };
		}
	});

	// Initialen Ajax-Request Teil 2 (Phaenotypen Ausgangsgeneration +1) abschicken
	jQuery.ajax({
		type: "POST",
		data: {query: "newKids"},
		dataType: "json",

		success: function(jsonData) {
			console.log("/haiku Initialer Ajax-Aufruf Teil 2 -> Success-Function: jsonData ist", jsonData); //DEBUG

			// Kinder-Zeile hinzufuegen
			addTableRow(jsonData);

			// Button-Zeile hinzufuegen
			jQuery("tr.latest").after('<tr class="button-row">\
				<td class="genCount"/>\
				<td><form method="post"><center><input class="button" type="submit" value="Linkes Kind-Gedicht" id="l" /></center></form></td>\
				<td><form method="post"><input class="button" type="submit" value="Rechtes Kind-Gedicht" id="r" /></form></td>\
				<td class="share">&nbsp;</td>\
			</tr>');
		},

		error: function(xhr, status, error) {
			console.log("/haiku Initialer AJAX-Aufruf Teil 2 fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
			jQuery("div.errorMsg").html('<p class="highlight">\
				Ein Fehler ist aufgetreten: ' + error + '<br /> \
				Bitte versuchen Sie es <a href="" class="errorReload">noch einmal</a>.\
			</p>');
		},

		complete: function() {
			finished2 = true;
			if (finished1 && finished2) { jQuery("#loading").hide(); };
		}
	});

	jQuery("div.errorMsg").on("click", "a.errorReload", function() { location.reload(); });

	jQuery("div.errorMsg").on("click", "a.errorRetrigger", function() {
		if (errorType && errorTarget) {
			jQuery(errorTarget).trigger(errorType);
			return false;
		} else { location.reload(); }
	});

	// Definiere Event-Handler fuer Kind-Buttons
	jQuery("table").on("click", "tr.button-row input.button", function(event) {
//	jQuery("table.haiku:not(.disabled)").on("click", "tr.button-row input.button", function(event) {

		// Klasse "disabled" zu Tabelle hinzufügen, um weiteren Buttonclicks zuvorzukommen
//		jQuery("table.haiku").addClass("disabled");

		// Event-Daten speichern fuer Retrigger-Link
		errorType = event.type;
		errorTarget = event.target;

		// evtl. Fehlermeldung loeschen
		jQuery("div.errorMsg").html("");

		// Warteanimation einfuegen
		jQuery("tr.latest").html('<td /><td colspan="2"><div align="center" id="loading" style="display:block"><img src="/static/ajax-loader.gif" /></div></td><td />');

		// Button-Identifier festhalten
		var callButton = jQuery(this).attr("id");
		var lr = (callButton == "l") ? 1 : 0;

		// nichtausgewaehltes Kind verstecken
		jQuery("tr.older:last td.phenotype").eq(lr).hide();
		jQuery("tr.older:last td.phenotype").eq(1-lr).attr("colspan", "2"); // mit .animate() in die Mitte sliden?

		// Neue-Kinder-Button verstecken
		jQuery("tr.older:last td.share").hide();

		// AJAX-Request senden
		jQuery.ajax({
			type: "POST",
			data: {query: callButton},
			dataType: "json",

			success: function(jsonData) {
				console.log("/haiku Kind-Button click()-Handler Success-Function: jsonData ist", jsonData); //DEBUG

				// verstecktes Kind loeschen
				jQuery("tr.older:last td.phenotype").eq(lr).remove();

				// Daten fuer die Share-Funktion sammeln
				var content = jQuery("tr.older:last td.phenotype").html();
				var generation = jQuery("tr.older:last th.genCount").html();
				var genotype = new String(jQuery("tr.older:last td.phenotype").attr("title"));
				var lineBreakPos = genotype.indexOf("\n")
				var seedword = genotype.substring(11, lineBreakPos-1);
				var genes = genotype.substring(lineBreakPos+7)

				// Share-Button einfuegen
				jQuery("tr.older:last td.share").html('<form method="post" action="/share" target="_blank">\
					<input name="content" type="hidden" value="' + content + '" />\
					<input name="generation" type="hidden" value="' + generation + '" />\
					<input name="seedword" type="hidden" value="' + seedword + '" />\
					<input name="genes" type="hidden" value="' + genes + '" />\
					<input class="button" type="submit" value="in Galerie aufnehmen" />\
				</form>')
				.show();

				// Kind-Zeile hinzufuegen
				addTableRow(jsonData);
			},

			error: function(xhr, status, error) {
				console.log("/haiku AJAX-Aufruf fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
				jQuery("div.errorMsg").html('<p class="highlight">\
					Ein Fehler ist aufgetreten: ' + error + '<br /> \
					Bitte führen Sie Ihre Aktion <a href="" class="errorRetrigger">erneut aus</a>.\
				</p>');

				// verstecktes Kind und Button wieder anzeigen
				jQuery("tr.older:last td.phenotype").eq(1-lr).removeAttr("colspan");
				jQuery("tr.older:last td.phenotype").eq(lr).show();
				jQuery("tr.older:last td.share").show();
			},

			complete: function() {
				jQuery("#loading").hide();
//				jQuery("table.haiku").removeClass("disabled");
			},
		});
		return false;
	});

	// Definiere Event-Handler fuer Neue-Kinder-Button
	jQuery("table").on("click", "tr.older:last input.button", function(event) {

		// Event-Daten speichern fuer Retrigger-Link
		errorType = event.type;
		errorTarget = event.target;

		// evtl. Fehlermeldung loeschen
		jQuery("div.errorMsg").html("");

		// Warteanimation einfuegen
		jQuery("tr.latest").html('<td /><td colspan="2"><div align="center" id="loading" style="display:block"><img src="/static/ajax-loader.gif" /></div></td><td />');

		// Kinder und Button verstecken
		jQuery("tr.older:last td").hide();

		// Sende AJAX-Request
		jQuery.ajax({
			type: "POST",
			data: {query: jQuery(this).attr("id")},
			dataType: "json",

			success: function(jsonData) {
				console.log("/haiku Neue-Kinder-Button click()-Handler Success-Function: jsonData ist", jsonData); //DEBUG

				// alte Kinder durch neue ersetzen
				jQuery("tr.older:last td.phenotype:first")
					.attr('title', 'Startwort: ' + jsonData[0][0] + ' \nGene: ' + jsonData[0][1])
					.html(jsonData[0][2].split('\n').join('<br />'))
					.show();
				jQuery("tr.older:last td.phenotype:last")
					.attr('title', 'Startwort: ' + jsonData[1][0] + ' \nGene: ' + jsonData[1][1])
					.html(jsonData[1][2].split('\n').join('<br />'))
					.show();
				jQuery("tr.older:last td.share").show();
			},

			error: function(xhr, status, error) {
				console.log("/haiku AJAX-Aufruf fehlgeschlagen: xhr, status, error sind ", xhr, status,  error);
				jQuery("div.errorMsg").html('<p class="highlight">\
					Ein Fehler ist aufgetreten: ' + error + '<br /> \
					Bitte führen Sie Ihre Aktion <a href="" class="errorRetrigger">erneut aus</a>.\
				</p>');

				// verstecktes Kind wieder anzeigen
				jQuery("tr.older:last td").show();
			},

			complete: function() {	jQuery("#loading").hide(); },
		});
		return false;
	});

	console.log("/haiku Document ist ready."); //DEBUG
});
