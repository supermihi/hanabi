from hanabi.spiel import HanabiSpiel

def simulieren(StrategieKlasse, spielerZahl, anzahlSpiele):
    spiel = HanabiSpiel(spielerZahl, StrategieKlasse)
    attribute = "Punkte", "Hinweise", "Blitze"
    summe = {attribut: 0 for attribut in attribute}
    minima = {attribut: 10000 for attribut in attribute}
    maxima = {attribut: 0 for attribut in attribute}
    for i in range(anzahlSpiele):
        print("simuliere spiel {} von {}".format(i+1, anzahlSpiele))
        spiel.kartenGeben()
        try:
            spiel.autoSpiel()
        except:
            pass
        ergebnisse = dict(Punkte=spiel.punktzahl(),
            Hinweise=spiel.verfügbareHinweise,
            Blitze=spiel.blitze)
        for attribut in attribute:
            if ergebnisse[attribut] < minima[attribut]:
                minima[attribut] = ergebnisse[attribut]
            if ergebnisse[attribut] > maxima[attribut]:
                maxima[attribut] = ergebnisse[attribut]
            summe[attribut] += ergebnisse[attribut]
    print("Durchschnitt:")
    for attribut, wert in summe.items():
        print("{}={}".format(attribut, wert / anzahlSpiele))
    print(minima)
    print(maxima)
