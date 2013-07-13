1. Fragen zu Automatoetry
=========================

1.1 Was ist Automatoetry?
-------------------------

Automatoetry ist der Versuch, aus dem Zusammenspiel von computerisiertem Ausprobieren und dem menschlichen Sinn für Schönheit heraus Poesie zu erschaffen. Ob es klappt? Ich habe keine Ahnung.

Das Medium der Wahl sind Haikus, eine japanische Gedichtform, die aus drei Zeilen mit 5, 7 und 5 Silben besteht.


1.2 Wie ist das Projekt entstanden?
-----------------------------------

Die Grundidee hatte ich bei der Lektüre von Richard Dawkins' "Der Blinde Uhrmacher". Dawkins beschreibt darin, wie er mit sogenannten Isomorphen experimentiert, Baumstrukturen, die von einem genetischen Algorithmus erzeugt werden. Durch zufällige Mutationen ihrer Gene verändern die Isomorphe ihre Gestalt und wandeln sich von simplen Graphen zu Insekten, Skorpionen oder Hüten.

Als ich das las, wollte ich ein ähnliches Programm schreiben, allerdings nicht mit Tierchen, sondern mit Text. Ich bin schließlich Schriftsteller.


1.3 Ist Automatoetry Open Source?
----------------------------------

Ja. Der gesamte Quellcode des Projekts steht unter der Gnu Public License (GPL), das heißt, er ist frei kopierbar, darf nicht kommerziell verwendet werden, yadda yadda yadda.

Der Quellcode ist über [Github](https://github.com/tradloff/haiku) zugänglich.


1.4 Und du hast das wirklich alles allein geschrieben?
-------------------------------------------------------

Ja.


1.5 Wow.
---------

Aber nicht doch.


2. Fragen zur Bedienung
=======================

2.1 Wie funktioniert Automatoetry genau?
----------------------------------------

Im Herzen von Automatoetry liegt ein genetischer Algorithmus, der Haikus erzeugen und zufällig mutieren lassen kann. Die hervorgebrachten "Kind"-Haikus sind ihrem Elter ähnlich, aber nicht komplett gleich; sie können sich in Details unterscheiden oder zur Gänze.

Aufgabe des Benutzers ist es, aus den vorgeschlagenen Kind-Gedichten das schönere herauszusuchen. Von diesem werden neue Kinder erzeugt, der Nutzer wählt wieder aus und so weiter.


2.2 Was muss ich machen?
------------------------

In jeder Generation hast du zwei Haikus zur Auswahl. Ihr jeweiliger Genotyp ist eine Mutation des Genotyps der vorigen Generation. Gewissermaßen handelt es sich also um Kinder des Haikus in der Zeile darüber.

Über die Buttons "Linkes/Rechtes Kind-Gedicht" suchst du eines der beiden Haikus aus. Dein Favorit ist das "überlebende" Haiku seiner Generation und darf sich "fortpflanzen", sprich: zwei Kinder hervorbringen, deren Genotyp erneut mutierte Versionen des Genotyps ihres Elters sind. Im Sinne der Evolutionstheorie bist du die Selektion, also das personifizierte "Survival of the Fittest".


2.3 Welches Haiku soll ich wählen?
----------------------------------

Dafür gibt es kein festes Kriterium und schon gar keinen Zwang. Nimm das, das dir besser gefällt. Oder das mehr Sinn ergibt als das andere, oder weniger Sinn. Oder das dich anspricht, ohne dass du sagen kannst, warum. Es ist ganz egal. Es gibt keinen Schiedsrichter, keine Punkte, keine Geschmackspolizei. Das Haiku soll dir gefallen, mehr nicht. Und wenn alles gut geht, stößt du irgendwann auf ein Gedicht, das tatsächlich schön ist (was immer das heißt).


2.4 Was hat es mit diesem "Startwort" und "Genen" auf sich?
-------------------------------------------------------

Sie sind die rohen Informationen, aus denen der Algorithmus ein Haiku erschafft. Biologisch gesprochen sind Startwort und Gene der Genotyp, während das Gedicht selbst den Phänotyp darstellt.

Die Gene bestehen aus 5, 7 und 5 Kleinbuchstaben (einer für jede Silbe). Das Startwort gibt die Richtung vor, die das Gedicht inhaltlich einschlägt. Ändern sich Gene und/oder Startwort, so ändert sich (in der Regel) auch das Haiku selbst. Zufällige Mutationen im Genotyp führen dadurch zu neuen und vor allem unerwarteten Effekten.

Tipp: Wenn du mit der Maus über ein beliebiges Haiku fährst, wird der Genotyp dafür angezeigt.


2.5 Warum kann ich unter verschiedenen Algorithmen auswählen?
----------------------------------------------------------

Ich habe verschiedene Strategien ausprobiert, um aus einem Geno- einen Phänotyp zu erzeugen. Im Moment ist *LRColloc* der beste (und einzige) Algorithmus, der die Anforderungen zumindest zum Teil erfüllt. Zu diesen Anforderungen gehören unter anderem die Sinnhaftigkeit der erzeugten Haikus, die Variabilität (ähnliche Mutationen sollten zu unterschiedlichen Gedichten führen) und eine halbwegs zügige Laufzeit.

Neben *LRColloc* sind noch viele weitere Algorithmen denkbar, um aus dem Geno- den Phänotyp zu erzeugen. Demnächst will ich den *TextRank*-Algorithmus unter die Lupe nehmen. Und zu Debugzwecken habe ich häufig *Loremipsum* benutzt, bei dem alle Haikus den gleichen, hartcodierten Inhalt haben. Langweilig, aber rasend schnell :-)


2.6 Wie genau erzeugt ein Algorithmus ein Haiku?
---------------------------------------------

Gute Frage. Tatsächlich ist das der Knackpunkt des gesamten Programms. Hier ist die Arbeitsweise von *LRColloc*:

* Setze Startwort an eine zufällige Position in Zeile 1.
* Fülle die Zeile in beide Richtungen mit Links- bzw. Rechtskollokationen auf. Höre auf, wenn alle Worte zusammen fünf Silben haben.
* Verfahre genauso mit Zeile 2 und 3, mit einem Unterschied: Nimm als Startwort ein Synonym oder verwandtes Wort des Startworts aus der vorherigen Zeile.

(Eine Kollokation ist ein Paar von Worten, die überdurchschnittlich häufig direkt nebeneinander stehen.)

Daneben sind unzählige weitere Möglichkeiten denkbar, um aus einem Startwort und 17 Genen ein Haiku zu erzeugen. Man könnte die einzelnen Zeile statt aus Wörtern aus Silben (oder gar einzelnen Buchstaben) zusammensetzen, oder von einem längeren Text ausgehend die Wortzahl reduzieren, oder oder oder.


2.7 Wann endet das Programm?
------------------------

Wie bei der echten Evolution gibt es kein festgelegtes Ziel. Vielmehr geht es ums Experimentieren und um den Spaß an der Sprache. Idealerweise kommt nach vielen Generationen ein "schönes" Haiku heraus, also eins, das mehr oder weniger künstlerisch ist. In der [Galerie](/gallery) sammle ich die schönsten mit Automatoetry geschriebenen Gedichte. Vielleicht kommt deins ja bald dazu.


3. Probleme
=================================

3.1 Warum sehe ich so viele Serverfehler?
-------------------------------

Für die Wort-Operationen greift Automatoetry auf den [Wortschatz](http://wortschatz.uni-leipzig.de/) der Universität Leipzig zurück. Wortschatz stellt Funktionen zur Verfügung, mit denen ich zum Beispiel nach Synonymen und Kollokationen suchen kann. Ich rufe diese Funktionen über eine API (Application Programming Interface) auf. Im Prinzip rufe ich eine bestimmte URL auf und bekomme anstatt einer HTML-Seite eine Liste von Wörtern zurück.

Nun kann es passieren, dass die Anfrage den Wortschatz-Server nicht oder in verstümmelter Form erreicht, oder dass der Server überlastet ist. In diesem Fall bekommt Automatoetry anstatt der angeforderten Daten eine Fehlermeldung zurück und muss die aktuelle Berechnung abbrechen.

Ob und wie oft das geschieht, kann ich leider nicht beeinflussen. Manchmal meldet Automatoetry auch nach dem dritten oder fünften Versuch den gleichen Fehler. In diesem Fall hilft nur Geduld; nach ein oder zwei Minuten klappt es meistens wieder. Insgesamt ist der Wortschatz-Server aber recht zuverlässig, und das Wortschatz-Team hat mir für Automatoetry sogar eine eigene Benutzerkennung eingerichtet.


3.2 Warum sind manche Wörter so komisch?
-------------------------------------

Auch hieran ist gewissermaßen der [Wortschatz](http://wortschatz.uni-leipzig.de/) schuld. Grundlage des Projekts ist eine große Sammlung von Zeitungsartikeln, Büchern, Redemanuskripten und vielen anderen Texten aus den verschiedensten Zeiten und Kontexten. Jedes Wort, das in dieser Textsammlung vorkommt, kann in den Haikus auftauchen, auch alte, ungebräuchliche, abgekürzte usw.


3.3 Warum ist das Programm so langsam?
----------------------------------

Die kurze Antwort: Der Wortschatz ist schuld, und das Internet.

Die etwas weniger kurze Antwort: Um ein Haiku zu erzeugen, stellt Automatoetry um die zehn Anfragen an die Wortschatz-API. Jede Generation umfasst zwei Exemplare, macht 20 Anfragen. Jede Anfrage wird nach Leipzig geschickt, dort bearbeitet (was bis zu einigen Sekunden dauern kann) und die Antwort zurückgegeben. Geschätzte anderthalb Millisekunden gehen außerdem dafür drauf, dass NSA und GCHQ die Daten überprüfen. Nach dem Motto: Ist das Kunst oder gehört das gespeichert?


4. Technische Fragen
======================

4.1 In welcher Programmiersprache ist Automatoetry geschrieben?
-----------------------------------------------------------

Das Programm ist in Python und ein wenig JavaScript geschrieben. Als Web-Framework verwende ich Web.py, als Datenbank MySQL, die Ajax-Aufrufe laufen über jQuery und das CSS-Template stammt von [Rambling Soul](http://ramblingsoul.com/). Gehostet wird das Programm auf [Openshift.com](http://www.openshift.com/).


4.2 Was steckt noch alles unter der Haube, von Python abgesehen?
------------------------------------------------------------

Du willst es genau wissen? Kannst du haben. Die Abhängigkeiten von Automatoetry lauten:

* [Python](http://www.python.org) 2.6
* [Web.py](http://webpy.org) 0.37
* [libleipzig](https://pypi.python.org/pypi/libleipzig/1.3) 1.3
* [mysql-python](http://sourceforge.net/projects/mysql-python/) 1.2.3
* [python-markdown](http://docutils.sourceforge.net/) 0.8.1

Darüber hinaus benötigt das Programm Zugriff auf:

* eine [MySQL](https://www.mysql.com/)-Datenbank
* [jQuery](http://www.jquery.com/) 1.10
* die [Wortschatz-API](http://wortschatz.uni-leipzig.de/) der Uni Leipzig (via Modul libleipzig)
* [wordreference.com](http://www.wordreference.com/) für das Zufallswort
* Der deutsche Stopwort-Corpus stammt aus dem [Natural Language Toolkit (NLTK)](http://www.nltk.org/>).


4.3 Listest du deshalb jede einzelne Ressource auf, weil du so stolz auf das Programm bist?
---------------------------------------------------------------------------------------

Unter anderem, ja.


4.4 Welche Ideen möchtest du mit Automatoetry noch umsetzen?
----------------------------------------------------------

Ich arbeite derzeit an einer zweiten Funktion, die Phänotypen (Haikus) erzeugt. Die Grundlage wird möglicherweise der TextRank-Algorithmus, eine Weiterentwicklung von Googles PageRank.

Außerdem würde ich mich freuen, wenn Automatoetry auch in andere Sprachen übersetzt würde. Da die Wortschatz-API nur in deutscher Sprache zu finden, lautet der erste Schritt, eine alternative Wortdatenbank oder ein vergleichbares Hilfsmittel zu finden, das die Erzeugung von Haikus in der Zielsprache möglich macht.


4.5 Wie kann ich dabei helfen?
---------------------------

Hier sind ein paar Ideen:

* Durch Lob, Kritik und Anregungen.
* Dadurch, dass du Automatoetry benutzt und deine Ergebnisse in die Galerie einstellst.
* Durch Mitmachen (siehe 4.4).
* Dadurch, dass du auf Automatoetry verlinkst.
* Dass du Bugs meldest oder sie selbst behebst.
* Dass du im Quellcode herumstöberst, damit herum experimentierst, ihn verbesserst oder meinetwegen auch verschlechterst (so funktioniert Open Source nun mal).
* Dadurch, dass du meine Bücher kaufst.
* Dadurch, dass du Spaß mit Automatoetry hast.
