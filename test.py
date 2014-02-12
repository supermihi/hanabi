
from hanabi.spiel import HanabiSpiel
from hanabi.spieler import HanabiSpieler
from hanabi.michaelsKI import Michael
from hanabi.dummeKI import DummerSpieler
from hanabi.jansKI import Jan

spiel = HanabiSpiel(4, Jan)
spiel.kartenGeben()
from hanabi import gui

gui.startHanabiGui(spiel)


