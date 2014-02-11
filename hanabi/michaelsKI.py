import itertools

from hanabi.spiel import Karte
from hanabi import Farben, Zahlen
from hanabi.spieler import HanabiSpieler

class HandKarte:
    
    def __init__(self):
        self.ws = {}
    
    def wsZurücksetzen(self):
        for farbe, zahl in itertools.product(Farben, Zahlen):
            self.ws[farbe,zahl] = Karte.häufigkeit(farbe, zahl) / Karte.gesamtzahl
        
        
class Michael(HanabiSpieler):
    
    def __init__(self, spiel, spielerNummer):
        super().__init__(spiel, spielerNummer)
        self.handKarten = [HandKarte() for i in range(4)]
        
    def neuesSpiel(self):
        for karte in self.handKarten:
            karte.wsZurücksetzen()
