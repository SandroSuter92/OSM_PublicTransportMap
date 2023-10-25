from math import radians, sin, cos, sqrt, atan2

# Funktion zur Berechnung der Entfernung zwischen zwei geographischen Koordinaten
def haversine(lat1, lon1, lat2, lon2):
    # Umrechnung der Breiten- und Längengrade von Grad in Radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine-Formel
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Radius der Erde in Kilometern (ca. 6371 km)
    r = 6371

    # Berechnung der Entfernung
    distance = r * c
    return distance