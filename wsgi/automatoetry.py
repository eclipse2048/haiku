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

from __future__ import division, absolute_import # Aufwärtskompatibilität
import string
import random
import sys
from libleipzig import Thesaurus, LeftNeighbours, RightNeighbours
# @TODO: Wortschatz-Credentials für die libleipzig-Methoden benutzen, zB Thesaurus("Wort", auth=("username", "password"))


# Konstanten für die Silbenzählung
VOWELS_DE = u"aeiouyäöü"
""" Vokale der deutschen Sprache, einschließlich "y" und Umlaute.
"""

ONE_SYLLABLE_COMBINATIONS = [u"aa", u"ae", u"ai", u"ao", u"au", u"ay", u"ee", u"ei", u"eu", u"ey", u"ie", u"ii", u"oe", u"oo", u"ou", u"oy", u"ue", u"ui", u"uo", u"uu", u"\xe4u"]
""" Alle Kombinationen von zwei Vokalen, die in der deutschen Sprache
	als einsilbiger Laut behandelt werden.
"""

SYLLABLE_COUNT_EXCEPTIONS = {u"Pietät": 3, u"McDonald's": 3}
""" Dictionary mit Wörtern, die anders getrennt werden als nach den üblichen
	Regeln. Bsp: Pi|e|tät statt Pie|tät. Das Wort ist der key, die
	tatsächliche Silbenzahl der value des Dictionary.
"""


class HaikuError(Exception):
	""" @TODO: Beschreibung fehlt
	"""
	pass


class AutoPoemSpecimen:
	"""	@TODO: Einleitende Beschreibung fehlt.

		Der Genotyp ist eine List mit zwei Elementen. Das erste Element ist
		das Seedwort. Das zweite ist ein String mit drei Worten à 5, 7 und 5
		Zeichen, jeweils durch Leerzeichen voneinander getrennt. Die Zeichen
		stammen aus der Menge [a-z] (string.ascii_lowercase). Die ersten fünf
		Zeichen korrespondieren mit Zeile 1 des Phänotyps (des Haiku-Gedichts),
		die letzten fünf mit Zeile 3 und die mittleren sieben mit Zeile 2.
	"""

	def __init__(self, seedword=None, genes=None, parent=None, phenotype=""):
		""" @TODO: Beschreibung einfügen
		"""
		self.__seedword = seedword or self.createRandomSeedword() # @TODO: Seedwort auf String (und Duden?) überprüfen
		# @TODO: Übergebene Gene auf len==17 und ascii_lowercase überprüfen: r"^[a-z]{5} [a-z]{7} [a-z]{5}$"
		self.__genes = genes or self.createRandomGenes()
		self.__parent = parent
		self.__children = []
		self.__phenotype = phenotype # @TODO hier am besten gleich den Phänotyp erzeugen; hängt aber davon ab, wie lange die Fkt. braucht. Nur weil die Develop-Funktionen z.T. so lange brauchen, gibt es überhaupt die Möglichkeit, dem Konstruktor den Phänotpyen zu übergeben.


	def createRandomGenes(self):
		"""	Erzeugt die Gene für ein zufälliges Exemplar. Nützlich für die
			Erzeugung eines Startindividuums in Generation 1.
		"""
		genes = "".join([random.choice(string.ascii_lowercase) for i in range(17)])
		return genes[:5] + " " + genes[5:12] + " " + genes[12:]


	def createRandomSeedword(self):
		"""	Gibt ein zufälliges Startwort zurück.
		"""
		# @TODO zufälliges Seedwort erzeugen statt hartcodiertes verwenden
		return "laufen"


	def getGenotype(self):
		""" @TODO: Beschreibung fehlt
		"""
		return [self.__seedword, self.__genes]


	def getPhenotype(self):
		""" @TODO: Beschreibung fehlt
		"""
		if self.__phenotype == "":
			self.__phenotype = self.__develop()
		return self.__phenotype


	def getParent(self):
		""" @TODO: Beschreibung fehlt
		"""
		return self.__parent


	def getChildren(self):
		""" @TODO: Beschreibung fehlt
		"""
		return self.__children


	def __sylCount(self, charList):
		"""	Rekursive Funktion, die die Zahl der Silben in einem Wort der deutschen
			Sprache ermittelt. Der Algorithmus sucht die nächste
			zusammenhängenden Vokalkette und überprüft, ob diese eine oder
			mehrere Silben konstituiert.

			Das Eingabewort wird nicht als String erwartet, sondern als Liste von
			einzelnen Buchstaben, alle klein und mit umgewandelten Umlauten (z.B.
			'ä' zu 'ae').
		"""
		if charList == []:
			return 0
		c, v = 0, []

		# nächste Kette von Vokalen finden
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
		"""	Gibt die Zahl der Silben für ein deutsches Wort zurück.
		"""

		# Wort ggf. in Unicode umwandeln
		try:
			word = word.decode("utf-8")
		except UnicodeEncodeError, u:
			pass

		# ist Wort in Liste mit Ausnahmen?
		if word in SYLLABLE_COUNT_EXCEPTIONS.keys():
			return SYLLABLE_COUNT_EXCEPTIONS[word]

		# Manchmal gibt libleipzig merere Worte als ein einzelnes zurück
		if " " in word:
			return sum([self.__sylCount(list(w.strip().lower())) for w in word.split()])

		# Wort in Liste von Kleinbuchstaben umwandeln und ab dafür
		return self.__sylCount(list(word.strip().lower()))


	def __char2int(self, c):
		"""	Gibt die Position des übergebenen Buchstabens im Alphabet zurück, bzw. 0,
			falls c kein Buchstabe ist.
		"""
		return string.ascii_lowercase.find(c.lower()) + 1


	def getFunctionNames(self):
		"""@TODO: Beschreibung fehlt
		"""
		classPrefix = "_" + self.__class__.__name__ + "__develop"
		l = len(classPrefix)
		return [f[l:] for f in dir(self) if f.startswith(classPrefix) and len(f) > l]


	def __develop(self, function=""):
		""" Dummy-Funktion. Ruft die __develop-Funktion auf, deren Restname als Parameter
			übergeben wird. __develop() als Dummy ermöglicht es, unterschiedliche Phänotyp-
			Algorithmen zu verwenden, ohne den Code zu verändern (Ausnahme: Default-Fkt.).

			Tritt beim Funktionsaufruf ein Fehler auf, wird ein HaikuError von der
			auslösenden Fehlerinstanz erzeugt und nach oben weitergegeben.
		"""

		functions, funcPrefix = self.getFunctionNames(), "_" + self.__class__.__name__ + "__develop"
		if function in functions:
			funcName = function
		else:
			# @TODO: Default-Fkt. zur Instanzvariable mit Getter/Setter-Methoden machen
			funcName = "LR575Syllables" # default
		print "Calling develop function '" + funcName + "()'" #DEBUG

		# Funktion ausführen und Fehler abfangen
		try:
			return getattr(self, funcPrefix + funcName).__call__()
		except:
#			errorType, errorInstance, traceback = sys.exc_info()
			print sys.exc_info() #DEBUG
			raise #HaikuError from sys.exc_info()[1]


	def __developLoremipsum(self):
		""" Gibt ein hartcodiertes Haiku zurück. Gut fürs Debugging und wenn der
			Wortschatz-Server nicht erreichbar ist.
		"""
		import time # DEBUG
		time.sleep(sleep) # DEBUG

		return "Lorem Ipsum bla\nZeile braucht sieben Silben\nHassenichgesehn"


	# Funktion ist kaputt
	def __developLR575Words(self, genotype=[]):
		"""	Erzeugt aus einem Genotyp den dazugehörigen Phänotyp. Hier findet der
			schwierige Teil des gesamten Programms statt.

			Die Funktion entwickelt den übergebenen Genotypen. Wird kein Genotyp
			übergeben, nimmt sie den Genotyp der eigenen Instanz.

			__developLR575Words() erzeugt ein Haiku, das anstatt aus 5-7-5 Silben
			aus 5-7-5 Wörtern besteht. In jeder Zeile wird das Seedwort ermittelt
			und an die richtige Stelle gesetzt, danach wird die Zeile nach links
			und nach rechts mit Left/RightNeighbours aufgefüllt.
		"""

		if genotype == []:
			genotype = self.getGenotype()

		geneLines, phenotype, seedwordPos = genotype[1].split(), [], []

		# Position des Seedworts in der jeweiligen Zeile ermitteln.
		# Zurzeit nehme ich die Position des Gens mit dem höchsten Wert
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
				words = Thesaurus(genotype[0], g) # das g-te Thesaurusergebnis wird Seedwort
				seedword = words.pop()[0] # Thesaurus stellt das Synonymwort im Ergebnis an Pos. 0
			line.pop(seedwordPos[i])
			line.insert(seedwordPos[i], seedword)

			# Zeile nach links vervollständigen
			if seedwordPos[i] != 0:
				for j in range(seedwordPos[i]-1, -1, -1):
					words = LeftNeighbours(line[j+1], self.__char2int(geneLines[i][j]))

					if len(words) == 0: # prüfen, ob die Neighbours-Liste leer ist
						word = "Ersatz"
					else:
						word = words.pop()[0] # LeftNeighbours stellt das Nachbarwort im Ergebnis an Pos. 0

					line.pop(j)
					line.insert(j, word)

			# Zeile nach rechts vervollständigen
			if seedwordPos[i] != len(geneLines[i])-1:
				for j in range(seedwordPos[i]+1, len(geneLines[i])):
					words = RightNeighbours(line[j-1], self.__char2int(geneLines[i][j]))

					if len(words) == 0: # prüfen, ob die Neighbours-Liste leer ist
						word = "Ersatz"
					else:
						word = words.pop()[1] # RightNeighbours stellt das Nachbarwort im Ergebnis an Pos. 1

					line.pop(j)
					line.insert(j, word)

			phenotype.append(" ".join(line))

		p = "\n".join(phenotype)

		# Falls der Genotyp der Instanz entwickelt wurde: Phänotyp speichern
		if genotype == self.getGenotype():
			self.__phenotype = p
		return p


	def __developLR575Syllables(self):
		"""	__developLR575Syllables() erzeugt ein Haiku aus 5-7-5 Silben. Wie bei
			__developLR575Words() wird in jeder Zeile das Seedwort ermittelt und an die
			entsprechende Stelle gesetzt. Danach wird die Zeile nach links und rechts mit
			Left/RightNeighbours aufgefüllt, bis die gewünschte Silbenanzahl erreicht
			ist. Falls nur noch eine Silbe frei ist und die Neighbours-Liste kein
			einsilbiges Wort enthält, nehme ich "und".

			Die Ergebnisse sind nicht völlig schlecht, aber:
			- Kinder haben zu wenig Varianz, vor allem bei ungewöhnlichen Seedworten mit
			wenigen Synonymen.
			- Oft ist der Phänotyp einer oder beider Kinder identisch mit dem des Elter.
			- Nicht jede Mutation sorgt für eine sichtbare Veränderung, und wenn es zu
			Veränderungen kommt, betreffen sie oft die ganze Zeile.

			Schöner wäre eine direkte Zuordnung Gen->Silbe, weil dann jede Mutation eine
			konkrete Phänotypenveränderung hervorrufen würde.
		"""

		geneLines, phenotype, seedwordPos = self.getGenotype()[1].split(), [], []

		# Position des Seedworts in der jeweiligen Zeile ermitteln.
		# Zurzeit nehme ich die Position des Gens mit dem höchsten Wert
		for i in range(3):
			seedwordPos.append(geneLines[i].index(max(geneLines[i])))

		# nacheinander die drei Zeilen des Haikus erzeugen
		for i in range(3):
			if i == 1:
				syllableNo = 7
			else:
				syllableNo = 5

			# Seedwort finden
			seedword = self.getGenotype()[0] # Zeile 0 und default
			if i != 0:
				g = self.__char2int(geneLines[i-1][seedwordPos[i-1]]) # nimmt das nicht benutzte Gen aus der vorigen Zeile, um das Seedwort dieser Zeile zu erzeugen
				words = Thesaurus(self.getGenotype()[0], g) # hole g Worte via Thesaurus
				while len(words) > 0:
					j = len(words) % g - 1
					print "Zeile", i, ", Seedwort: len(words) ist", len(words), ", g ist", g, " und der Rest - 1 ist", j
					seedword = words.pop(j)[0] # words[j] ist eine Liste mit dem Synonymwort an Pos. 0
					if self.countSyllables(seedword) > 0:
						break
			print "Das Seedwort lautet", seedword #DEBUG


			# Zahl der freien Silben rechts und links errechnen
			# @TODO: Was tun, wenn Seedwort zu lang für die Zeile?
			line, s = seedword, self.countSyllables(seedword)
			if s + seedwordPos[i] > syllableNo:
				freeSyllablesRight = 0
				seedwordPos[i] = syllableNo - s
			else:
				freeSyllablesRight = syllableNo - s - seedwordPos[i]
			freeSyllablesLeft = seedwordPos[i]

			#print syllableNo, seedwordPos[i], freeSyllablesRight, freeSyllablesLeft #DEBUG

			# Zeile nach links vervollständigen
			while freeSyllablesLeft > 0:
				word = "und"
				g = self.__char2int(geneLines[i][freeSyllablesLeft-1])
				words = LeftNeighbours(line.split()[0], g)
				while len(words) > 0:
					j = len(words) % g - 1
					print "Zeile", i, ", links: len(words) ist", len(words), ", g ist", g, " und der Rest - 1 ist", j
					tmpWord = words.pop(j)[0] # words[j] ist eine Liste mit dem Nachbarwort an Pos. 0
					#print "tmpWort links lautet", tmpWord, "und hat", self.countSyllables(tmpWord), "Silben" #DEBUG
					lTmp = self.countSyllables(tmpWord)
					if lTmp > freeSyllablesLeft or lTmp == 0:
						continue
					else:
						word = tmpWord
						break
				#print "lWort lautet", word, "und hat", countSyllables(word), "Silben" #DEBUG
				freeSyllablesLeft -= self.countSyllables(word)
				line = word + " " + line
				print line, freeSyllablesLeft #DEBUG

			# Zeile nach rechts vervollständigen
			while freeSyllablesRight > 0:
				word = "und"
				g = self.__char2int(geneLines[i][syllableNo-freeSyllablesRight])
				words = RightNeighbours(line.split()[-1], g)
				while len(words) > 0:
					j = len(words) % g - 1
					print "Zeile", i, ", rechts: len(words) ist", len(words), ", g ist", g, " und der Rest - 1 ist", j
					tmpWord = words.pop(j)[1] # words[j] ist eine Liste mit dem Nachbarwort an Pos. 1
					#print "tmpWort rechts lautet", tmpWord, "und hat", countSyllables(tmpWord), "Silben" #DEBUG
					lTmp = self.countSyllables(tmpWord)
					if lTmp > freeSyllablesRight or lTmp == 0:
						continue
					else:
						word = tmpWord
						break
				#print "rWort lautet", word, "und hat", countSyllables(word), "Silben" #DEBUG
				line = line + " " + word
				freeSyllablesRight -= self.countSyllables(word)
				print line, freeSyllablesRight #DEBUG

			phenotype.append(line)

		self.__phenotype = "\n".join(phenotype)
		return self.__phenotype


	def __develop3(self):
		"""@TODO: Beschreibung fehlt
		"""
		pass


	def procreate1(self):
		"""	Gibt eine Instanz von AutoPoemSpecimen zurück, deren Genotyp
			eine Mutation des eigenen Genotyps ist.

			Zurzeit wird ein Gen zufällig ausgewählt und entweder um eins
			erhöht oder um eins erniedrigt.
		"""

		parent = self.getGenotype()
		newSeedword = parent[0] # @TODO: Mutation des Seedworts ermöglichen

		# Zufälliges Gen mutieren
		genes = parent[1].replace(" ", "")
		i, j = random.randint(0, 16), random.choice([-1, +1])
		mutatedGene = chr(ord(genes[i]) + j)

		# Sonderfälle abfangen
		if mutatedGene == chr(96):
			mutatedGene = "z"
		elif mutatedGene == chr(123):
			mutatedGene = "a"

		mutatedGenes = genes[:i] + mutatedGene + genes[i+1:]
		# @TODO Sollte ich den Phänotyp mit dem des Elter abgleichen, um identische Phänotypen zu vermeiden? Andererseits würde ich damit Mutationssprünge von mehr als einem Gen und +/-1 unmöglich machen
		return AutoPoemSpecimen(newSeedword, mutatedGenes[:5] + " " + mutatedGenes[5:12] + " " + mutatedGenes[12:], self)


	def procreateN(self, litterSize=2):
		"""	Erzeugt n voneinander verschiedene Kinder, die alle vom Genotyp
			der Instanz abstammen.

			Anders als Procreate1() gibt diese Funktion die neuen Kinder nicht als
			Einträge zurück, sondern erzeugt einen komplett neuen Wurf und speichert
			ihn in der Instanz.
		"""

		# Erstes Kind
		self.__children = [self.procreate1(), ] # vorhandene Kinder werden überschrieben
		if litterSize == 1:
			return self.__children

		# Kinder 2 bis n
		for i in range(litterSize - 1):

			# So lange weitere Kinder erzeugen, bis keine zwei gleich sind
			while True:
				newChild = self.procreate1()
				isDistinct = True

				# prüfen, ob das neue Kind mit einem der schon erzeugten Kinder identisch ist
				# @TODO Phänotypen miteinander vergleichen statt wie im Moment nur die Genotypen
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
	"""	Lässt den Benutzer eines der Kinder in der übergebenen Liste auswählen.

		Zurzeit erfolgt die Auswahl über die Kommandozeile und die Eingabe via
		raw_input().
	"""

	# Phänotypen erzeugen und anzeigen
	for i in range(len(children)):
		children[i].append(autoPoem.develop(children[i]))
		print "Kind " + str(i+1) + ":\n\n"
		print children[i][2] + "\n"

	# Nutzereingabe einholen und auswerten
	while True:
		choice = raw_input("Welches Kind (1 bis " + str(len(children)) + ") soll überleben?\n")
		try:
			c = int(choice)
		except:
			print "Bitte Eingabe wiederholen."
			continue
		if not 0 < c < len(children)+1:
			print "Bitte wählen Sie ein Kind aus der Liste aus."
			continue
		break

	return children[c-1]


def main():
	myPoem = AutoPoemSpecimen()
	print "Genotyp: ", myPoem.getGenotype()
	print "\nPhänotyp:\n\n", myPoem.getPhenotype()

#	while True: # dieser Block fkt. so nicht mehr
#		children = myPoem.procreateN([], 2)
#		newGeneration = chooseNewGeneration(myPoem, children)
#		print "Die naechste Generation lautet: \n" + newGeneration[2] + "!\n" # fkt. das so? siehe Kommentar bei enableNextGeneration
#		myPoem.enableNextGeneration(newGeneration)

	return 0

if __name__ == '__main__':
	main()
