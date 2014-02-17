
from hanabi.spiel import HanabiSpiel
from hanabi.spieler import HanabiSpieler
from hanabi.michaelsKI import Michael
from hanabi.dummeKI import DummerSpieler
from hanabi.jansKI import Jan
import logging
logging.basicConfig(level=logging.DEBUG)
spiel = HanabiSpiel(4, Michael)
from hanabi import gui
from hanabi import simulator
simulator.simulieren(Michael, 4, 100)
#gui.startHanabiGui(spiel)


