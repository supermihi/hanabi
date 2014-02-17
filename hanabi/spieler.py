import itertools

import numpy as np

from hanabi import Karte, Farben, Zahlen


arrayDim = (len(Farben), len(Zahlen))
ones = np.ones(arrayDim, dtype=np.int)

class SpielerInfo:
    """Informationen, die die KI  über einen bestimmten Spieler hat.
    
    Die Informationen werden durch 5x5-Matrizen (indiziert durch (Farbe, Zahl)) verwaltet. Der
    Eintrag M[f,z] gibt an, wie viele Karten mit Farbe f und Zahl z potentiell auf der gegebenen
    Position sein könnten.
    Die "Grundinformation" (startInfo) enthält jeweils die Häufigkeit mit der die Karte im Spiel
    ist. Für jede sichtbare Karte (Mitspieler, Abwurf- und Ablagestapel) kann der entsprechende
    Eintrag der Matrix um 1 verringert werden. Dazu wird die Matrix sichtInfo bei jeder Abwurf-
    oder Ablage-Aktion aktualisiert und dann von der startInfo subtrahiert.
    
    Hinweise lassen sich als binäre 5x5-Matrizen modellieren, die als Maske wirken: alle Einträge
    sind zunächst 1, bei jeder Karte die durch den Hinweis ausgeschlossen werden kann steht statt-
    dessen eine 0. Wird nun die Maske mit der Info-Matrix (elementweise) multipliziert, stehen nur
    noch die übrigen Möglichkeiten darin.
    
    Ebenfalls durch Masken modelliert wird die Information, ob eine Karte passt (passtMaske: enthält
    Einsen genau bei den Karten die derzeit auf den Ablagestapel passen), ob sie "egal" ist, also
    sicher abgeworfen werden kann (egalMaske), und ob sie kritisch ist, also noch gebraucht wird und
    als einzige im Spiel ist (kritischMaske).
    """
    
    startInfo = np.empty(arrayDim, dtype=np.int)
    
    def __init__(self, spieler, betrifft):
        """Erstellt SpielerInfo von *spieler* aus Sicht von *betrifft* (kann gleich sein.
        """
        self.spieler = spieler
        self.betrifft = betrifft
        self.kartenInfos = []
        self.sichtInfo = np.zeros(arrayDim, dtype=np.int)
        self.passtMaske = np.zeros(arrayDim, dtype=np.int)
        self.passtMaske[:, 0] = 1 # am Anfang passen alle 1er
        self.kritischMaske = np.zeros(arrayDim, dtype=np.int)
        self.kritischMaske[:,-1] = 1 # am Anfang sind alle 5er kritisch
        self.egalMaske = np.zeros(arrayDim, dtype=np.int)
        for i in range(spieler.kartenProSpieler()):
            self.kartenInfos.append(KartenInfo(betrifft, i))
        self.info = self.sichtInfo
        self.initialisiere()
            
    def initialisiere(self):
        """Initialisiert die Informationen nach Austeilen der Karten."""
        for karte in self.spieler.sichtbareKarten():
            self.sichtInfo[karte.index] += 1
        for mitspieler in self.spieler.mitspieler(außer=self.betrifft):
            karten = self.spieler.handkartenVon(mitspieler)
            for karte in karten:
                self.sichtInfo[karte.index] += 1
        for kartenInfo in self.kartenInfos:
            self.berechneKartenInfo(kartenInfo)
    
    def berechneKartenInfo(self, kartenInfo):
        """Berechnet die Matrix für gegebenes KartenInfo-Objekt."""
        matrix = SpielerInfo.startInfo - self.sichtInfo
        for hinweis in self.spieler.hinweisInfos:
            matrix = hinweis.anwenden(kartenInfo, matrix)
        kartenInfo.matrix = matrix

    def neueSichtInfo(self, karte):
        """Hilfsfunktion, die die Daten aktualisiert wenn neue Karte sichtbar ist."""
        # self.betrifft kannte die Karte vorher nicht => jetzt sichtInfo rauf
        self.sichtInfo[karte.index] += 1
        for kartenInfo in self.kartenInfos:
            if kartenInfo.matrix[karte.index] > 0:
                kartenInfo.matrix[karte.index] -= 1
    
    def neueKarte(self, mitspieler, position, spielzug):
        """Reagiere darauf dass *mitspieler* auf *position* eine neue Karte gezogen hat."""
        if not self.spieler.habeKarteInPosition(position, mitspieler):
            # neue Karte ist None (letzte Runde)
            self.kartenInfos[position].matrix[:,:] = 0
            return
        if mitspieler is self.betrifft:
            # der betreffende mitspieler hat gezogen -> kenn die Karte selbst nicht.
            # Wir aktualisieren das Alter und berechnen Info neu (potentiell sind Hinweise
            # nicht mehr aktuell).
            self.kartenInfos[position].seit = spielzug
            self.berechneKartenInfo(self.kartenInfos[position])
        elif mitspieler is not self.spieler:
            # mitspieler ist weder self.spieler noch self.betrifft.
            # => self.betrifft kann die neue Karte sehen => sichtInfo runtersetzen
            karte = self.spieler.handkartenVon(mitspieler)[position]
            self.sichtInfo[karte.index] += 1
            for k in self.kartenInfos:
                if k.matrix[karte.index] > 0:
                    k.matrix[karte.index] -= 1
        else: # mitspieler is self.spieler and mitspieler is not self.betrifft
            # jemand anders sieht neue Karte bei mir, ich weiß aber nicht welche
            # => kann nichts sagen
            pass
    
    def karteAbgeworfen(self, mitspieler, karte):
        """Reagiere darauf dass *mitspieler* eine *karte* abgeworfen hat."""
        if mitspieler is self.betrifft:
            self.neueSichtInfo(karte)
        
        # kritischMaske ggf. aktualisieren
        abgeworfene = [ k for k in self.spieler.abgeworfeneKarten()
                        if k == karte ]
        if len(abgeworfene) == Karte.häufigkeit(karte.zahl) - 1:
            self.kritischMaske[karte.farbIndex, karte.zahlIndex] = 1
        
        # TODO REPARIEREN if self. == self.startInfo[karte.index]:
            # alle Karten dieser Sorte sind weg -> stapel egal
        #    self.egalMaske[karte.farbIndex, :] = 1
    
    def karteAbgelegt(self, mitspieler, karte):
        """Reagiere darauf dass *mitspieler* eine *karte* abgelegt hat."""
        if mitspieler is self.betrifft:
            self.neueSichtInfo(karte)
        self.passtMaske[karte.farbIndex, karte.zahlIndex] = 0 # passt jetzt nicht mehr
        if karte.zahl < max(Zahlen):
            # dafür die nächste
            self.passtMaske[karte.farbIndex, karte.zahlIndex+1] = 1
        self.egalMaske[karte.farbIndex, karte.zahlIndex] = 1 # kann jetzt abgeworfen werden

    def neuerHinweis(self, hinweis):
        """Reagiere darauf dass ein neuer Hinweis gegeben wurde wurde."""
        for kartenInfo in self.kartenInfos:
            kartenInfo.matrix = hinweis.anwenden(kartenInfo, kartenInfo.matrix)
    
    def möglichkeiten(self, position):
        """Gibt Anzahl der möglichen Karten auf *position* (inkl. Multiplizität) an."""
        return np.sum(self.kartenInfos[position].matrix)
    
    def wsPasst(self, position):
        """Gibt Wahrscheinlichkeit dass Karte auf *position* abgelegt werden kann."""
        passend = np.sum(self.kartenInfos[position].matrix*self.passtMaske)
        alle = self.möglichkeiten(position)
        if alle == 0:
            return 0
        if passend > alle:
            print("????")
            print(self.passtMaske)
            print(self.kartenInfos[position].matrix)
            print(self.kartenInfos[position].matrix*self.passtMaske)
        return passend / alle
    
    def wsEgal(self, position):
        """Gibt Wahrscheinlichkeit dass Karte auf *position* nicht mehr gebraucht wird."""
        egal = np.sum(self.kartenInfos[position].matrix*self.egalMaske)
        alle = self.möglichkeiten(position)
        if alle == 0:
            return 0
        return egal / alle
        
    def wsKritisch(self, position):
        """Gibt Wahrscheinlichkeit dass Karte auf *position* die letzte ihrer Art ist."""
        kritisch = np.sum(self.kartenInfos[position].matrix*self.kritischMaske)
        alle = self.möglichkeiten(position)
        if alle == 0:
            return 0
        return kritisch / alle       
    
    def erwZahl(self, position):
        """Erwartungswert der Zahl, die sich auf *position* befindet."""
        return np.dot(np.arange(1,6), self.kartenInfos[position].matrix.sum(0))/self.kartenInfos[position].matrix.sum()
    
    def infoMatrix(self, position):
        """Informations-Matrix für Kartenposition *position* angeben."""
        return self.kartenInfos[position].matrix
    
    def htmlInfo(self, position):
        string = "<table><tr><td></td>{}</tr>".format("".join("<th>{}</th>".format(zahl) for zahl in Zahlen))
        for i, farbe in enumerate(Farben):
            string += "<tr><th>{}</th>{}</tr>".format(farbe, "".join("<td>{}</td>".format(self.kartenInfos[position].matrix[i,j]) for j, zahl in enumerate(Zahlen)))
        string += "</table>"
        string += "wsPasst:{}<br />wsEgal: {}".format(self.wsPasst(position), self.wsEgal(position))
        return string


class KartenInfo:
    """Informationen über eine unbekannte Karte eines bestimmten Spielers"""
    
    def __init__(self, spieler, position, seit=1):
        """Spieler: betreffender Spieler
           position: position der Karte
           seit: spielzug in dem sie aufgenommen wurde
        """
        self.spieler = spieler
        self.position = position
        self.seit = seit

# startInfo initialisieren
for i, farbe in enumerate(Farben):
    for j, zahl in enumerate(Zahlen):
        SpielerInfo.startInfo[i,j] = Karte.häufigkeit(zahl)


class HinweisInfo:
    """Information über einen gegebenen Hinweis."""
    def __init__(self, spieler, spielzug, positionen, art):
        self.spieler = spieler
        self.spielzug = spielzug
        self.positionen = positionen
        self.art = art
        self.positivMatrix = np.zeros(arrayDim, dtype=np.int)
        if art in Farben:
            self.positivMatrix[Farben.index(art),:] = 1
        else:
            self.positivMatrix[:,Zahlen.index(art)] = 1
        self.negativMatrix = ones - self.positivMatrix
        
    def anwenden(self, kartenInfo, matrix):
        if kartenInfo.spieler is not self.spieler:
            return matrix
        if kartenInfo.seit > self.spielzug:
            return matrix
        if kartenInfo.position in self.positionen:
            return matrix*self.positivMatrix
        else:
            return matrix*self.negativMatrix


class HanabiSpieler:
    """Ein Hanabi-Spieler, in der Regel mit KI.
    
    Die Klasse enthält Methoden mit denen regelkonform Information über das derzeitige Spiel
    abgefragt werden können. Außerdem werden die SpielerInfo-Objekte mit der "objektiven"
    Information erstellt und verwaltet, um die Implementierung eigener KI-Spieler zu vereinfachen.
    """
    
    def __init__(self, spiel, spielerNummer):
        self.spiel = spiel
        self.nummer = spielerNummer           
            
    # ===== Informations-Abfragen die eine KI benutzen darf ====
    
    def mitspieler(self, außer=None):
        """Gibt die Mitspieler als Liste aus, beginnend mit dem Nachfolger.
        
        Falls *außer* angegeben ist, wird dieser übersprungen."""
        return [self.spiel.spieler[i % self.spiel.spielerAnzahl]
                for i in range(self.nummer, self.nummer + self.spiel.spielerAnzahl - 1)
                if self.spiel.spieler[i % self.spiel.spielerAnzahl] is not außer]
    
    def handkartenVon(self, mitspieler):
        """Handkarten von *mitspieler* ausgeben. Wirt einen Fehler wenn mitspieler == self ist."""
        if mitspieler is self:
            raise RuntimeError("Die eigenen Karten darf man nicht sehen!")
        return self.spiel.handKarten[mitspieler]
    
    def aktuellerSpielzug(self):
        """Zahl des aktuellen Spielzugs (beginnt bei 1)."""
        return self.spiel.aktuellerSpielzug
    
    def verfügbareHinweise(self):
        """Anzahl noch verfügbarer Hinweisplättchen."""
        return self.spiel.verfügbareHinweise
    
    def verfügbareBlitze(self):
        """Anzahl der Fehler die noch gemacht werden dürfen bevor das Spiel verloren ist."""
        return 2 - self.spiel.blitze
    
    def abgelegteKarten(self, farbe):
        """Anzahl Karten die auf den Ablagestapel mit der Farbe *farbe* abelegt wurden."""
        return len(self.spiel.ablage[farbe])
    
    def abgeworfeneKarten(self):
        """Iterator über alle abgeworfenen Karten."""
        for karte in self.spiel.abwurfStapel:
            yield karte
    
    def sichtbareKarten(self):
        """Iteriert durch alle öffentlich sichtbare (abgelegte und abgeworfene) Karten."""
        for farbe in Farben:
            for karte in self.spiel.ablage[farbe]:
                yield karte
        yield from self.abgeworfeneKarten()

    def passtAufAblage(self, karte):
        """Gibt an ob *karte* derzeit auf den Ablagestapel passen würde."""
        return self.spiel.passtAufAblage(karte)
        
    def habeKarteInPosition(self, position, spieler=None):
        """Gibt an ob der Spieler an *position* eine Karte hat. In der letzten
        Runde kann dies False zurückgeben."""
        if spieler is None:
            spieler = self
        return self.spiel.handKarten[spieler][position] is not None
    
    def spielerAnzahl(self):
        """Anzahl der Spieler im Spiel."""
        return self.spiel.spielerAnzahl
    
    def kartenProSpieler(self):
        """Anzahl Karten pro Spieler."""
        return self.spiel.kartenProSpieler
    
    
    
    # ====== Verwaltung der SpielerInfos =======
    
    def neuesSpiel(self):
        spiel = self.spiel
        self.hinweisInfos = []
        self.infos = {}
        for spieler in [self] + self.mitspieler():
            self.infos[spieler] = SpielerInfo(self, spieler)

    
    def neueKarte(self, mitspieler, position):
        """Funktion wird vom Spiel aufgerufen, wenn *mitspieler* (kann auch
        man selbst sein) auf *position* eine neue Karte aufgenommen hat.
        """
        for spielerInfo in self.infos.values():
            spielerInfo.neueKarte(mitspieler, position, self.aktuellerSpielzug())
        
    def karteAbgelegt(self, mitspieler, karte):
        for spielerInfo in self.infos.values():
            spielerInfo.karteAbgelegt(mitspieler, karte)
            
    def karteAbgeworfen(self, mitspieler, karte):
        for spielerInfo in self.infos.values():
            spielerInfo.karteAbgeworfen(mitspieler, karte)
    
    def hinweis(self, mitspieler, hinweis, positionen):
        hInfo = HinweisInfo(mitspieler, self.aktuellerSpielzug(), positionen, hinweis)
        self.hinweisInfos.append(hInfo)
        self.infos[mitspieler].neuerHinweis(hInfo)
    
    def __str__(self):
        return "Spieler {}".format(self.nummer)
