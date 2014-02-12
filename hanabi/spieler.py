import itertools

from hanabi.spiel import Karte
from hanabi import Farben, Zahlen

class KartenInformation(dict):
    
    def __init__(self, spieler, andere, position, seitSpielzug=1):
        super().__init__()
        self.spieler = spieler
        self.spiel = spieler.spiel
        self.andere = andere
        self.position = position
        self.seitSpielzug = seitSpielzug
        self.aufbauen()
    
    def aufbauen(self):
        for (farbe,zahl) in itertools.product(Farben, Zahlen):
            self[farbe, zahl] = Karte.häufigkeit(farbe,zahl)
        for karte in self.spiel.fürAlleSichtbareKarten():
            # ablage und abgeworfene
            self[karte.farbe, karte.zahl] -= 1
        for anderer in self.andere:
            for karte in self.spieler.handkartenVon(anderer):
                if karte is not None:
                    self[karte.farbe, karte.zahl] -= 1
        for hinweis in self.relevanteHinweise():
            for (farbe, zahl) in self:
                if self.position in hinweis.positionen:
                    if farbe != hinweis.art and zahl != hinweis.art:
                        self[farbe, zahl] = 0
                else:
                    if farbe == hinweis.art or zahl == hinweis.art:
                        self[farbe, zahl] = 0
    
    def relevanteHinweise(self):
        for hinweis in self.spieler.hinweise:
            if hinweis.spielzug >= self.seitSpielzug and hinweis.spieler == self.spieler:
                yield hinweis
    
    def möglicheKarten(self):
        """Gibt eine Liste an Karten zurück, die aktuell möglich sind."""
        return [Karte(farbe, zahl) for (farbe,zahl), nummer in self.items() if nummer > 0]
    
    def toHTML(self):
        string = "<table><tr><td></td>{}</tr>".format("".join("<th>{}</th>".format(farbe) for farbe in Farben))
        for zahl in Zahlen:
            string += "<tr><th>{}</th>{}</tr>".format(zahl, "".join("<td>{}</td>".format(self[farbe,zahl]) for farbe in Farben))
        string += "</table>"
        return string


class HinweisInformation:
    
    def __init__(self, spieler, spielzug, positionen, art):
        self.spielzug = spielzug
        self.positionen = positionen
        self.art = art
        self.spieler = spieler


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
    
    def passtAufAblage(self, karte):
        return self.spiel.passtAufAblage(karte)
    
    
    # === Verwaltung der Infos ===
    def neuesSpiel(self):
        spiel = self.spiel
        self.hinweise = []
        self.infos = {}
        self.infos[self] = [ KartenInformation(self, self.mitspieler(), i) 
                             for i in range(spiel.kartenProSpieler) ]
        for spieler in self.mitspieler():
            andere = self.mitspieler(außer=spieler)
            self.infos[spieler] = [ KartenInformation(self, andere, i) for i in range(spiel.kartenProSpieler) ]
    
    def infosAufbauen(self):
        for spielerInfos in self.infos.values():
            for info in spielerInfos:
                info.aufbauen()

    # ====== Funktionen die Nachrichten vom Spiel verarbeiten =====
    
    def neueKarte(self, mitspieler, position):
        self.infos[mitspieler][position].seitSpielzug = self.spiel.aktuellerSpielzug
        self.infosAufbauen()
        
    def karteAbgelegt(self, karte):
        self.infosAufbauen()
            
    def karteAbgeworfen(self, karte):
        self.infosAufbauen()
                
    def hinweis(self, mitspieler, hinweis, positionen):
        hinweisInfo = HinweisInformation(mitspieler, self.spiel.aktuellerSpielzug, positionen, hinweis)
        self.hinweise.append(hinweisInfo)
        self.infosAufbauen()
    
    def __str__(self):
        return "Spieler {}".format(self.nummer)
