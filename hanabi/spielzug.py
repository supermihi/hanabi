from hanabi import Farben, Zahlen
from hanabi.spiel import HanabiSpiel

class UngültigerZug(Exception):
    pass

class Spielzug:

    def ausführen(self, spiel):
        raise NotImplementedError()


class Hinweis(Spielzug):
    
    def __init__(self, spieler, hinweis):
        self.zielSpieler = spieler
        self.hinweis = hinweis
        
    def ausführen(self, spiel):
        if spiel.aktuellerSpieler == self.zielSpieler:
            raise UngültigerZug("Man kann sich nicht selbst Hinweise geben!")
        if spiel.verfügbareHinweise == 0:
            raise UngültigerZug("Keine Hinweise verfügbar")
        spiel.verfügbareHinweise -= 1
        handKarten = spiel.handKarten[self.zielSpieler]
        passendeKarten = [i for i, karte in enumerate(handKarten) if karte.ist(self.hinweis) ]
        for spieler in spiel.spieler:
            spieler.hinweis(self.zielSpieler, self.hinweis, passendeKarten)
    
    def __str__(self):
        return "{} den Hinweis {} geben".format(self.zielSpieler, self.hinweis)
        
class Abwerfen(Spielzug):
    
    def __init__(self, position):
        self.position = position
        
    def ausführen(self, spiel):
        if spiel.verfügbareHinweise < HanabiSpiel.hinweisPlättchen:
            spiel.verfügbareHinweise += 1
        karte = spiel.handKarten[spiel.aktuellerSpieler][self.position]
        spiel.abwurfStapel.append(karte)
        spiel.zieheKarte(spiel.aktuellerSpieler, self.position)
        for spieler in spiel.spieler:
            spieler.karteAbgeworfen(karte)
    
    def __str__(self):
        return "Karte {} abwerfen".format(self.position)
        
        
class Ablegen(Spielzug):
    
    def __init__(self, position):
        self.position = position
        
    def ausführen(self, spiel):
        karte = spiel.handKarten[spiel.aktuellerSpieler][self.position]
        if spiel.passtAufAblage(karte):
            spiel.ablage[karte.farbe].append(karte)
            for spieler in spiel.spieler:
                spieler.karteAbgelegt(karte)
            spiel.zieheKarte(spiel.aktuellerSpieler, self.position)
        else:
            spiel.abwurfStapel.append(karte)
            for spieler in spiel.spieler:
                spieler.karteAbgeworfen(karte)
            spiel.blitze += 1
            spiel.zieheKarte(spiel.aktuellerSpieler, self.position)
    
    def __str__(self):
        return "Karte {} ablegen".format(self.position)
