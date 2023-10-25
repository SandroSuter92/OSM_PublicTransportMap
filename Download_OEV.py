import pandas as pd
import overpy

# Verbindung zur Overpass API herstellen
api = overpy.Overpass()

# Definieren Sie Ihre Suchanfrage (hier nach touristischen Attraktionen in Luzern)
query = """
area["name"="Luzern"]->.a;
(
  node(area.a)["highway"="bus_stop"];
  node(area.a)["railway"="station"];
);
out center;
"""

# Führen Sie die Anfrage aus
result = api.query(query)

# Erstellen Sie leere Listen, um die Daten zu speichern
names = []
operator = []
wheelchair = []
latitudes = []
longitudes = []

# Durchsuchen Sie die Ergebnisse und füllen Sie die Listen
for element in result.nodes:
    d_name = element.tags.get("uic_name", None)
    d_operator = element.tags.get("operator", None)
    d_wheelchair = element.tags.get("wheelchair", None)
    latitude, longitude = element.lat, element.lon

    # Fügen Sie die Werte zu den entsprechenden Listen hinzu
    names.append(d_name)
    operator.append(d_operator)
    wheelchair.append(d_wheelchair)
    latitudes.append(latitude)
    longitudes.append(longitude)

# Erstellen Sie ein Pandas DataFrame aus den Listen
df = pd.DataFrame({
    "name": names,
    "operator": operator,
    "Latitude": latitudes,
    "Longitude": longitudes
})

df.to_csv('data/oev_haltestellen.csv')