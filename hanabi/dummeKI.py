from hanabi.spieler import HanabiSpieler
from hanabi.spielzug import *

class DummerSpieler(HanabiSpieler):
    
    def macheSpielzug(self):
        if self.spiel.leereKartenposition(self) == 0:
            return Abwerfen(1)
        return Abwerfen(0)
