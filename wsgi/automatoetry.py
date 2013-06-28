#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  automatoetry.py
#
#  Copyright 2013 Tobias Radloff <mail@tobias-radloff.de>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from __future__ import division, absolute_import # Aufwaertskompatibilitaet
import string
import random
import sys
import os
import traceback
from libleipzig import Thesaurus, LeftNeighbours, RightNeighbours, Similarity, Baseform
from httplib import HTTPConnection

# Umgebungsvariablen mit Credentials fuer die Wortschatz-API einlesen
WORTSCHATZ_CREDENTIALS = ("anonymous", "anonymous")
#if os.environ.has_key("WORTSCHATZ_USER") and os.environ.has_key("WORTSCHATZ_PASSWORD"):
#	WORTSCHATZ_CREDENTIALS = (os.environ["WORTSCHATZ_USER"], os.environ["WORTSCHATZ_PASSWORD"])

# Konstanten fuer die Silbenzaehlung
VOWELS_DE = u"aeiouyäoü"
u"""Vokale der deutschen Sprache, einschliesslich "y" und Umlaute.
"""

ONE_SYLLABLE_COMBINATIONS = [u"aa", u"ae", u"ai", u"ao", u"au", u"ay", u"ee", u"ei", u"eu", u"ey", u"ie", u"ii", u"oe", u"oo", u"ou", u"oy", u"ue", u"ui", u"uo", u"uu", u"\xe4u"]
u"""Alle Kombinationen von zwei Vokalen, die in der deutschen Sprache
	als einsilbiger Laut behandelt werden.
"""

SYLLABLE_COUNT_EXCEPTIONS = {u"Pietät": 3, u"McDonald's": 3}
u"""Dictionary mit Woertern, die anders getrennt werden als nach den
	ueblichen Regeln. Bsp: Pi|e|taet statt Pie|taet. Das Wort ist der
	key, die tatsaechliche Silbenzahl der value des Dictionary.
"""


DEFAULT_SEEDWORD = u"werden"


class AutoPoemSpecimen:
	u"""@TODO: Einleitende Beschreibung fehlt.

		Der Genotyp ist eine List mit zwei Elementen. Das erste Element
		ist das Seedwort. Das zweite ist ein String mit drei Worten à 5,
		7 und 5 Zeichen, jeweils durch Leerzeichen voneinander getrennt.
		Die Zeichen stammen aus der Menge [a-z]. Die ersten fuenf
		Zeichen korrespondieren mit Zeile 1 des Phaenotyps (des Haiku-
		Gedichts), die letzten fuenf mit Zeile 3 und die mittleren
		sieben mit Zeile 2.
	"""

	def __init__(self, seedword=None, genes=None, parent=None, phenotype=""):
		u"""@TODO: Beschreibung fehlt
		"""
		self.__seedword = seedword or self.getRandomSeedword()
		# @TODO: Uebergebene Gene auf len==17 und ascii_lowercase ueberpruefen: r"^[a-z]{5} [a-z]{7} [a-z]{5}$"
		self.__genes = genes or self.getRandomGenes()
		self.__parent = parent
		self.__children = []
		self.__phenotype = phenotype # @TODO hier am besten gleich den Phaenotyp erzeugen; dazu muss die Fkt. aber schnell und zuverlaessig arbeiten. Nur weil die Develop-Funktionen z.T. so lange brauchen, gibt es ueberhaupt die Moeglichkeit, dem Konstruktor den Phaenotpyen zu uebergeben und eine zweite Phaenotyp-Erzeugung einzusparen.


	def getRandomGenes(self):
		u"""Erzeugt die Gene fuer ein zufaelliges Exemplar. Nuetzlich
			fuer die Erzeugung eines Startindividuums in Generation 1.
		"""
		genes = "".join([random.choice(string.ascii_lowercase) for i in range(17)])
		return genes[:5] + " " + genes[5:12] + " " + genes[12:]


	def getRandomSeedword(self):
		u"""Gibt ein zufaelliges Startwort zurueck.
		"""

		# Seite mit Zufallswort von Wordreference.com anfordern
		conn = HTTPConnection("www.wordreference.com")
#		conn.set_debuglevel(1) #DEBUG
		conn.putrequest("GET", "/random/deen")
		conn.putheader("accept-encoding", "utf-8")
		conn.putheader("user-agent", "python-httplib")
		conn.endheaders()
		resp = conn.getresponse()
		page = resp.read()
		conn.close()

		# Fehler abfangen
		if resp.status != 200:
			print "getRandomSeedword(): HTTP request fehlgeschlagen mit Status", resp.status, resp.reason
			return DEFAULT_SEEDWORD

		# Wort suchen und zurueckgeben
		wordStart = page.find('name="description" content="') + 28
		wordEnd = page.find(" ", wordStart)
		print "Zufallswort-Zeile lautet:", page[wordStart-10:wordEnd+30] #DEBUG
		word = page[wordStart:wordEnd].rstrip("-,").rstrip()
		try:
			word = word.decode("utf-8")
		except UnicodeEncodeError, u:
			pass
		print "getRandomSeedword(): Wort ist", word #DEBUG
		return word


	def getGenotype(self):
		u"""@TODO: Beschreibung fehlt
		"""
		return [self.__seedword, self.__genes]


	def getPhenotype(self, function=""):
		u"""@TODO: Beschreibung fehlt. Darin muss erwaehnt werden, dass
			diese Funktion Fehler weitergeben kann, die abgefangen
			werden müssen.

			Hier die alte Beschreibung von __develop():

			Dummy-Funktion. Ruft diejenige __develop...()-Funktion auf,
			deren Restname als Parameter uebergeben wird. __develop()
			als Dummy ermoeglicht es, unterschiedliche Phaenotyp-
			Algorithmen zu verwenden, ohne den Code zu veraendern
			(Ausnahme: Default-Fkt.).
		"""

		# Ist Phaenotyp schon erzeugt worden?
		if self.__phenotype != "":
			return self.__phenotype

		# Gut, dann erzeugen wir ihn eben jetzt
		functions, funcPrefix = self.getDevelopFunctionNames(), "_" + self.__class__.__name__ + "__develop"
		if function in functions:
			funcName = function
		else: # default
			funcName = "LR575Syllables" # @TODO: Default-Fkt. zur Instanzvariable mit Getter/Setter-Methoden machen

		print "Calling develop function '" + funcName + "()'" #DEBUG
		self.__phenotype = getattr(self, funcPrefix + funcName).__call__()
		return self.__phenotype


	def getParent(self):
		u"""@TODO: Beschreibung fehlt
		"""
		return self.__parent


	def getChildren(self):
		u"""@TODO: Beschreibung fehlt
		"""
		return self.__children


	def __sylCount(self, charList):
		u"""Rekursive Funktion, die die Zahl der Silben in einem Wort
			der deutschen Sprache ermittelt. Der Algorithmus sucht die
			naechste zusammenhaengenden Vokalkette und ueberprueft, ob
			diese eine oder mehrere Silben konstituiert.

			Das Eingabewort wird nicht als String erwartet, sondern als
			Liste von einzelnen Buchstaben, alle klein und mit
			umgewandelten Umlauten (z.B. 'ae' zu 'ae').
		"""
		if charList == []:
			return 0
		c, v = 0, []

		# naechste Kette von Vokalen finden
		while c < len(charList) and charList[c] not in VOWELS_DE:
			c += 1
		while c < len(charList) and charList[c] in VOWELS_DE:
			v.append(charList[c])
			c += 1

		# kein Vokal: keine Silbe
		if v == []:
			return 0
		# ein Vokal: eine Silbe
		elif len(v) == 1:
			return 1 + self.__sylCount(charList[c:])
		# zwei Vokale: eine oder zwei Silben
		elif len(v) >= 2:
			if "".join(v[:2]) in ONE_SYLLABLE_COMBINATIONS:
				return 1 + self.__sylCount(charList[c-len(v)+2:])
			else:
				return 1 + self.__sylCount(charList[c-len(v)+1:])


	def countSyllables(self, word):
		u"""Gibt die Zahl der Silben fuer ein deutsches Wort zurueck.
		"""
		# Wort ggf. in Unicode umwandeln
		try:
			word = word.decode("utf-8")
		except UnicodeEncodeError, u:
			pass

		# ist Wort in Liste mit Ausnahmen?
		if word in SYLLABLE_COUNT_EXCEPTIONS.keys():
			return SYLLABLE_COUNT_EXCEPTIONS[word]

		# Manchmal gibt libleipzig merere Worte als ein einzelnes zurueck
		if " " in word:
			return sum([self.__sylCount(list(w.strip().lower())) for w in word.split()])

		# Wort in Liste von Kleinbuchstaben umwandeln und ab dafuer
		return self.__sylCount(list(word.strip().lower()))


	def __char2int(self, c):
		u"""Gibt die Position des uebergebenen Buchstabens im Alphabet
			zurueck, bzw. 0 falls c kein Buchstabe ist.
		"""
		return string.ascii_lowercase.find(c.lower()) + 1


	def getDevelopFunctionNames(self):
		"""@TODO: Beschreibung fehlt
		"""
		classPrefix = "_" + self.__class__.__name__ + "__develop"
		l = len(classPrefix)
		return [f[l:] for f in dir(self) if f.startswith(classPrefix) and len(f) > l]


	def __developLoremipsum(self):
		u"""Gibt ein hartcodiertes Haiku zurueck. Gut fuers Debugging
			und wenn der Wortschatz-Server nicht erreichbar ist.
		"""
		return "Lorem Ipsum bla\nZeile braucht sieben Silben\nHassenichgesehn"


	# Funktion ist kaputt
	def __developLR575Words(self, genotype=[]):
		u"""Erzeugt aus einem Genotyp den dazugehoerigen Phaenotyp. Hier
			findet der schwierige Teil des gesamten Programms statt.

			Die Funktion entwickelt den uebergebenen Genotypen. Wird
			kein Genotyp uebergeben, nimmt sie den Genotyp der eigenen
			Instanz.

			__developLR575Words() erzeugt ein Haiku, das anstatt aus
			5-7-5 Silben aus 5-7-5 Woertern besteht. In jeder Zeile wird
			das Seedwort ermittelt und an die richtige Stelle gesetzt,
			danach wird die Zeile nach links und rechts mit
			Left/RightNeighbours aufgefuellt.
		"""

		if genotype == []:
			genotype = self.getGenotype()

		geneLines, phenotype, seedwordPos = genotype[1].split(), [], []

		# Position des Seedworts in der jeweiligen Zeile ermitteln.
		# Zurzeit nehme ich die Position des Gens mit dem hoechsten Wert
		for i in range(3):
			seedwordPos.append(geneLines[i].index(max(geneLines[i])))

		# nacheinander die drei Zeilen des Haikus erzeugen
		for i in range(3):

			# leere Zeile erzeugen
			line = []
			if i == 1:
				for j in range(7): line.append("")
			else:
				for j in range(5): line.append("")

			# Seedwort finden und in Zeile schreiben
			if i == 0:
				seedword = genotype[0]
			else:
				# das nicht benutzte Gen aus der vorigen Zeile hilft beim Erzeugen des Seedworts in dieser Zeile
				g = self.__char2int(geneLines[i-1][seedwordPos[i-1]])
				words = Thesaurus(genotype[0], g, ) # das g-te Thesaurusergebnis wird Seedwort
				seedword = words.pop()[0] # Thesaurus stellt das Synonymwort im Ergebnis an Pos. 0
			line.pop(seedwordPos[i])
			line.insert(seedwordPos[i], seedword)

			# Zeile nach links vervollstaendigen
			if seedwordPos[i] != 0:
				for j in range(seedwordPos[i]-1, -1, -1):
					words = LeftNeighbours(line[j+1], self.__char2int(geneLines[i][j]))

					if len(words) == 0: # pruefen, ob die Neighbours-Liste leer ist
						word = "Ersatz"
					else:
						word = words.pop()[0] # LeftNeighbours stellt das Nachbarwort im Ergebnis an Pos. 0

					line.pop(j)
					line.insert(j, word)

			# Zeile nach rechts vervollstaendigen
			if seedwordPos[i] != len(geneLines[i])-1:
				for j in range(seedwordPos[i]+1, len(geneLines[i])):
					words = RightNeighbours(line[j-1], self.__char2int(geneLines[i][j]))

					if len(words) == 0: # pruefen, ob die Neighbours-Liste leer ist
						word = "Ersatz"
					else:
						word = words.pop()[1] # RightNeighbours stellt das Nachbarwort im Ergebnis an Pos. 1

					line.pop(j)
					line.insert(j, word)

			phenotype.append(" ".join(line))

		p = "\n".join(phenotype)

		# Falls der Genotyp der Instanz entwickelt wurde: Phaenotyp speichern
		if genotype == self.getGenotype():
			self.__phenotype = p
		return p


	def __developLR575Syllables(self):
		u"""__developLR575Syllables() erzeugt ein Haiku aus 5-7-5
			Silben. Wie bei __developLR575Words() wird in jeder Zeile
			das Seedwort ermittelt und an die entsprechende Stelle
			gesetzt. Danach wird die Zeile nach links und rechts mit
			Left/RightNeighbours aufgefuellt, bis die gewuenschte
			Silbenanzahl erreicht ist. Falls nur noch eine Silbe frei
			ist und die Neighbours-Liste kein einsilbiges Wort enthaelt,
			nehme ich "und".

			Die Ergebnisse sind nicht voellig schlecht, aber:
			- Kinder haben zu wenig Varianz, vor allem bei
			ungewoehnlichen Seedworten mit wenigen Synonymen.
			- Oft ist der Phaenotyp einer oder beider Kinder identisch
			mit dem des Elter.
			- Nicht jede Mutation sorgt fuer eine sichtbare
			Veraenderung, und wenn es zu Veraenderungen kommt, betreffen
			sie oft die ganze Zeile.

			Schoener waere eine direkte Zuordnung Gen->Silbe, weil dann
			jede Mutation eine konkrete Phaenotypenveraenderung
			hervorrufen wuerde.
		"""
		print "LR575Syl: Credentials sind", WORTSCHATZ_CREDENTIALS #DEBUG
		geneLines, phenotype, seedwordPos = self.getGenotype()[1].split(), [], []

		# Position des Seedworts in der jeweiligen Zeile ermitteln. Zurzeit nehme ich die Position des Gens mit dem niedrigsten Wert
		for i in range(3):
			seedwordPos.append(geneLines[i].index(min(geneLines[i])))
		print "seedwordPos:", seedwordPos #DEBUG
		print "geneLines:", geneLines #DEBUG

		# nacheinander die drei Zeilen des Haikus erzeugen
		for i in range(3):

			# Seedwort ermitteln
			seedword = self.getGenotype()[0] # Zeile 0 und default
			if i != 0:
				g = self.__char2int(geneLines[i-1][seedwordPos[i-1]]) # das nicht benutzte Gen aus der vorigen Zeile hilft, das Seedwort dieser Zeile zu erzeugen
				if i == 1:
					lineSeed = self.getGenotype()[0]
					line1Seed = ""
				elif i == 2:
					lineSeed = line1Seed

				# Wortgrundform suchen
				baseform = Baseform(lineSeed, auth=WORTSCHATZ_CREDENTIALS)
				if len(baseform) > 0:
					lineSeed = baseform[0][0]

				# Thesaurus
				words = Similarity(lineSeed, g, auth=WORTSCHATZ_CREDENTIALS) # hole g Worte via Thesaurus
#				print len(words), [w[1] for w in words] #DEBUG

				# Seedwort aus Rueckgabeliste auswaehlen
				while len(words) > 0:
					j = g % len(words) - 1
#					print "Zeile", i, ", Seedwort: len(words) ist", len(words), ", g ist", g, " und der Rest - 1 ist", j #DEBUG
					seedword = words.pop(j)[1] # words[j] ist Liste mit dem Synonymwort an Pos. 0 (Similarity: Pos. 1)
					if self.countSyllables(seedword) > 0:
						line1Seed = seedword
						break
#			print "Das Seedwort lautet", seedword #DEBUG

			# Zahl der freien Silben rechts und links errechnen
			# @TODO: Was tun, wenn Seedwort zu lang fuer die Zeile?
			line, s, syllableNo = seedword, self.countSyllables(seedword), 5
			if i == 1:
				syllableNo = 7
			if s + seedwordPos[i] > syllableNo:#
				freeSyllablesRight = 0
				seedwordPos[i] = syllableNo - s
			else:
				freeSyllablesRight = syllableNo - s - seedwordPos[i]
			freeSyllablesLeft = seedwordPos[i]
#			print syllableNo, seedwordPos[i], freeSyllablesRight, freeSyllablesLeft #DEBUG

			# Zeile nach links vervollstaendigen
			while freeSyllablesLeft > 0:
				word = "und" # @TODO: zufaelliges Ein-Silben-Fuellwort aussuchen
				g = self.__char2int(geneLines[i][freeSyllablesLeft-1])
				words = LeftNeighbours(line.split()[0], g, auth=WORTSCHATZ_CREDENTIALS)
				while len(words) > 0:
					j = g % len(words) - 1
#					print "Zeile", i, ", links: len(words) ist", len(words), ", g ist", g, " und der Rest - 1 ist", j #DEBUG
					tmpWord = words.pop(j)[0] # words[j] ist Liste mit dem Nachbarwort an Pos. 0
#					print "tmpWort links lautet", tmpWord, "und hat", self.countSyllables(tmpWord), "Silben" #DEBUG
					lTmp = self.countSyllables(tmpWord)
					if lTmp > freeSyllablesLeft or lTmp == 0:
						continue
					else:
						word = tmpWord
						break
#				print "lWort lautet", word, "und hat", countSyllables(word), "Silben" #DEBUG
				freeSyllablesLeft -= self.countSyllables(word)
				line = word + " " + line
#				print line, freeSyllablesLeft #DEBUG

			# Zeile nach rechts vervollstaendigen
			while freeSyllablesRight > 0:
				word = "und" # @TODO: zufaelliges Ein-Silben-Fuellwort aussuchen
				g = self.__char2int(geneLines[i][syllableNo-freeSyllablesRight])
				words = RightNeighbours(line.split()[-1], g, auth=WORTSCHATZ_CREDENTIALS)
				while len(words) > 0:
					j = g % len(words) - 1
#					print "Zeile", i, ", rechts: len(words) ist", len(words), ", g ist", g, " und der Rest - 1 ist", j #DEBUG
					tmpWord = words.pop(j)[1] # words[j] ist eine Liste mit dem Nachbarwort an Pos. 1
					#print "tmpWort rechts lautet", tmpWord, "und hat", countSyllables(tmpWord), "Silben" #DEBUG
					lTmp = self.countSyllables(tmpWord)
					if lTmp > freeSyllablesRight or lTmp == 0:
						continue
					else:
						word = tmpWord
						break
#				print "rWort lautet", word, "und hat", countSyllables(word), "Silben" #DEBUG
				line = line + " " + word
				freeSyllablesRight -= self.countSyllables(word)
#				print line, freeSyllablesRight #DEBUG

			phenotype.append(line)

		self.__phenotype = "\n".join(phenotype)
		return self.__phenotype


	def __develop3(self):
		"""@TODO: Beschreibung fehlt
		"""
		pass


	def procreate1(self):
		u"""Gibt eine Instanz von AutoPoemSpecimen zurueck, deren
			Genotyp eine Mutation des eigenen Genotyps ist.

			Zurzeit wird ein Gen zufaellig ausgewaehlt und um eins oder
			zwei entweder erhoeht oder erniedrigt.
		"""

		parent = self.getGenotype()
		newSeedword = parent[0] # @TODO: Mutation des Seedworts ermoeglichen

		# Zufaelliges Gen mutieren
		genes = parent[1].replace(" ", "")
		i, j = random.randint(0, 16), random.choice([-2, -1, 1, 2])
		mutatedGene = chr(ord(genes[i]) + j)

		# Sonderfaelle abfangen
		if mutatedGene == chr(96):
			mutatedGene = "z"
		elif mutatedGene == chr(123):
			mutatedGene = "a"

		mutatedGenes = genes[:i] + mutatedGene + genes[i+1:]
		# @TODO Sollte ich den Phaenotyp mit dem des Elter abgleichen, um identische Phaenotypen zu vermeiden? Andererseits wuerde ich damit Mutationsspruenge von mehr als einem Gen und +/-1 unmoeglich machen
		return AutoPoemSpecimen(newSeedword, mutatedGenes[:5] + " " + mutatedGenes[5:12] + " " + mutatedGenes[12:], self)


	def procreateN(self, litterSize=2):
		u"""Erzeugt n voneinander verschiedene Kinder, die alle vom
			Genotyp der Instanz abstammen.

			Anders als Procreate1() gibt diese Funktion die neuen Kinder
			nicht nur zurueck (als Liste von AutoPoemSpecimen), sondern
			speichert den Wurf zusaetzlich in der Instanz (wobei alle
			existierenden Kinder ueberschrieben werden).
		"""

		# Erstes Kind
		self.__children = [self.procreate1(), ] # vorhandene Kinder werden ueberschrieben
		if litterSize == 1:
			return self.__children

		# Kinder 2 bis n
		for i in range(litterSize - 1):

			# So lange weitere Kinder erzeugen, bis keine zwei gleich sind
			while True:
				newChild = self.procreate1()
				isDistinct = True

				# pruefen, ob das neue Kind mit einem der schon erzeugten Kinder identisch ist
				# @TODO Phaenotypen miteinander vergleichen statt wie im Moment nur die Genotypen
				for j in range(len(self.__children)):
					if newChild.getGenotype()[1] == self.__children[j].getGenotype()[1]:
						# @TODO: Was tun, wenn die Varianz der Develop-Fkt. keine Varianz erzeugt, d.h. alle Kinder sind gleich und die while-Schleife nie endet?
						isDistinct = False
						print "Leider keine unterschiedlichen Kinder. Der Genotyp ist", newChild.getGenotype() #DEBUG
						break
						# @TODO Bei bestimmten Seedworten ist die Haiku-Varianz so gering,
						# dass alle Kinder gleich sind und die while-Schleife nie endet. Hmpf.
				if isDistinct:
					break
			self.__children.append(newChild)

		return self.__children


	# Funktion ist obsolet (Web-Frontend) und kaputt; sie beruht noch darauf, dass die
	# Kinder keine Klasseninstanzen, sondern reine Genotypen sind
def chooseNewGeneration(autoPoem, children):
	u"""Laesst den Benutzer eines der Kinder in der uebergebenen Liste
		auswaehlen.

		Zurzeit erfolgt die Auswahl ueber die Kommandozeile und die
		Eingabe via raw_input().
	"""

	# Phaenotypen erzeugen und anzeigen
	for i in range(len(children)):
		children[i].append(autoPoem.develop(children[i]))
		print "Kind " + str(i+1) + ":\n\n"
		print children[i][2] + "\n"

	# Nutzereingabe einholen und auswerten
	while True:
		choice = raw_input(u"Welches Kind (1 bis " + str(len(children)) + u") soll ueberleben?\n")
		try:
			c = int(choice)
		except:
			print "Bitte Eingabe wiederholen."
			continue
		if not 0 < c < len(children)+1:
			print u"Bitte waehlen Sie ein Kind aus der Liste aus."
			continue
		break

	return children[c-1]


def main():
	myPoem = AutoPoemSpecimen()
	print "Genotyp: ", myPoem.getGenotype()
	print u"\nPhaenotyp:\n\n", myPoem.getPhenotype()

#	while True: # dieser Block fkt. so nicht mehr
#		children = myPoem.procreateN([], 2)
#		newGeneration = chooseNewGeneration(myPoem, children)
#		print "Die naechste Generation lautet: \n" + newGeneration[2] + "!\n" # fkt. das so? siehe Kommentar bei enableNextGeneration
#		myPoem.enableNextGeneration(newGeneration)

	return 0

if __name__ == '__main__':
	main()
