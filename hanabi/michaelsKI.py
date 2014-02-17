import itertools, math

import numpy as np

from hanabi import Karte, Farben, Zahlen
from hanabi.spieler import HanabiSpieler, HinweisInfo
from hanabi.spielzug import Hinweis, Abwerfen, Ablegen


class Michael(HanabiSpieler):
    
    def entropie(self, spieler, matrix):
        info = self.infos[spieler]
        gesamt = np.sum(matrix)
        if gesamt == 0:
            return 0, 0
        passt = np.sum(matrix*info.passtMaske)/gesamt
        egal = np.sum(matrix*info.egalMaske)/gesamt
        wedernoch = 1 - passt - egal
        return np.sum(((p*np.log2(1/p) if p>0 else 0) for p in (passt,egal,wedernoch))), passt
        
        
    def bewerteHinweis(self, spieler, hinweis):
        sInfo = self.infos[spieler]
        informationsGewinn = 0
        entropieVerlust = 0
        for i in range(self.kartenProSpieler()):
            davor = sInfo.infoMatrix(i)
            davorEntropie, davorPasst = self.entropie(spieler, davor)
            danach = hinweis.anwenden(sInfo.kartenInfos[i], davor)
            danachEntropie, danachPasst = self.entropie(spieler, danach)
            informationsGewinn += np.sum(davor - danach)
            entropieVerlust += davorEntropie - danachEntropie
            if danachPasst > davorPasst:
                entropieVerlust += 2*(danachPasst - davorPasst)
        #return informationsGewinn
        return entropieVerlust
        
    def besterHinweis(self):
        bester = None
        besteWertung = -1
        for abstand, mitspieler in enumerate(self.mitspieler()):
            karten = self.handkartenVon(mitspieler)
            for hinw in Farben + Zahlen:
                passend = [i for i, k in enumerate(karten)
                             if k is not None and k.ist(hinw) ]
                hinweis = HinweisInfo(mitspieler, self.aktuellerSpielzug(), passend, hinw)
                wertung = self.bewerteHinweis(mitspieler, hinweis)-.1*abstand
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
        info = self.infos[self]
        wsPasst = {}
        wsEgal = {}
        wsKritisch = {}
        for i in range(self.kartenProSpieler()):
            if not self.habeKarteInPosition(i):
                continue
            wsPasst[i] = info.wsPasst(i)
            if wsPasst[i] > (0.7 if self.verfügbareBlitze() > 0 else 1):
                erwZahl = info.erwZahl(i)
                sicher.append( (wsPasst[i], erwZahl, Ablegen(i)))
                print("{} kann {} mit WS {} ablegen".format(self, i, wsPasst[i]))
            wsEgal[i] = info.wsEgal(i)
            wsKritisch[i] = info.wsKritisch(i)
            if wsEgal[i] > 0.8 and wsKritisch[i] == 0:
                sicher.append( (wsEgal[i], 100, Abwerfen(i)))
                print("{} kann {} mit WS {} abwerfen".format(self, i, wsEgal[i]))
        if len(sicher):
            wertung, ws, zug = min(sicher, key=lambda t: (-t[0], t[1]))
            if isinstance(zug, Ablegen) and ws == 1:
                print("INFO: {}".format(info.infoMatrix(zug.position)))
                print("PASST: {}".format(info.passtMaske))
            return zug
        best = max(wsPasst, key=lambda pos: wsPasst[pos])
        print("max sicherheit: {} auf {}".format(best, wsPasst[best]))
        if self.verfügbareHinweise() > 0:
            (mitspieler, hinw), wertung = self.besterHinweis()
            if wertung > 0:
                return Hinweis(mitspieler, hinw)
        sicherste = min(wsKritisch, key=lambda pos: wsKritisch[pos])
        print("notfall: werfe {} ab; ws = {}".format(sicherste, wsKritisch[sicherste]))
        return Abwerfen(sicherste)
        
            
