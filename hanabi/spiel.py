import itertools

from hanabi import Farben, Zahlen


class SpielEnde(RuntimeError):
    pass


class Karte:
    
    def __init__(self, farbe, zahl):
        self.farbe = farbe
        self.zahl = zahl
        self.farbIndex = Farben.index(farbe)
        self.zahlIndex = Zahlen.index(zahl)
        self.index = (self.farbIndex, self.zahlIndex)
    
    def ist(self, farbeOderZahl):
        return self.farbe == farbeOderZahl or self.zahl == farbeOderZahl
    
    def __eq__(self, andere):
        if andere is None:
            return False
        return self.farbe == andere.farbe and self.zahl == andere.zahl
    
    @staticmethod
    def komplettesDeck():
        stapel = []
        for farbe, zahl in itertools.product(Farben, Zahlen):
            for i in range(Karte.häufigkeit(farbe, zahl)):
                stapel.append(Karte(farbe, zahl))
        import numpy
        numpy.random.shuffle(stapel)
        return stapel
    
    
    @staticmethod
    def häufigkeit(farbe, zahl):
        if zahl == 1:
            return 3
        elif zahl == 5:
            return 1
        else:
            return 2
    
    
    gesamtzahl = 50

    def __str__(self):
        return "{}e {}".format(self.farbe.title(), self.zahl)

    __repr__ = __str__

class HanabiSpiel:
    
    hinweisPlättchen = 8
    
    def __init__(self, spielerAnzahl, SpielerKlasse):
        self.SpielerKlasse = SpielerKlasse
        self.setSpielerAnzahl(spielerAnzahl)
        self.initSpieler()
        
    def setSpielerAnzahl(self, anzahl):
        self.spielerAnzahl = anzahl
        self.kartenProSpieler = 5 if anzahl <= 3 else 4
    
    def initSpieler(self):
        self.spieler = []
        for spielerNummer in range(1, self.spielerAnzahl+1):
            self.spieler.append(self.SpielerKlasse(self, spielerNummer))
        self.kartenGeben()
    
    def kartenGeben(self):
        print("****** NEUES SPIEL *****")
        self.handKarten = {}
        self.abwurfStapel = []
        self.ablage = {farbe: [] for farbe in Farben }
        self.verfügbareHinweise = HanabiSpiel.hinweisPlättchen
        self.blitze = 0
        self.stapel = Karte.komplettesDeck()
        self.aktuellerSpieler = self.spieler[0]
        self.aktuellerSpielzug = 1
        self.letzterSpielzug = 0
        self.spielEnde = False
        for spieler in self.spieler:
            startKarten = self.stapel[-self.kartenProSpieler:]
            del self.stapel[-self.kartenProSpieler:]
            self.handKarten[spieler] = startKarten
        for spieler in self.spieler:
            spieler.neuesSpiel()
    
    
    def zieheKarte(self, spieler, position):
        """Ersetzt Karte von *spieler* an Position *position* durch eine neue vom
        Stapel und benachrichtigt alle Spieler.
        """
        if len(self.stapel) == 1:
            self.letzterSpielzug = self.aktuellerSpielzug + self.spielerAnzahl
        neueKarte = self.stapel.pop() if len(self.stapel) > 0 else None
        self.handKarten[spieler][position] = neueKarte
        for mitspieler in self.spieler:
            mitspieler.neueKarte(spieler, position) # mitspieler benachrichtigen

    def passtAufAblage(self, karte):
        if karte is None:
            return False
        stapel = self.ablage[karte.farbe]
        if len(stapel) == 0:
            return karte.zahl == 1
        else:
            return stapel[-1].zahl == karte.zahl - 1
    
    def punktzahl(self):
        if self.blitze == 3:
            return 0
        return sum(len(stapel) for stapel in self.ablage.values())
    
    def autoSpiel(self):
        while True:
            self.autoSpielzug()
    
    def autoSpielzug(self):
        self.spielzug(self.aktuellerSpieler.macheSpielzug())
    
    def spielzug(self, zug):
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
