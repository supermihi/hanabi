import itertools

import numpy as np

Farben = ["blau", "weiß", "grün", "gelb", "rot"]
Zahlen = [1,2,3,4,5]

class Karte:
    """Klasse für Spielkarten. Jede Karte hat eine Farbe und eine Zahl."""
    
    def __init__(self, farbe, zahl):
        """Erstelle neue Karte mit *farbe* und *zahl*."""
        self.farbe = farbe
        self.zahl = zahl
        self.farbIndex = Farben.index(farbe)
        self.zahlIndex = Zahlen.index(zahl)
        self.index = (self.farbIndex, self.zahlIndex)
    
    def ist(self, farbeOderZahl):
        """Testet ob die Karte eine bestimmte Farbe oder Zahl hat."""
        return self.farbe == farbeOderZahl or self.zahl == farbeOderZahl
    
    def __eq__(self, andere):
        """Karten sind gleich wenn sie beide existieren und in Farbe und Zahl übereinstimmen."""
        if andere is None:
            return False
        return self.farbe == andere.farbe and self.zahl == andere.zahl
    
    @staticmethod
    def komplettesDeck():
        """Erstellt ein komplettes, zufällig gemischtes Kartendeck."""
        stapel = []
        for farbe, zahl in itertools.product(Farben, Zahlen):
            for i in range(Karte.häufigkeit(zahl)):
                stapel.append(Karte(farbe, zahl))
        import numpy
        numpy.random.shuffle(stapel)
        return stapel
    
    @staticmethod
    def häufigkeit(zahl):
        """Gibt an wie häufig eine Karte mit *zahl* im Spiel vorkommt."""
        if zahl == 1:
            return 3
        elif zahl == 5:
            return 1
        else:
            return 2
    
    def __str__(self):
        """Menschenlesbare Darstellung (z.B. "Grüne 3")"""
        return "{}e {}".format(self.farbe.title(), self.zahl)

    __repr__ = __str__
