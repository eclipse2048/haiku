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

from __future__ import division, absolute_import
import string
import random
import os
import re
import libleipzig
from httplib import HTTPConnection

# Umgebungsvariablen mit Credentials fuer die Wortschatz-API einlesen
WORTSCHATZ_CREDENTIALS = ("anonymous", "anonymous")
#if os.environ.has_key("WORTSCHATZ_USER") and os.environ.has_key("WORTSCHATZ_PASSWORD"):
#	WORTSCHATZ_CREDENTIALS = (os.environ["WORTSCHATZ_USER"], os.environ["WORTSCHATZ_PASSWORD"])

# Konstanten fuer die Silbenzaehlung
VOWELS_DE = u"aeiouyäöü"
u"""Vokale der deutschen Sprache, einschliesslich "y" und Umlaute.
"""

ONE_SYLLABLE_COMBINATIONS = (
	u"aa", u"ai", u"ao", u"au", u"ay",
	u"ee", u"ei", u"eu", u"ey",
	u"ie", u"ii",
	u"oo", u"ou", u"oy",
	u"ui", u"uo", u"uu",
	u"\xe4u"
) # nicht enthalten: u"ae", u"oe", u"ue"
u"""Alle Kombinationen von zwei Vokalen, die in der deutschen Sprache
	als einsilbiger Laut behandelt werden.
"""

SYLLABLE_COUNT_EXCEPTIONS = {u"Pietät": 3, u"McDonald's": 3, u"T-Shirt": 2}
u"""Dictionary mit Woertern, die anders getrennt werden als nach den
	ueblichen Regeln. Bsp: Pi|e|taet statt Pie|taet. Das Wort ist der
	key, die tatsaechliche Silbenzahl der value des Dictionary.
"""

# Regulaere Ausdruecke fuer __init__() und countSyllables()
GENES_REGEXP = re.compile(r"[a-z]{5} [a-z]{7} [a-z]{5}$")
SYL_DIGITS_REGEXP = re.compile(r"\d+")
SYL_QU_REGEXP = re.compile(ur"qu[aeiouäöüy]")
SYL_Y_REGEXP = re.compile(ur"y[aeiouäöü]")

DEFAULT_SEEDWORD = u"werden"
u"""Default-Seedwort, falls kein zufaelliges Wort ermittelt werden kann.
"""

WORD_TYPES = ["A", "N", "S", "V"]
u"""Liste der Wortarten fuer den Left/RightCollocationFinder(). A =
	Adjektiv, N = Nomen, S = Stoppwort, V = Verb.
"""

# Stoppwoerter einlesen
# Alt: from nltk.corpus import stopwords; STOPWORDS_DE = [sw.decode("utf-8") for sw in stopwords.words("german")]
corpusFile = "nltk-corpus-stopwords-german.txt"
if os.environ.has_key("OPENSHIFT_REPO_DIR"):
	filename = os.environ["OPENSHIFT_REPO_DIR"] + "wsgi/static/" + corpusFile
else:
	filename = os.path.dirname(os.path.realpath(__file__)) + "/static/" + corpusFile
print "Reading stopwords from file", filename #DEBUG
f = open(filename, "r")
STOPWORDS_DE = [sw.strip().decode("utf-8") for sw in f.readlines()]
f.close()


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

	def __init__(self, seedword=None, genes=None, parent=None):
		u"""@TODO: Beschreibung fehlt
		"""
		self.__seedword = seedword or self.getRandomSeedword()
		if genes:
			# Ggf. Leerzeichen einfuegen
			if len(genes) == 17 and " " not in genes:
				genes = genes[:5] + " " + genes[5:12] + " " + genes[12:]
			#  Gene richtig aufgebaut?
			if not GENES_REGEXP.match(genes):
				print "Fehler: AutoPoemSpecimen.__init__() mit falsch aufgebauten Genen aufgerufen. Verwende zufaellige Gene."
				self.__genes = self.getRandomGenes()
			else:
				self.__genes = genes
		else:
			self.__genes = self.getRandomGenes()

		self.__parent = parent
		self.__children = []
		self.__phenotype = "" # @TODO Besser waere es, den Phaenotyp gleich hier aus dem Genotyp zu erzeugen. Dazu muss die Develop-Funktion aber schnell und zuverlaessig arbeiten; mehrere Sekunden Wartezeit fuer eine simple Instanziierung sind zu viel.
		self.__randGen = random.Random()


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
		word = page[wordStart:wordEnd].rstrip("-,").rstrip()
		try:
			word = word.decode("utf-8")
		except UnicodeEncodeError, u:
			pass
		return word


	def getGenotype(self):
		u"""@TODO: Beschreibung fehlt
		"""
		return [self.__seedword, self.__genes]


	def getPhenotype(self, function=""):
		u"""@TODO: Beschreibung fehlt. Darin muss erwaehnt werden, dass
			diese Funktion Fehler weitergeben kann, die abgefangen
			werden muessen.

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
			funcName = "LRColloc" # @TODO: Default-Fkt. zur Instanzvariable mit Getter/Setter-Methoden machen

		print "Calling develop function '" + funcName + "()' mit Credentials", WORTSCHATZ_CREDENTIALS #DEBUG
		phenotype = getattr(self, funcPrefix + funcName).__call__() # Hier fange ich absichtlich keine Exceptions ab
		if phenotype:
			self.__phenotype = phenotype
		return self.__phenotype


	def getParent(self):
		u"""@TODO: Beschreibung fehlt
		"""
		return self.__parent


	def getChildren(self):
		u"""@TODO: Beschreibung fehlt
		"""
		return self.__children


	def countSyllables(self, word):
		u"""Rekursive Funktion, die die Zahl der Silben fuer ein
			deutsches Wort zurueckgibt.
		"""
		# Manchmal gibt libleipzig merere Worte als ein einzelnes zurueck
		if " " in word:
			return sum([self.countSyllables(w) for w in word.split()])

		def __sylCount(charList):
			u"""Rekursive Funktion, die die naechste Vokalkette sucht
				und die Anzahl ihrer Silben bestimmt.
			"""
			if charList == []:
				return 0
			c, v = 0, []
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
				return 1 + __sylCount(charList[c:])
			# zwei Vokale: eine oder zwei Silben
			elif len(v) >= 2:
				if "".join(v[:2]) in ONE_SYLLABLE_COMBINATIONS:
					return 1 + __sylCount(charList[c-len(v)+2:])
				else:
					return 1 + __sylCount(charList[c-len(v)+1:])

		# Wort in Unicode umwandeln
		try:
			word = word.decode("utf-8")
		except UnicodeEncodeError, u:
			pass
		# ist Wort in Liste mit Ausnahmen?
		if word in SYLLABLE_COUNT_EXCEPTIONS.keys():
			return SYLLABLE_COUNT_EXCEPTIONS[word]
		# Sonderzeichen eliminieren
		if not word.isalnum():
			word = "".join([w for w in word if w.isalnum() or w in u"'`-"]).rstrip(u"-")
		# Sonderfall: Abkuerzung
		if word.isupper():
			return len(word) + word.count("Y") * 2 # "Ypsilon" hat drei Silben
		word = word.lower()
		# Sonderfall: Ziffern am Wortanfang (zB "1920er")
		m = SYL_DIGITS_REGEXP.match(word)
		if m != None:
			return m.end() + self.countSyllables(word[m.end():])
		# Sonderfall: "y<vokal>" ist eine Silbe -> "y" abschneiden
		if SYL_Y_REGEXP.match(word):
			word = word[1:]
		# Sonderfall: "qu<vokal>" ist eine Silbe -> durch "qu" ersetzen
		word = SYL_QU_REGEXP.sub("qu", word)
		return __sylCount(list(word))


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
		geneLines, phenotype, seedwordPos = self.getGenotype()[1].split(), [], []

		# Position des Seedworts in der jeweiligen Zeile ermitteln. Zurzeit nehme ich die Position des Gens mit dem niedrigsten Wert
		for i in range(3):
			seedwordPos.append(geneLines[i].index(min(geneLines[i])))

		# Wortgrundform von Seedwort suchen
		baseseed = libleipzig.Baseform(self.getGenotype()[0], auth=WORTSCHATZ_CREDENTIALS)
		if len(baseseed) > 0:
			seedword1 = baseseed[0][0]
		else:
			seedword1 = self.getGenotype()[0]

		# nacheinander die drei Zeilen des Haikus erzeugen
		for i in range(3):

			# Seedwort ermitteln
			seedword = seedword1
			if i != 0:
				if i == 1:
					lineSeed, line1Seed = seedword1, ""
				elif i == 2:
					lineSeed = line1Seed
				g = self.__char2int(geneLines[i-1][seedwordPos[i-1]]) # das nicht benutzte Gen aus der vorigen Zeile hilft, das Seedwort dieser Zeile zu erzeugen

				# Wortgrundform suchen
				baseform = libleipzig.Baseform(lineSeed, auth=WORTSCHATZ_CREDENTIALS)
				if len(baseform) > 0:
					lineSeed = baseform[0][0]

				# Thesaurus
				words = libleipzig.Similarity(lineSeed, g, auth=WORTSCHATZ_CREDENTIALS) # hole g Worte via Thesaurus

				# Seedwort aus Rueckgabeliste auswaehlen
				while len(words) > 0:
					j = g % len(words) - 1
					seedword = words.pop(j)[1] # words[j] ist Liste mit dem Synonymwort an Pos. 0 (Similarity: Pos. 1)
					if self.countSyllables(seedword) > 0:
						line1Seed = seedword
						break

			# Zahl der freien Silben rechts und links errechnen
			# @TODO: Was tun, wenn Seedwort zu lang fuer die Zeile?
			line, s, syllableNo = seedword, self.countSyllables(seedword), len(geneLines[i])
			if s + seedwordPos[i] > syllableNo:
				freeSyllablesRight = 0
				seedwordPos[i] = syllableNo - s
			else:
				freeSyllablesRight = syllableNo - s - seedwordPos[i]
			freeSyllablesLeft = seedwordPos[i]

			# Zeile nach links vervollstaendigen
			while freeSyllablesLeft > 0:
				word = "und" # @TODO: zufaelliges Ein-Silben-Fuellwort aussuchen
				g = self.__char2int(geneLines[i][freeSyllablesLeft-1])
				words = libleipzig.LeftNeighbours(line.split()[0], g, auth=WORTSCHATZ_CREDENTIALS)
				while len(words) > 0:
					j = g % len(words) - 1
					tmpWord = words.pop(j)[0] # words[j] ist Liste mit dem Nachbarwort an Pos. 0
					lTmp = self.countSyllables(tmpWord)
					if lTmp > freeSyllablesLeft or lTmp == 0:
						continue
					else:
						word = tmpWord
						break
				freeSyllablesLeft -= self.countSyllables(word)
				line = word + " " + line

			# Zeile nach rechts vervollstaendigen
			while freeSyllablesRight > 0:
				word = "und" # @TODO: zufaelliges Ein-Silben-Fuellwort aussuchen
				g = self.__char2int(geneLines[i][syllableNo-freeSyllablesRight])
				words = libleipzig.RightNeighbours(line.split()[-1], g, auth=WORTSCHATZ_CREDENTIALS)
				while len(words) > 0:
					j = g % len(words) - 1
					tmpWord = words.pop(j)[1] # words[j] ist eine Liste mit dem Nachbarwort an Pos. 1
					lTmp = self.countSyllables(tmpWord)
					if lTmp > freeSyllablesRight or lTmp == 0:
						continue
					else:
						word = tmpWord
						break
				line = line + " " + word
				freeSyllablesRight -= self.countSyllables(word)

			phenotype.append(line)

		self.__phenotype = "\n".join(phenotype)
		return self.__phenotype


	def __developLRColloc(self):
		"""@TODO: Beschreibung fehlt
		"""
		geneLines, phenotype, seedwordPos = self.getGenotype()[1].split(), [], []

		def getStopword(randSeed="", syllables=1):
			u"""Gibt ein reproduzierbar zufaelliges Stopwort mit einer
				vorgegebenen maximalen Silbenlaenge zurueck.
			"""
			self.__randGen.seed(str(randSeed)+self.getGenotype()[0]) # Random-Seed ist Konkatenation aus uebergebenem Wert und Seedword
			while True:
				stopword = self.__randGen.choice(STOPWORDS_DE)
				stopwordSyllables = self.countSyllables(stopword)
				if stopwordSyllables > 0 and stopwordSyllables <= syllables:
					break
			return stopword

		# Position des Seedworts in der jeweiligen Zeile ermitteln. Derzeit nehme ich die Summe der Gen-Zahlenwerte modulo der Zeilenlaenge
		for i in range(3):
			lineLen = len(geneLines[i])
			s = sum([self.__char2int(geneLines[i][j]) for j in range(lineLen)])
			seedwordPos.append(s % lineLen)

		# Wortgrundform suchen
		baseSeed = libleipzig.Baseform(self.getGenotype()[0], auth=WORTSCHATZ_CREDENTIALS)
		if len(baseSeed) > 0:
			seedword1 = baseSeed[0][0]
		else:
			seedword1 = self.getGenotype()[0]

		# nacheinander die drei Zeilen des Haikus erzeugen
		for i in range(3):

			# Seedwort ermitteln
			seedword = seedword1
			if i != 0:
				if i == 1:
					lineSeed, line1Seed = seedword1, ""
				elif i == 2:
					lineSeed = line1Seed
				g = self.__char2int(geneLines[i-1][seedwordPos[i-1]])

				# Wortgrundform suchen
				baseform = libleipzig.Baseform(lineSeed, auth=WORTSCHATZ_CREDENTIALS)
				if len(baseform) > 0:
					lineSeed = baseform[0][0]

				# Thesaurus
				words = libleipzig.Similarity(lineSeed, g, auth=WORTSCHATZ_CREDENTIALS)

				# Seedwort aus Rueckgabeliste auswaehlen
				while len(words) > 0:
					j = g % len(words) - 1
					seedword = words.pop(j)[1]
					if self.countSyllables(seedword) > 0:
						if i == 1:
							line1Seed = seedword
						break

			# Zahl der freien Silben rechts und links errechnen
			# @TODO: Was tun, wenn Seedwort zu lang fuer die Zeile?
			line, s, syllableNo = seedword, self.countSyllables(seedword), len(geneLines[i])
			if s + seedwordPos[i] > syllableNo:
				freeSyllablesRight = 0
				seedwordPos[i] = syllableNo - s
			else:
				freeSyllablesRight = syllableNo - s - seedwordPos[i]
			freeSyllablesLeft = seedwordPos[i]

			# Zeile nach links vervollstaendigen
			while freeSyllablesLeft > 0:
				g = self.__char2int(geneLines[i][freeSyllablesLeft-1])
				word = getStopword(g) # @NICE2HAVE: wenn word ein Nomen ist, den passenden Artikel als Stopwort vorhalten
				wordType = WORD_TYPES[g % 4]

				# Kollokationen links holen
				words = libleipzig.LeftCollocationFinder(line.split()[0], wordType, g, auth=WORTSCHATZ_CREDENTIALS)
				while len(words) > 0:
					j = g % len(words) - 1
					tmpWord = words.pop(j)[0]
					lTmp = self.countSyllables(tmpWord)
					if lTmp > freeSyllablesLeft or lTmp == 0:
						continue
					else:
						word = tmpWord
						break
				line = word + " " + line
				freeSyllablesLeft -= self.countSyllables(word)

			# Zeile nach rechts vervollstaendigen
			while freeSyllablesRight > 0:
				g = self.__char2int(geneLines[i][syllableNo-freeSyllablesRight])
				word = getStopword(g)
				wordType = WORD_TYPES[g % 4]

				# Kollokationen rechts holen
				words = libleipzig.RightCollocationFinder(line.split()[0], wordType, g, auth=WORTSCHATZ_CREDENTIALS)

				while len(words) > 0:
					j = g % len(words) - 1
					tmpWord = words.pop(j)[1]
					rTmp = self.countSyllables(tmpWord)
					if rTmp > freeSyllablesRight or rTmp == 0:
						continue
					else:
						word = tmpWord
						break
				line = line + " " + word
				freeSyllablesRight -= self.countSyllables(word)

			phenotype.append(line)

		self.__phenotype = "\n".join(phenotype)
		return self.__phenotype


	def procreate1(self):
		u"""Gibt eine Instanz von AutoPoemSpecimen zurueck, deren
			Genotyp eine Mutation des eigenen Genotyps ist.

			Zurzeit wird ein Gen zufaellig ausgewaehlt und um eins oder
			zwei entweder erhoeht oder erniedrigt.
		"""
		# Zufaelliges Gen mutieren
		genes = self.getGenotype()[1].replace(" ", "")
		i, j = random.randint(0, 16), random.choice([-2, -1, 1, 2])
		mutatedGene = chr(ord(genes[i]) + j)
		newSeedword = self.getGenotype()[0] # @TODO: Mutation des Seedworts ermoeglichen
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
	print u"\nPhaenotyp LRColloc:\n\n", myPoem.getPhenotype(function="LRColloc")

#	while True: # dieser Block fkt. so nicht mehr
#		children = myPoem.procreateN([], 2)
#		newGeneration = chooseNewGeneration(myPoem, children)
#		print "Die naechste Generation lautet: \n" + newGeneration[2] + "!\n" # fkt. das so? siehe Kommentar bei enableNextGeneration
#		myPoem.enableNextGeneration(newGeneration)
	return 0

if __name__ == '__main__':
	main()
