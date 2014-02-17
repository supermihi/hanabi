import itertools

from hanabi import Karte, Farben, Zahlen


class SpielEnde(RuntimeError):
    """Wird in einem Spielzug geworfen wenn er das Spiel beendet."""
    pass


class HanabiSpiel:
    """Verwaltet die Spieldaten und kümmert sich um Einhaltung der Regeln."""
    
    hinweisPlättchen = 8
    
    def __init__(self, spielerAnzahl, SpielerKlasse):
        """Spiel mit gegebener *spielerAnzahl* und KI-Klasse *SpielerKlasse* erstellen."""
        self.SpielerKlasse = SpielerKlasse
        self.setSpielerAnzahl(spielerAnzahl)
        self.initSpieler()
        
    def setSpielerAnzahl(self, anzahl):
        """Spieleranzahl ändern.
        
        Danach muss initSpieler() aufgerufen werden, um neue KI-Spieler zu erstellen.
        """
        self.spielerAnzahl = anzahl
        self.kartenProSpieler = 5 if anzahl <= 3 else 4
    
    def initSpieler(self):
        """Erstellt neue KI-Spielerobjekte."""
        self.spieler = []
        for spielerNummer in range(1, self.spielerAnzahl+1):
            self.spieler.append(self.SpielerKlasse(self, spielerNummer))
        self.kartenGeben()
    
    def kartenGeben(self):
        """Startet ein neues Spiel durch Austeilen der Karten und rücksetzen aller Daten."""
        
        self.abwurfStapel = []
        self.ablage = {farbe: [] for farbe in Farben }
        self.verfügbareHinweise = HanabiSpiel.hinweisPlättchen
        self.blitze = 0
        self.stapel = Karte.komplettesDeck()
        self.aktuellerSpieler = self.spieler[0]
        self.aktuellerSpielzug = 1
        self.letzterSpielzug = 0
        self.spielEnde = False
        self.handKarten = {}
        # Karten austeilen
        for spieler in self.spieler:
            startKarten = self.stapel[-self.kartenProSpieler:]
            del self.stapel[-self.kartenProSpieler:]
            self.handKarten[spieler] = startKarten
        # Spieler-KIs benachrichtigen dass neues Spiel angefangen hat
        for spieler in self.spieler:
            spieler.neuesSpiel()
    
    def zieheKarte(self, spieler, position):
        """Ersetzt Karte von *spieler* an Position *position* durch eine neue vom Stapel.
        
        Wenn es keine Karten mehr gibt (letzte Runde), wird die entsprechende Handkarte durch
        "None" ersetzt. Die Funktion benachrichtigt nach dem Ziehen alle Spieler über deren
        "neueKarte"-Funktion.
        """
        if len(self.stapel) == 1:
            # noch eine Runde
            self.letzterSpielzug = self.aktuellerSpielzug + self.spielerAnzahl
        neueKarte = self.stapel.pop() if len(self.stapel) > 0 else None
        self.handKarten[spieler][position] = neueKarte
        for mitspieler in self.spieler:
            mitspieler.neueKarte(spieler, position) # mitspieler benachrichtigen

    def passtAufAblage(self, karte):
        """Gibt an ob die *karte* derzeit auf die Ablage passt."""
        if karte is None:
            return False
        stapel = self.ablage[karte.farbe]
        if len(stapel) == 0:
            return karte.zahl == 1
        else:
            return stapel[-1].zahl == karte.zahl - 1
    
    def punktzahl(self):
        """Derzeitige Punktzahl: Summe der abgelegten Karten oder 0 bei drei Fehlern."""
        if self.blitze == 3:
            return 0
        return sum(len(stapel) for stapel in self.ablage.values())
    
    def autoSpiel(self):
        """Lässt das Spiel per KI bis zum Ende durchlaufen."""
        while True:
            self.autoSpielzug()
    
    def autoSpielzug(self):
        """Macht einen Spielzug per KI."""
        self.spielzug(self.aktuellerSpieler.macheSpielzug())
    
    def spielzug(self, zug):
        """Spielzug *zug* (Instanz von spielzug.Spielzug) ausführen.
        
        Falls durch diesen Zug das Spiel endet, wird eine SpielEnde-Ausnahme geworfen.
        Ist das Spiel schon zu Ende oder der Zug ungültig, wird spielzug.UngültigerZug
        geworfen.
        Nach dem Zug wird der aktuelle Spielzug hochgezählt und der nächste Spieler ist
        an der Reihe.
        """
        if self.spielEnde:
            from hanabi.spielzug import UngültigerZug
            raise UngültigerZug("Das Spiel ist zu Ende!")
        #print("{} macht Spielzug: {}".format(self.aktuellerSpieler, zug))
        zug.ausführen(self)
        if self.aktuellerSpielzug == self.letzterSpielzug:
            self.spielEnde = True
            raise SpielEnde("Letzter Spielzug gespielt!")
        if self.punktzahl() == 25:
            self.spielEnde = True
            raise SpielEnde("Gewonnen – 25 Punkte!!!")
        if self.blitze == 3:
            self.spielEnde = True
            raise SpielEnde("Verloren – 3 Fehler :-(")
        self.aktuellerSpielzug += 1
        self.aktuellerSpieler = self.spieler[(self.spieler.index(self.aktuellerSpieler) + 1) % self.spielerAnzahl]
