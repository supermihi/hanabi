import itertools

from hanabi import Farben, Zahlen


class SpielEnde(RuntimeError):
    pass


class Karte:
    
    def __init__(self, farbe, zahl):
        self.farbe = farbe
        self.zahl = zahl
    
    def ist(self, farbeOderZahl):
        return self.farbe == farbeOderZahl or self.zahl == farbeOderZahl
    
    
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


class HanabiSpiel:
    
    hinweisPlättchen = 8
    
    def __init__(self, spielerAnzahl, SpielerKlasse):
        self.spieler = []
        self.spielerAnzahl = spielerAnzahl
        for spielerNummer in range(1, spielerAnzahl+1):
            self.spieler.append(SpielerKlasse(self, spielerNummer))
        self.kartenProSpieler = 5 if self.spielerAnzahl <= 3 else 4
    
    
    def kartenGeben(self):
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
            
    
    
    def fürAlleSichtbareKarten(self):
        """Iteriert durch alle öffentlich sichtbare (abgelegte und abgeworfene) Karten."""
        for farbe in Farben:
            for karte in self.ablage[farbe]:
                yield karte
        for karte in self.abwurfStapel:
            yield karte

    def obersteKarte(self, farbe):
        """Gibt an welches die oberste Karte auf Ablagestapel *farbe* ist (oder None)."""
        try:
            return self.ablage[farbe][-1]
        except IndexError:
            return None
    
    def passtAufAblage(self, karte):
        stapel = self.ablage[karte.farbe]
        if len(stapel) == 0:
            return karte.zahl == 1
        else:
            return stapel[-1].zahl == karte.zahl - 1
    
    def leereKartenposition(self, spieler):
        """Falls *spieler* eine Karte zu wenig hat (in der letzten Runde),
        gib die entsprechende Position aus, sonst -1."""
        for i, karte in enumerate(self.handKarten[spieler]):
            if karte is None:
                return i
        return -1
    
    def punktzahl(self):
        if self.blitze == 3:
            return 0
        return sum(len(stapel) for stapel in self.ablage.values())
    
    def autoSpielzug(self):
        self.spielzug(self.aktuellerSpieler.macheSpielzug())
    
    def spielzug(self, zug):
        if self.spielEnde:
            from hanabi.spielzug import UngültigerZug
            raise UngültigerZug("Das Spiel ist zu Ende!")
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
