
from hanabi.spiel import HanabiSpiel
from hanabi.spieler import HanabiSpieler
from hanabi.michaelsKI import Michael
from hanabi.dummeKI import DummerSpieler

spiel = HanabiSpiel(4, DummerSpieler)
spiel.kartenGeben()
from hanabi import gui

gui.startHanabiGui(spiel)


