import itertools

from hanabi.spieler import HanabiSpieler
from hanabi.spielzug import *

class Jan(HanabiSpieler):
    
    def macheSpielzug(self):
        for hinweis in self.hinweise:
            if hinweis.spielzug == self.aktuellerSpielzug() - 1:
                position = self.ältesteKarte(self, hinweis.positionen)
                if self.verfügbareBlitze() == 0 and len(hinweis.positionen) > 1:
                    möglich = self.infos[self][position].möglicheKarten()
                    if all(self.passtAufAblage(karte) for karte in möglich):
                        return Ablegen(position)
                    else:
                        print("sicher ist sicher")
                        print(möglich)
                        
                else:
                    return Ablegen(position)
        nächster = self.mitspieler()[0]
        if self.verfügbareHinweise() > 0:
            passendeKarten = [karte for karte in self.handkartenVon(nächster) if self.passtAufAblage(karte)]
            bester = (10, None)
            for karte in passendeKarten:
                for hinweis in karte.farbe, karte.zahl:
                    zutreffend = [k for k in self.handkartenVon(nächster) if karte.ist(hinweis)]
                    if len(zutreffend) < bester[0] or (len(zutreffend) == bester[0] and hinweis in Zahlen):
                        bester = (len(zutreffend), hinweis)
            if bester[1] is not None:
                return Hinweis(nächster, bester[1])
        return Abwerfen(self.ältesteKarte())
                    
