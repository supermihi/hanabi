import itertools, math

from hanabi.spiel import Karte
from hanabi import Farben, Zahlen
from hanabi.spieler import HanabiSpieler, HinweisInformation
from hanabi.spielzug import Hinweis, Abwerfen, Ablegen

        
class Michael(HanabiSpieler):
    
    def bewerteHinweis(self, spieler, hinweis):
        ausgenullt = 0
        multiplikator = 1
        infos = self.infos[spieler]
        handkarten = self.handkartenVon(spieler)
        passende = [k for k in handkarten if self.passtAufAblage(k) and k.ist(hinweis.art)]
        if self.aktuellerSpielzug() <= 2*self.spielerAnzahl() and len(passende) == 0:
            return 0
        for i, info in enumerate(infos):
            karte = handkarten[i]
            if not karte:
                continue
            if self.passtAufAblage(karte):
                multiplikator += .1
            elif self.nichtMehrBenötigt(karte):
                multiplikator += .1
            for (farbe, zahl), nummer in info.items():
                if info.position in hinweis.positionen:
                    if farbe != hinweis.art and zahl != hinweis.art and info[farbe, zahl] > 0:
                        ausgenullt += 1 #math.sqrt(zahl)*math.sqrt(nummer)
                else:
                    if farbe == hinweis.art or zahl == hinweis.art and info[farbe, zahl] > 0:
                        ausgenullt += 1 #math.sqrt(zahl)*math.sqrt(nummer)
        if hinweis.art in Zahlen:
            multiplikator += .1
        return ausgenullt*multiplikator
    
    def besterHinweis(self):
        bester = None
        besteWertung = 0
        for mitspieler in self.mitspieler():
            karten = self.handkartenVon(mitspieler)
            for hinw in Farben + Zahlen:
                passend = [i for i, k in enumerate(karten)
                             if k is not None and k.ist(hinw) ]
                hinweis = HinweisInformation(mitspieler, self.aktuellerSpielzug(), passend, hinw)
                wertung = self.bewerteHinweis(mitspieler, hinweis)
                if wertung > besteWertung:
                    besteWertung = wertung
                    bester = (mitspieler, hinw)
        print("beste Wertung: {}".format(besteWertung))
        return bester, besteWertung
        
    def nichtMehrBenötigt(self, karte):
        """Gibt an ob *karte* /sicher/ nicht mehr benötigt wird."""
        return self.abgelegteKarten(karte.farbe) >= karte.zahl

    def macheSpielzug(self):
        # teste auf sichere Spielzüge
        sicher = []
        wsPasst = {}
        wsUnnötig = {}
        for i, info in enumerate(self.infos[self]):
            if not self.habeKarteInPosition(i):
                continue
            möglich = info.möglicheKarten()            
            wsPasst[i] = len([k for k in möglich if self.passtAufAblage(k)]) / len(möglich)
            if wsPasst[i] > (0.7 if self.verfügbareBlitze() > 0 else 1):
                erwZahl = sum(karte.zahl for karte in möglich)/len(möglich)
                sicher.append( (erwZahl, Ablegen(i)))
                print("{} kann {} mit WS {} ablegen".format(self, i, wsPasst[i]))
            wsUnnötig[i] = len([k for k in möglich if self.nichtMehrBenötigt(k)]) / len(möglich)
            if wsUnnötig[i] > 0.8:
                sicher.append( (100, Abwerfen(i)))
                print("{} kann {} mit WS {} abwerfen".format(self, i, wsUnnötig[i]))
        if len(sicher):
            wertung, zug = min(sicher, key=lambda t: t[0])
            return zug
        best = max(wsPasst, key = lambda pos: wsPasst[pos])
        print("max sicherheit: {} auf {}".format(best, wsPasst[best]))
        if self.verfügbareHinweise() > 0:
            (mitspieler, hinw), wertung = self.besterHinweis()
            if wertung > 0:
                return Hinweis(mitspieler, hinw)
        sicherste = max(wsUnnötig, key = lambda pos: wsUnnötig[pos])
        print("notfall: werfe {} ab; ws = {}".format(sicherste, wsUnnötig[sicherste]))
        return Abwerfen(sicherste)
        
            
