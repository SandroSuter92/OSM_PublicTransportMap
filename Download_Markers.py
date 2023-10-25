import pandas as pd
import overpy

# Verbindung zur Overpass API herstellen
api = overpy.Overpass()

# Definieren Sie Ihre Suchanfrage (hier nach touristischen Attraktionen in Luzern)
query = """
area["name"="Luzern"]->.a;
(
  node(area.a)["tourism"];
  way(area.a)["tourism"];
  relation(area.a)["tourism"];
);
out body;
"""

# Führen Sie die Anfrage aus
result = api.query(query)

# Erstellen Sie leere Listen, um die Daten zu speichern
infos = []
names = []
tourisms = []
phones = []
websites = []
latitudes = []
longitudes = []

# Durchsuchen Sie die Ergebnisse und füllen Sie die Listen
for element in result.nodes:
    info = element.tags.get("information", None)
    name = element.tags.get("name", None)
    tourism = element.tags.get("tourism", None)
    phone = element.tags.get("phone", None)
    website = element.tags.get("website", None)
    latitude, longitude = element.lat, element.lon

    # Fügen Sie die Werte zu den entsprechenden Listen hinzu
    infos.append(info)
    names.append(name)
    tourisms.append(tourism)
    phones.append(phone)
    websites.append(website)
    latitudes.append(latitude)
    longitudes.append(longitude)

# Erstellen Sie ein Pandas DataFrame aus den Listen
df = pd.DataFrame({
    "information": infos,
    "name": names,
    "tourism": tourisms,
    "phone": phones,
    "website": websites,
    "Latitude": latitudes,
    "Longitude": longitudes
})

#Erstelle Kategorie Spalte
list_beherbergung = ['hotel', 'hostel','camp_site','motel', 'guest_house', 'apartment','chalet', 'caravan_site']
list_aktivität = ['viewpoint', 'attraction', 'museum', 'picnic_site', 'artwork', 'theme_park', 'gallery']
list_info = ['information']

df_cleaned = df.dropna(subset=["name"])

df_cleaned = df_cleaned.query('information != "guidepost"')

list_tourism = df_cleaned.tourism

list_cat = []

for i in list_tourism:
  if i in list_beherbergung:
    list_cat.append('Beherbergung')
  elif i in list_aktivität:
    list_cat.append('Aktivität')
  else:
    list_cat.append('Information')

df_cleaned['Kategorie'] = list_cat

#Erstelle Beschreibung

lorem_beschreibung = """
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt
ut labore et dolore magna aliquyam erat, sed diam voluptua."""

df_cleaned['Beschreiung'] = lorem_beschreibung

df_cleaned.to_csv('data/markers.csv')