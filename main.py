from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy_garden.mapview import MapView, MapMarker
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

import pandas as pd
import requests
from tabulate import tabulate

from imports import haversine

haltestellen = pd.read_csv('data/oev_haltestellen.csv')
markers = pd.read_csv('data/markers.csv')

me_lat = 47.043846
me_lon = 8.315501

class SplitScreenApp(App):

    def __init__(self, **kwargs):
        super(SplitScreenApp, self).__init__(**kwargs)
        self.nearest_point_name = 'Not defined'


        self.haltestellen = pd.read_csv('data/oev_haltestellen.csv')
        self.markers = pd.read_csv('data/markers.csv')
        self.markers.fillna('not Available', inplace=True)
        self.df = pd.DataFrame(columns=['Start', 'Abfahrtszeit', 'Ziel', 'Ankunftszeit', 'Verbindungsnummer'],
                                       data=[['','','','','']])

        self.start = 'Not defined'
        self.shown_df = 'Not defined'
        self.end = 'Not defined'
        self.way = 'Fahrplan'

        self.shown_df = self.df.to_string(index=False, justify='center', col_space=40)  # Initialer Text für das Label

        self.me_lat = 47.043846
        self.me_lon = 8.315501

        # Berechne die Entfernungen für jeden Datenpunkt im DataFrame
        self.haltestellen["Distance"] = haltestellen.apply(lambda row: haversine(me_lat, me_lon, row["Latitude"], row["Longitude"]), axis=1)

        # Finde den Datenpunkt mit der geringsten Entfernung
        self.nearest_point = self.haltestellen.loc[self.haltestellen["Distance"].idxmin()]
        self.nearest_point_name = str(self.nearest_point["name"])

    def build(self):
        # Haupt-Layout erstellen
        layout = BoxLayout(orientation='horizontal', spacing=0, padding=0)

        # Linker Teil (1/3 des Bildschirms)
        left_panel = BoxLayout(orientation='vertical', size_hint=(1 / 3, 1))

        # Füge ein Bild hinzu (hier 'sample_image.png' ersetzen)
        image = Image(source='images/Logo.png', size=(400, 400), pos_hint={'center_x': 0.5, 'center_y': 1})
        left_panel.add_widget(image)

        # Button für "Hello World"
        start_button = Button(text=self.nearest_point_name, size_hint_y=None, height=40)

        left_panel.add_widget(start_button)

        # Suchfeld für die Dropdown-Filterung
        search_input = TextInput(hint_text='Suche...', multiline=False, size_hint_y=None, height=40, width=10)
        left_panel.add_widget(search_input)

        # Dropdown-Menü für Endhaltestelle
        end_dropdown = DropDown()
        end_button = Button(text=self.end, size_hint_y=None, height=40)
        end_button.bind(on_release=end_dropdown.open)
        end_dropdown.bind(on_select=lambda instance, x: setattr(end_button, 'text', x) or setattr(self, 'end', x))
        haltestellen['name'].fillna('nan', inplace=True)
        list_halt = list(set(haltestellen['name']))

        for stop in sorted(list_halt):
            if str(stop) == 'nan':
                next
            else:
                btn = Button(text=str(stop), size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn: end_dropdown.select(btn.text))
                end_dropdown.add_widget(btn)

                # Suchfunktion für das Dropdown-Menü
        def filter_options(instance, value):
            end_dropdown.clear_widgets()  # Lösche alle vorhandenen Buttons im Dropdown
            for city in sorted(list_halt):
                if value.lower() in city.lower():
                    btn = Button(text=city, size_hint_y=None, height=40)
                    btn.bind(on_release=lambda btn: end_dropdown.select(btn.text))
                    end_dropdown.add_widget(btn)

        search_input.bind(text=filter_options)

        left_panel.add_widget(end_button)

        layout.add_widget(left_panel)

        # Rechter Teil (2/3 des Bildschirms)
        right_panel = BoxLayout(orientation='vertical', size_hint=(2 / 3, 1))

        # Füge die MapView zum rechten Panel hinzu
        mapview = MapView(zoom=10, lat=47.050440256962446, lon=8.307181146159728, size_hint= (1, 8/10))

        # Füge Marker für meinen Standort hinzu

        marker = MapMarker(lat=self.me_lat, lon=self.me_lon, source='markers/marker.png')
        mapview.add_marker(marker)

        # Füge die Marker Aktivität zur Karte hinzu
        self.activities = self.markers.loc[self.markers['Kategorie'] == 'Aktivität']
        self.activities = self.activities.reset_index()

        self.coordinates = []
        self.markers_info = []

        for i in range(len(self.activities)):
            x_data = self.activities['Latitude']
            y_data = self.activities['Longitude']
            x = x_data.loc[i]
            y = y_data.loc[i]
            z = (x,y)
            self.coordinates.append(z)

        for i in range(len(self.activities)):
            x = self.activities.loc[i]['name']
            y = self.activities.loc[i]['Beschreiung']
            z = {'name': x, 'keyword': y}
            self.markers_info.append(z)

        # Füge Marker mit Namen und Stichworten hinzu
        for i, (lat, lon) in enumerate(self.coordinates):

            marker_info = self.markers_info[
                i % len(self.markers_info)]  # Wiederholt Informationen, wenn mehr Marker als Informationen vorhanden sind

            # Erstellen Sie den Marker und fügen Sie Informationen als Eigenschaft hinzu
            marker = MapMarker(lat=float(lat), lon=float(lon), source='markers/activities.png')
            marker.info = marker_info

            marker.bind(on_press=lambda marker: self.show_popup(marker.info, 'activities.png'))
            mapview.add_marker(marker)

        # Füge die Marker Beherbergung zur Karte hinzu
        self.beherbergung = self.markers.loc[self.markers['Kategorie'] == 'Beherbergung']
        self.beherbergung = self.beherbergung.reset_index()

        self.coordinates = []
        self.markers_info = []

        for i in range(len(self.beherbergung)):
            x_data = self.beherbergung['Latitude']
            y_data = self.beherbergung['Longitude']
            x = x_data.loc[i]
            y = y_data.loc[i]
            z = (x, y)
            self.coordinates.append(z)

        for i in range(len(self.beherbergung)):
            x = self.beherbergung.loc[i]['name']
            y = self.beherbergung.loc[i]['Beschreiung']
            z = {'name': x, 'keyword': y}
            self.markers_info.append(z)

        #Füge Marker mit Namen und Stichworten hinzu
        for i, (lat, lon) in enumerate(self.coordinates):
            marker_info = self.markers_info[
                i % len(
                    self.markers_info)]  # Wiederholt Informationen, wenn mehr Marker als Informationen vorhanden sind

            # Erstellen Sie den Marker und fügen Sie Informationen als Eigenschaft hinzu
            marker = MapMarker(lat=float(lat), lon=float(lon), source='markers/beherbergung.png')
            marker.info = marker_info

            marker.bind(on_press=lambda marker: self.show_popup(marker.info, 'hotel.png'))
            mapview.add_marker(marker)

        # Füge die Marker information zur Karte hinzu
        self.info = self.markers.loc[self.markers['Kategorie'] == 'Information']
        self.info = self.info.reset_index()

        self.coordinates = []
        self.markers_info = []

        for i in range(len(self.info)):
            x_data = self.info['Latitude']
            y_data = self.info['Longitude']
            x = x_data.loc[i]
            y = y_data.loc[i]
            z = (x, y)
            self.coordinates.append(z)

        for i in range(len(self.info)):
            x = self.info.loc[i]['name']
            y = self.info.loc[i]['Beschreiung']
            z = {'name': x, 'keyword': y}
            self.markers_info.append(z)

        # Füge Marker mit Namen und Stichworten hinzu
        for i, (lat, lon) in enumerate(self.coordinates):
            marker_info = self.markers_info[
                i % len(self.markers_info)]  # Wiederholt Informationen, wenn mehr Marker als Informationen vorhanden sind
            #
            # Erstellen Sie den Marker und fügen Sie Informationen als Eigenschaft hinzu
            marker = MapMarker(lat=float(lat), lon=float(lon), source='markers/information.png')
            marker.info = marker_info
            #
            marker.bind(on_press=lambda marker: self.show_popup(marker.info, 'info.png'))
            mapview.add_marker(marker)

        right_panel.add_widget(mapview)

        bottom_panel = BoxLayout(orientation='horizontal')

        # Button für "Hello World"
        hello_button = Button(text='Verbindung suchen', size_hint=(1, 0.1))
        hello_button.bind(on_release=self.say_hello)
        right_panel.add_widget(hello_button)

        # Label für das Hello World-Statement
        self.hello_label = Label(text=self.shown_df, size_hint=(1,0.4), pos_hint={'top': 1})
        right_panel.add_widget(self.hello_label)

        # Fahrplan
        scrollview = ScrollView()
        self.way_label = Label(text=self.way, size_hint_y=None)
        self.way_label.bind(texture_size=self.way_label.setter('size'))
        scrollview.add_widget(self.way_label)

        right_panel.add_widget(scrollview)

        layout.add_widget(right_panel)
        return layout

    def update_end(self, selected_option):
        print(self.end)
        self.end = selected_option
        print(str(self.end))

    def show_popup(self, marker_info, image):
        name = marker_info['name']
        keyword = marker_info['keyword']

        # Erstelle ein ScrollView für das mehrzeilige Keyword
        scrollview = ScrollView()
        keyword_label = Label(text=keyword, halign='left', valign='top', size_hint_y=None, height=90)
        scrollview.add_widget(keyword_label)

        # Füge ein Bild hinzu (hier 'sample_image.png' ersetzen)
        image = Image(source='images/{}'.format(image), size_hint=(None, None), size=(200, 200), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        popup_content = BoxLayout(orientation='vertical')
        popup_content.add_widget(Label(text=f'[b]{name}', markup=True,bold=True, font_size=60))
        popup_content.add_widget(image)  # Füge das Bild zum Popup-Inhalt hinzu
        popup_content.add_widget(Label(text='[b]Beschreibung:', markup=True,bold=True))
        popup_content.add_widget(scrollview)  # Füge das ScrollView zum Popup-Inhalt hinzu

        popup = Popup(title='Marker Information', content=popup_content, size_hint=(None, None), size=(1000, 800))
        popup.open()

    def say_hello(self, instance):

        # Definieren Sie die API-Endpunkt-URL
        url = "http://transport.opendata.ch/v1/connections"

        # Definieren Sie die Abfahrts- und Zielhaltestellen
        from_station = str(self.nearest_point_name)
        to_station = str(self.end)

        # Führen Sie die API-Anfrage durch
        response = requests.get(url, params={"from": from_station, "to": to_station})

        # Überprüfen Sie den Status der Anfrage
        if response.status_code == 200:
            # Die API-Antwort ist ein JSON-Objekt
            data = response.json()
            # Verarbeiten Sie die Daten hier nach Bedarf
            self.start_haltestelle = data['connections'][0]['from']['station']['name']
            self.abhfahrtszeit = data['connections'][0]['from']['departure'][11:16]
            self.end_haltestelle = data['connections'][0]['to']['station']['name']
            self.ankunftszeit = data['connections'][0]['to']['arrival'][11:16]
            self.dauer = data['connections'][0]['duration']
            self.busnummer = data['connections'][0]['sections'][0]['journey']['number']
            self.bus_endstation = data['connections'][0]['sections'][0]['journey']['to']

            self.df_new = pd.DataFrame(columns=['Start', 'Abfahrtszeit', 'Ziel', 'Ankunftszeit', 'Verbindungsnummer'],
                                       data=[[self.start_haltestelle, self.abhfahrtszeit, self.end_haltestelle, self.ankunftszeit, self.busnummer]])

            df_path = pd.DataFrame(columns=['Haltestelle', 'x', 'y', 'Zeit'])

            for i in data['connections'][0]['sections'][0]['journey']['passList']:
                list_path = []
                list_path.append(i['station']['name'].ljust(80))
                list_path.append(i['station']['coordinate']['x'])
                list_path.append(i['station']['coordinate']['y'])
                list_path.append(i['arrival'])

                df_path.loc[len(self.df)] = list_path
            print('variables created')
        else:
            print("Fehler bei der API-Anfrage.")

        self.shown_df = tabulate(self.df_new, headers='keys', showindex="never")
        self.hello_label.text = self.shown_df # Aktualisieren Sie das Label-Textattribut

        start_haltestelle = data['connections'][0]['from']['station']['name']
        abhfahrtszeit = data['connections'][0]['from']['departure']
        end_haltestelle = data['connections'][0]['to']['station']['name']
        ankunftszeit = data['connections'][0]['to']['arrival']
        dauer = data['connections'][0]['duration']
        busnummer = data['connections'][0]['sections'][0]['journey']['number']
        bus_endstation = data['connections'][0]['sections'][0]['journey']['to']

        df = pd.DataFrame(columns=['Haltestelle', 'x', 'y', 'Plattform', 'Zeit'])

        check = len(data['connections'][0]['sections'])


        for x in range(check):
            if data['connections'][0]['sections'][x]['journey'] == None:
                next
            else:
                for i in data['connections'][0]['sections'][x]['journey']['passList']:
                    list_path = []
                    list_path.append(i['station']['name'].ljust(80))
                    list_path.append(i['station']['coordinate']['x'])
                    list_path.append(i['station']['coordinate']['y'])
                    if i['platform'] == None:
                        list_path.append(i['platform'])
                    else:
                        list_path.append(i['platform'].ljust(80))

                    if i['arrival'] == None:
                        list_path.append(i['arrival'])
                    else:
                        list_path.append(i['arrival'][11:16].ljust(80))

                    df.loc[len(df)] = list_path

        df = df.drop(columns=['x','y'])
        self.way = tabulate(df, headers='keys', colalign=('left',),showindex="never")

        self.way_label.text = self.way # Aktualisieren Sie das Label-Textattribut


    def on_end_haltestelle_selected(self, selected_haltestelle):
        # Diese Funktion wird aufgerufen, wenn eine Endhaltestelle ausgewählt wird
        self.selected_end_haltestelle = selected_haltestelle
        print(f"Ausgewählte End-Haltestelle: {self.selected_end_haltestelle}")

    def on_search(self, instance, value):
        # Filtern Sie die Optionen basierend auf dem eingegebenen Text
        filtered_options = [option for option in self.options if value.lower() in option.lower()]

        # Aktualisieren Sie die Dropdown-Optionen
        self.dropdown.clear_widgets()
        for option in filtered_options:
            btn = Button(text=option, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_option(btn.text))
            self.dropdown.add_widget(btn)


if __name__ == '__main__':
    SplitScreenApp().run()
