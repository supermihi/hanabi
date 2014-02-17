import itertools

from hanabi.spiel import Karte
from hanabi import Farben, Zahlen
import numpy as np

arrayDim = (len(Farben), len(Zahlen))
ones = np.ones(arrayDim, dtype=np.int)

class SpielerInfo:
    """Informationen über einen bestimmten Spieler"""
    startInfo = np.empty(arrayDim, dtype=np.int)
    
    def __init__(self, spieler, betrifft):
        self.spieler = spieler
        self.betrifft = betrifft
        self.karten = []
        self.sichtInfo = np.zeros(arrayDim, dtype=np.int)
        self.passtMaske = np.zeros(arrayDim, dtype=np.int)
        self.passtMaske[:, 0] = 1 # am Anfang passen alle 1er
        self.kritischMaske = np.zeros(arrayDim, dtype=np.int)
        self.kritischMaske[:,-1] = 1 # am Anfang sind alle 5er kritisch
        self.egalMaske = np.zeros(arrayDim, dtype=np.int)
        for i in range(spieler.kartenProSpieler()):
            self.karten.append(KartenInfo(betrifft, i))
        self.info = self.sichtInfo
        self.initialisiere()
            
    def initialisiere(self):
        for karte in self.spieler.sichtbareKarten():
            self.sichtInfo[karte.index] += 1
        for mitspieler in self.spieler.mitspieler(außer=self.betrifft):
            karten = self.spieler.handkartenVon(mitspieler)
            for karte in karten:
                self.sichtInfo[karte.index] += 1
        for karte in self.karten:
            self.berechneKartenInfo(karte)
    
    def berechneKartenInfo(self, karte):
        matrix = SpielerInfo.startInfo - self.sichtInfo
        for hinweis in self.spieler.hinweisInfos:
            matrix = hinweis.anwenden(karte, matrix)
        karte.matrix = matrix

    def neueKarte(self, mitspieler, position, spielzug):
        if not self.spieler.habeKarteInPosition(position, mitspieler):
            self.karten[position].matrix[:,:] = 0
            return
        if mitspieler is self.betrifft:
            self.karten[position].seit = spielzug
            self.berechneKartenInfo(self.karten[position])
        elif mitspieler is not self.spieler:
            # ich kann die neue Karte sehen -> sichtInfo runtersetzen
            karte = self.spieler.handkartenVon(mitspieler)[position]
            self.sichtInfo[karte.index] += 1
            for k in self.karten:
                if k.matrix[karte.index] > 0:
                    k.matrix[karte.index] -= 1
        else:
            # jemand anders sieht neue Karte bei mir, ich weiß aber nicht welche
            # => kann nichts sagen
            pass
    
    def karteAbgeworfen(self, mitspieler, karte):
        if mitspieler is self.betrifft:
            self.sichtInfo[karte.index] += 1
            for kartenInfo in self.karten:
                if kartenInfo.matrix[karte.index] > 0:
                    kartenInfo.matrix[karte.index] -= 1
        else:
            # die Karte habe ich schon vorher gesehen, also keine
            # neue Information
            pass
        abgeworfene = [ k for k in self.spieler.abgeworfeneKarten()
                        if k == karte ]
        if len(abgeworfene) == Karte.häufigkeit(karte.farbe, karte.zahl) - 1:
            self.kritischMaske[karte.farbIndex, karte.zahlIndex] = 1
        
        # TODO REPARIEREN if self. == self.startInfo[karte.index]:
            # alle Karten dieser Sorte sind weg -> stapel egal
        #    self.egalMaske[karte.farbIndex, :] = 1
    
    def karteAbgelegt(self, mitspieler, karte):
        self.karteAbgeworfen(mitspieler, karte) # gleiche Behandlung
        self.passtMaske[karte.farbIndex, karte.zahlIndex] = 0
        if karte.zahl < max(Zahlen):
            self.passtMaske[karte.farbIndex, karte.zahlIndex+1] = 1
        self.egalMaske[karte.farbIndex, karte.zahlIndex] = 1

    def neuerHinweis(self, hinweis):
        for karte in self.karten:
            karte.matrix = hinweis.anwenden(karte, karte.matrix)
    
    def möglichkeiten(self, position):
        """Gibt Anzahl der möglichen Karten auf *position* (inkl. Multiplizität) an."""
        return np.sum(self.karten[position].matrix)
    
    def wsPasst(self, position):
        """Gibt Wahrscheinlichkeit dass Karte auf *position* abgelegt werden kann."""
        passend = np.sum(self.karten[position].matrix*self.passtMaske)
        alle = self.möglichkeiten(position)
        if alle == 0:
            return 0
        return passend / alle
    
    def wsEgal(self, position):
        """Gibt Wahrscheinlichkeit dass Karte auf *position* nicht mehr gebraucht wird."""
        egal = np.sum(self.karten[position].matrix*self.egalMaske)
        alle = self.möglichkeiten(position)
        if alle == 0:
            return 0
        return egal / alle
        
    def wsKritisch(self, position):
        """Gibt Wahrscheinlichkeit dass Karte auf *position* die letzte ihrer Art ist."""
        kritisch = np.sum(self.karten[position].matrix*self.kritischMaske)
        alle = self.möglichkeiten(position)
        if alle == 0:
            return 0
        return kritisch / alle       
    
    def erwZahl(self, position):
        """Erwartungswert der Zahl, die sich auf *position* befindet."""
        return np.dot(np.arange(1,6), self.karten[position].matrix.sum(0))/self.karten[position].matrix.sum()
    
    def infoMatrix(self, position):
        return self.karten[position].matrix
    
    def htmlInfo(self, position):
        string = "<table><tr><td></td>{}</tr>".format("".join("<th>{}</th>".format(zahl) for zahl in Zahlen))
        for i, farbe in enumerate(Farben):
            string += "<tr><th>{}</th>{}</tr>".format(farbe, "".join("<td>{}</td>".format(self.karten[position].matrix[i,j]) for j, zahl in enumerate(Zahlen)))
        string += "</table>"
        string += "wsPasst:{}<br />wsEgal: {}".format(self.wsPasst(position), self.wsEgal(position))
        return string

class KartenInfo:
    """Informationen über eine Karte eines bestimmten Spielers"""
    
    def __init__(self, spieler, position, seit=1):
        """Spieler: betreffender Spieler
           position: position der Karte
           seit: spielzug in dem sie aufgenommen wurde
        """
        self.spieler = spieler
        self.position = position
        self.seit = seit

for i, farbe in enumerate(Farben):
    for j, zahl in enumerate(Zahlen):
        SpielerInfo.startInfo[i,j] = Karte.häufigkeit(farbe, zahl)


class HinweisInfo:
    
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
    
    def __init__(self, spiel, spielerNummer):
        self.spiel = spiel
        self.nummer = spielerNummer           
            
    # ===== Informations-Abfragen die eine KI benutzen darf ====
    
    def mitspieler(self, außer=None):
        """Gibt die Mitspieler als Liste aus, beginnend mit dem Nachfolger. Falls *außer*
        angegeben, diesen ausschließen."""
        return [self.spiel.spieler[i % self.spiel.spielerAnzahl]
                for i in range(self.nummer, self.nummer + self.spiel.spielerAnzahl - 1)
                if self.spiel.spieler[i % self.spiel.spielerAnzahl] is not außer]
    
    def handkartenVon(self, mitspieler):
        """Handkarten von *mitspieler* ausgeben."""
        if mitspieler is self:
            raise RuntimeError("Die eigenen Karten darf man nicht sehen!")
        return self.spiel.handKarten[mitspieler]
    
    def ältesteKarte(self, spieler=None, positionen=None):
        """Index der Karte die *spieler* (Standard: self) am längsten hat.
        Falls *positionen* gegeben ist,
        nur auf diesen Positionen suchen. Bei Gleichstand wird der kleinste Index 
        zurückgegeben.
        """
        if spieler is None:
            spieler = self
        spielerInfos = self.infos[spieler]
        if positionen is None:
            positionen = list(range(len(spielerInfos)))
        infos = [ spielerInfos[i] for i in positionen ]
        maxAlter = min(info.seitSpielzug for info in infos)
        for pos in positionen:
            if spielerInfos[pos].seitSpielzug == maxAlter:
                return pos
    
    def aktuellerSpielzug(self):
        return self.spiel.aktuellerSpielzug
    
    def verfügbareHinweise(self):
        return self.spiel.verfügbareHinweise
    
    def verfügbareBlitze(self):
        return 2 - self.spiel.blitze
    
    def abgelegteKarten(self, farbe):
        return len(self.spiel.ablage[farbe])
    
    def abgeworfeneKarten(self):
        for karte in self.spiel.abwurfStapel:
            yield karte
    
    def sichtbareKarten(self):
        """Iteriert durch alle öffentlich sichtbare (abgelegte und abgeworfene) Karten."""
        for farbe in Farben:
            for karte in self.spiel.ablage[farbe]:
                yield karte
        yield from self.abgeworfeneKarten()

    def passtAufAblage(self, karte):
        return self.spiel.passtAufAblage(karte)
        
    def habeKarteInPosition(self, position, spieler=None):
        """Gibt an ob der Spieler an *position* eine Karte hat. In der letzten
        Runde kann dies False zurückgeben."""
        if spieler is None:
            spieler = self
        return self.spiel.handKarten[spieler][position] is not None
    
    def spielerAnzahl(self):
        return self.spiel.spielerAnzahl
    
    def kartenProSpieler(self):
        return self.spiel.kartenProSpieler
    
    # === Verwaltung der Infos ===
    def neuesSpiel(self):
        spiel = self.spiel
        self.hinweisInfos = []
        self.infos = {}
        for spieler in [self] + self.mitspieler():
            self.infos[spieler] = SpielerInfo(self, spieler)

    # ====== Funktionen die Nachrichten vom Spiel verarbeiten =====
    
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
