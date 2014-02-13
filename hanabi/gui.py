import sys, math
from collections import OrderedDict

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

from hanabi import Farben, Zahlen
from hanabi.spielzug import Ablegen, Abwerfen, Hinweis, UngültigerZug
from hanabi.spiel import SpielEnde
from hanabi.spieler import HanabiSpieler

KartenGröße   = QtCore.QRectF(-15, -25, 30, 50)
KartenAbstand = KartenGröße.width() / 3
SpielfeldRadius = 150
colorMap = {
          "blau" : Qt.cyan,
          "weiß" : Qt.white,
          "grün" : Qt.green,
          "gelb" : Qt.yellow,
          "rot"  : Qt.red
        }

class HanabiFenster(QtGui.QWidget):
    
    def __init__(self, spiel):
        super().__init__()
        self.spiel = spiel
        self.setWindowTitle("Hanabi")
        layout = QtGui.QHBoxLayout()
        self.spielfeld = QtGui.QGraphicsScene()
        self.spielfeld.fenster = self
        self.spielfeldView = QtGui.QGraphicsView(self.spielfeld)
        self.initSpielfeld()
        layout.addWidget(self.spielfeldView)
        
        buttonBox = QtGui.QVBoxLayout()
        buttonBox.addWidget(QtGui.QLabel("KI-Spieler:"))
        combobox = QtGui.QComboBox()
        clses = HanabiSpieler.__subclasses__()
        for cls in clses:
            combobox.addItem(cls.__name__, cls)
        buttonBox.addWidget(combobox)
        combobox.activated.connect(self.setSpielerKlasse)
        self.clsBox = combobox
        combobox.setCurrentIndex(clses.index(type(spiel.spieler[0])))
        
        anzahlBox = QtGui.QSpinBox()
        anzahlBox.setRange(2, 5)
        buttonBox.addWidget(anzahlBox)
        anzahlBox.setValue(spiel.spielerAnzahl)
        anzahlBox.valueChanged.connect(self.setSpielerZahl)
        kartenGebenButton = QtGui.QPushButton("Karten geben")
        buttonBox.addWidget(kartenGebenButton)
        kartenGebenButton.clicked.connect(self.initSpiel)
        autoZugButton = QtGui.QPushButton("KI-Zug")
        autoZugButton.clicked.connect(self.autoSpielzug)
        spielDurchlaufenButton = QtGui.QPushButton("KI bis ende")
        spielDurchlaufenButton.clicked.connect(self.durchlaufen)
        buttonBox.addWidget(autoZugButton)
        buttonBox.addWidget(spielDurchlaufenButton)
        buttonBox.addStretch()
        layout.addLayout(buttonBox)
        
        self.setLayout(layout)
        self.show()
        self.initSpiel() # zum Testen
        self.resize(1000, 650)
    
    def initSpielfeld(self):
        self.spielfeld.clear()
        self.spielerItems = []
        for i, spieler in enumerate(self.spiel.spieler):
            spielerItem = SpielerGraphicsItem(self.spiel, spieler)
            self.spielerItems.append(spielerItem)
            self.spielfeld.addItem(spielerItem)
            winkel = 2*math.pi/self.spiel.spielerAnzahl*i
            spielerItem.setPos(SpielfeldRadius*math.cos(winkel),
                               SpielfeldRadius*math.sin(winkel))
            spielerItem.setRotation(math.degrees(winkel)+90)
        
        self.ablage = AblageGraphicsItem(self.spiel)
        self.spielfeld.addItem(self.ablage)
        
        self.infofeld = InfoFeld(self.spiel)
        self.spielfeld.addItem(self.infofeld)
        self.infofeld.setPos(self.spielfeld.itemsBoundingRect().left() - 50 - self.infofeld.boundingRect().width(),
            -self.infofeld.boundingRect().height()/2)
            
        self.abwurf = AbwurfGraphicsItem(self.spiel)
        self.spielfeld.addItem(self.abwurf)
        self.abwurf.setPos(self.spielfeld.itemsBoundingRect().topRight())
        
        self.spielfeld.setSceneRect(self.spielfeld.itemsBoundingRect())

    def setSpielerKlasse(self, index):
        self.spiel.SpielerKlasse = self.clsBox.itemData(index)
        self.spiel.initSpieler()
        self.initSpielfeld()
        
    def setSpielerZahl(self, value):
        self.spiel.setSpielerAnzahl(value)
        self.spiel.initSpieler()
        self.initSpielfeld()
    
    def aktualisiere(self):
        for item in self.spielerItems:
            item.aktualisiere()
        self.abwurf.aktualisiere()
        self.ablage.aktualisiere()
        self.infofeld.aktualisiere()
    
    
    def autoSpielzug(self):
        return self.triggerSpielzug(self.spiel.aktuellerSpieler.macheSpielzug())
    
    def durchlaufen(self):
        try:
            self.spiel.autoSpiel()
        except UngültigerZug:
            pass
        except SpielEnde:
            pass
        self.aktualisiere()
    
    def triggerSpielzug(self, spielzug):
        try:
            self.spiel.spielzug(spielzug)
            self.aktualisiere()
            return True
        except UngültigerZug as e:
            self.aktualisiere()
            QtGui.QMessageBox.warning(self, "Ungültiger Zug", str(e))
            return False
        except SpielEnde as e:
            self.aktualisiere()
            QtGui.QMessageBox.information(self, "Spielende", str(e))
            return False
        
    def initSpiel(self):
        self.spiel.kartenGeben()
        self.aktualisiere()
    
    
class KarteGraphicsItem(QtGui.QGraphicsRectItem):
    
    def __init__(self, karte):
        super().__init__(KartenGröße)
        
        self.zahlItem = QtGui.QGraphicsSimpleTextItem()
        self.zahlItem.setParentItem(self)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(20)
        self.zahlItem.setFont(font)
        self.zahlItem.setAcceptedMouseButtons(Qt.NoButton)
        self.infoItem = QtGui.QGraphicsSimpleTextItem()
        self.infoItem.setParentItem(self)
        self.infoItem.setPos(self.boundingRect().topLeft())
        self.setKarte(karte)
    
    def setKarte(self, karte):
        self.karte = karte
        if karte is not None:
            farbe = colorMap[karte.farbe]
            zahl = karte.zahl
        else:
            farbe = Qt.gray
            zahl = "?"
        self.setBrush(QtGui.QBrush(farbe))
        self.zahlItem.setText(str(zahl))
        zahlRect = self.zahlItem.boundingRect()
        self.zahlItem.setPos(-zahlRect.width()/2, -zahlRect.height()/2)


class SpielerGraphicsItem(QtGui.QGraphicsRectItem):
    
    def __init__(self, spiel, spieler):
        super().__init__()
        self.spiel = spiel
        self.spieler = spieler
        self.setPen(QtGui.QPen(Qt.NoPen))
        self.kartenItems = [KarteGraphicsItem(None) for _ in range(spiel.kartenProSpieler)]
        gesamtBreite = spiel.kartenProSpieler*KartenGröße.width() \
                     + (spiel.kartenProSpieler - 1)*KartenAbstand
        for i, item in enumerate(self.kartenItems):
            item.setParentItem(self)
            item.setPos(-gesamtBreite/2 + KartenGröße.width()/2 + i*(KartenGröße.width() + KartenAbstand),
                        0)
        self.setTransformOriginPoint(self.boundingRect().center())
        label = QtGui.QGraphicsSimpleTextItem("Spieler {}".format(spieler.nummer))
        font = QtGui.QFont()
        font.setPointSize(12)
        label.setFont(font)
        label.setPos(-label.boundingRect().width()/2,
                     -KartenGröße.height()/2 - 15 - label.boundingRect().height() / 2)
        label.setParentItem(self)
        self.label = label
        self.setRect(self.childrenBoundingRect())
        self.aktualisiere()
    
    def aktualisiere(self):
        self.label.setPen(QtGui.QPen(Qt.green if self.spieler is self.spiel.aktuellerSpieler
                                            else Qt.black))
        for i, karte in enumerate(self.spiel.handKarten[self.spieler]):
            if self.kartenItems[i].karte != karte:
                self.kartenItems[i].setKarte(karte)
            self.kartenItems[i].setToolTip(self.spiel.aktuellerSpieler.infos[self.spieler][i].toHTML())
            hinweise = set()
            for hinweis in self.spieler.hinweise:
                if hinweis.spieler is self.spieler:
                    if hinweis.spielzug >= self.spieler.infos[self.spieler][i].seitSpielzug:
                        if i in hinweis.positionen:
                            hinweise.add(hinweis.art)
            self.kartenItems[i].infoItem.setText("/".join(str(h) for h in hinweise))
    
    
    def mousePressEvent(self, event):
        for i, item in enumerate(self.kartenItems):
            if item.contains(item.mapFromParent(event.pos())):
                if self.spieler is self.spiel.aktuellerSpieler:
                    items = ["Ablegen", "Abwerfen"]
                    ans, ok = QtGui.QInputDialog.getItem(
                        None,
                        "Ablegen oder abwerfen?",
                        "Die {} ...".format(item.karte),
                        items, 0, False)
                    if ok:
                        if ans == items[0]:
                            zug = Ablegen(i)
                        else:
                            zug = Abwerfen(i)
                else:
                    items = ["Farbe ({})".format(item.karte.farbe),
                             "Zahl ({})".format(item.karte.zahl)]
                    ans, ok = QtGui.QInputDialog.getItem(
                        None,
                        "Farb- oder Zahltipp?",
                        "Tipp zu: ",
                        items, 0, False)
                    if ok:
                        zug = Hinweis(self.spieler, item.karte.farbe if ans == items[0] else item.karte.zahl)
                if ok:
                    self.scene().fenster.triggerSpielzug(zug)
                    event.accept()
                    return

class AblageGraphicsItem(QtGui.QGraphicsRectItem):
    
    def __init__(self, spiel):
        super().__init__()
        self.spiel = spiel
        self.setPen(QtGui.QPen(Qt.NoPen))
        self.stapel = OrderedDict()
        breite = KartenGröße.width()*len(Farben) + KartenAbstand*(len(Farben)-1)
        for i, farbe in enumerate(Farben):
            karteItem = KarteGraphicsItem(None)
            karteItem.setParentItem(self)
            karteItem.setPos(-breite/2 + KartenGröße.width()/2 + i*(KartenGröße.width() + KartenAbstand), 0)
            self.stapel[farbe] = karteItem
        self.setRect(self.childrenBoundingRect())
        
    def aktualisiere(self):
        for farbe in Farben:
            try:
                oben = self.spiel.ablage[farbe][-1]
            except IndexError:
                oben = None
            if self.stapel[farbe].karte != oben:
                self.stapel[farbe].setKarte(oben)
        

class InfoFeld(QtGui.QGraphicsSimpleTextItem):
    
    _text = ("Hinweise: {h}\n"
            "Blitze: {b}\n"
            "Stapel: {s}\n"
            "Spielzug: {z}\n"
            "Letzter Zug: {l}\n"
            "Punkte: {p}")
    
    def __init__(self, spiel):
        super().__init__()
        self.spiel = spiel
        font = QtGui.QFont()
        font.setPointSize(16)
        self.setFont(font)
        self.aktualisiere()
        
    def aktualisiere(self):
        spiel = self.spiel
        self.setText(InfoFeld._text.format(
            h=spiel.verfügbareHinweise,
            b=spiel.blitze,
            s=len(spiel.stapel),
            z=spiel.aktuellerSpielzug,
            l=spiel.letzterSpielzug or "???",
            p=spiel.punktzahl()))

class AbwurfGraphicsItem(QtGui.QGraphicsRectItem):
    
    def __init__(self, spiel):
        super().__init__()
        font = QtGui.QFont()
        font.setPointSize(16)
        self.setPen(QtGui.QPen(Qt.NoPen))
        text = QtGui.QGraphicsSimpleTextItem("Abgeworfene Karten")
        text.setFont(font)
        text.setParentItem(self)
        self.text = text
        self.setRect(self.childrenBoundingRect())
        self.spiel = spiel
        self.zurückSetzen()
    
    def zurückSetzen(self):
        self.spalte = 0
        self.karteItems = []
        self.koordinate = self.text.boundingRect().bottomLeft() + QtCore.QPoint(KartenGröße.width()/2, KartenGröße.height()/2 + KartenAbstand)
        
        
    def aktualisiere(self):
        if len(self.karteItems) == len(self.spiel.abwurfStapel):
            return
        if len(self.karteItems) > len(self.spiel.abwurfStapel):
            for item in self.karteItems:
                item.scene().removeItem(item)
            self.zurückSetzen()
        for karte in self.spiel.abwurfStapel[len(self.karteItems):]:
            karteItem = KarteGraphicsItem(karte)
            karteItem.setPos(self.koordinate)
            karteItem.setParentItem(self)
            self.spalte += 1
            if self.spalte == 4:
                self.spalte = 0
                self.koordinate.setX(self.text.boundingRect().left() + KartenGröße.width()/2)
                self.koordinate.setY(self.koordinate.y() + KartenGröße.height() + KartenAbstand)
            else:
                self.koordinate.setX(self.koordinate.x() + KartenGröße.width() + KartenAbstand)
            self.karteItems.append(karteItem)
        self.setRect(self.childrenBoundingRect())
                
            


app = None
def startHanabiGui(spiel):
    global app
    app = QtGui.QApplication(sys.argv)
    fenster = HanabiFenster(spiel)
    app.exec_()
