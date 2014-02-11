import itertools

from hanabi.spiel import Karte

class HanabiSpieler:
    
    def __init__(self, spiel, spielerNummer):
        self.spiel = spiel
        self.nummer = spielerNummer
        
    def neuesSpiel(self):
        print("Ein neues Spiel wurde begonnen")
            
    def neueKarte(self, mitspieler, position):
        print("Ich ({}) weiß von neuer Karte von {} auf Position {}".format(self, mitspieler, position))
        
    def karteAbgelegt(self, karte):
        print("Ich ({}) weiß dass eine {} abgelegt wurde".format(self, karte))
    
    def karteAbgeworfen(self, karte):
        print("Ich ({}) weiß dass eine {} abgeworfen wurde".format(self, karte))
        
    def hinweis(self, mitspieler, hinweis, positionen):
        print("Spieler {} weiß dass Karten {} {} sind".format(mitspieler, positionen, hinweis))
    
    def __str__(self):
        return "Spieler {}".format(self.nummer)
