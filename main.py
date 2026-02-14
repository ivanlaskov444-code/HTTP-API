import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QSlider, QCheckBox, QRadioButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QButtonGroup
)
from PyQt6.QtCore import Qt
from io import BytesIO
import requests
from PIL import Image
from PyQt6.QtGui import QPixmap, QImage
import json
import math


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_lon = None
        self.current_lat = None
        self.current_delta = 0.001

        self.static_current_lon = None
        self.static_current_lat = None

        self.setWindowTitle("API")
        self.resize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.map_area = QLabel("")
        main_layout.addWidget(self.map_area)
        self.map_area.setFixedSize(900, 450)



        bottom_layout = QGridLayout()

        self.index_checkbox = QCheckBox("Индекс")
        bottom_layout.addWidget(self.index_checkbox, 0, 0)
        self.index_checkbox.toggled.connect(self.index)



        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("")
        main_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Искать")
        bottom_layout.addWidget(self.search_button, 0, 2)
        self.search_button.clicked.connect(self.click)

        self.reset_button = QPushButton("Сброс")
        bottom_layout.addWidget(self.reset_button, 1, 2)
        self.reset_button.clicked.connect(self.click_reset)
        self.show_marker = False

        self.full_coordinates = QLabel("")
        bottom_layout.addWidget(self.full_coordinates, 3, 2)


        self.radio_basic = QRadioButton("Базовая")
        self.radio_transport = QRadioButton("Транспорт")
        self.radio_auto = QRadioButton("Автомобильная")
        self.radio_admin = QRadioButton("Административная")
        self.map_type = "map"
        self.radio_basic.toggled.connect(self.map_view_switch)
        self.radio_transport.toggled.connect(self.map_view_switch)
        self.radio_auto.toggled.connect(self.map_view_switch)
        self.radio_admin.toggled.connect(self.map_view_switch)

        bottom_layout.addWidget(self.radio_basic, 1, 0)
        bottom_layout.addWidget(self.radio_transport, 1, 1)
        bottom_layout.addWidget(self.radio_auto, 2, 0)
        bottom_layout.addWidget(self.radio_admin, 2, 1)

        self.radio_white = QRadioButton("Светлая")
        self.radio_black = QRadioButton("Темная")
        bottom_layout.addWidget(self.radio_white, 0, 3)
        bottom_layout.addWidget(self.radio_black, 1, 3)
        self.theme = "light"
        self.radio_white.toggled.connect(self.black)
        self.radio_black.toggled.connect(self.black)


        main_layout.addLayout(bottom_layout)

    def index(self):
        if not self.index_checkbox.isChecked():
            self.full_coordinates.setText(self.toponym_address)
        else:
            self.full_coordinates.setText(f"{self.toponym_address}, {self.index}")



    def click_reset(self):
        self.search_input.clear()
        self.show_marker = False
        self.map_area.clear()
        self.full_coordinates.setText("")

    def map_view_switch(self):
        if self.radio_basic.isChecked():
            self.map_type = "map"
        elif self.radio_transport.isChecked():
            self.map_type = ""
        elif self.radio_auto.isChecked():
            self.map_type = ""
        elif self.radio_admin.isChecked():
            self.map_type = ""
        self.update_map()

    def black(self):
        if self.radio_white.isChecked():
            self.theme = "light"
        elif self.radio_black.isChecked():
            self.theme = "dark"
        self.update_map()


    def click(self):
        query = self.search_input.text()
        if query:
            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
            geocoder_params = {
                "apikey": "",
                "geocode": query,
                "format": "json"
            }
            response = requests.get(geocoder_api_server, params=geocoder_params)
            print(f"Статус ответа: {response.status_code}")
            print(f"Ответ: {response.text[:200]}")

            if response.status_code != 200:
                print(f"Ошибка: {response.status_code}")
                sys.exit(1)

            json_response = response.json()

            print(f"Ключи в ответе: {list(json_response.keys())}")

            if "error" in json_response:
                print(f"Ошибка API: {json_response['error']}")
                sys.exit(1)

            if "response" not in json_response:
                print(f"Нет ключа 'response' в ответе. Структура ответа: {json_response}")
                sys.exit(1)

            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

            self.toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            self.index = '0000'
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            print(f"Координаты: {toponym_longitude}, {toponym_lattitude}")

            self.current_lon = toponym_longitude
            self.current_lat = toponym_lattitude
            self.static_current_lon = self.current_lon
            self.static_current_lat = self.current_lat
            if self.index_checkbox.isChecked() and self.index:
                full_address = f"{self.toponym_address}, {self.index}"
                self.full_coordinates.setText(full_address)
            else:
                full_address = self.toponym_address
                self.full_coordinates.setText(full_address)
            self.update_map()



    def update_map(self):
        apikey = ""
        map_params = {
            "ll": f"{self.current_lon},{self.current_lat}",
            "spn": f"{self.current_delta},{self.current_delta}",
            "apikey": apikey,
            "size": "650,450",
            "theme": self.theme,
            "l": self.map_type
        }
        if  not self.show_marker:
            map_params["pt"] = f"{self.static_current_lon},{self.static_current_lat},pm2rdm"

        map_api_server = "https://static-maps.yandex.ru/v1"
        response = requests.get(map_api_server, params=map_params)

        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.map_area.setPixmap(pixmap)
            self.map_area.setScaledContents(True)
        else:
            print(f"Ошибка StaticMaps API: {response.status_code}")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Plus:
            self.current_delta -= 0.01
            self.update_map()
        elif key == Qt.Key.Key_Minus:
            self.current_delta += 0.01
            self.update_map()

        elif key == Qt.Key.Key_8:
            self.current_lon = float(self.current_lon) - self.current_delta / 2
            self.update_map()
        elif key == Qt.Key.Key_5:
            self.current_lon = float(self.current_lon) + self.current_delta / 2
            self.update_map()
        elif key == Qt.Key.Key_4:
            self.current_lat = float(self.current_lat) + self.current_delta
            self.update_map()
        elif key == Qt.Key.Key_6:
            self.current_lat = float(self.current_lat) - self.current_delta
            self.update_map()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Получаем координаты клика относительно карты
            pos = event.position()

            # Конвертируем координаты клика в географические координаты
            if self.current_lon and self.current_lat and self.current_delta:
                # Размер карты
                map_width = self.map_area.width()
                map_height = self.map_area.height()

                # Вычисляем диапазон координат
                lon_min = float(self.current_lon) - self.current_delta
                lon_max = float(self.current_lon) + self.current_delta
                lat_min = float(self.current_lat) - self.current_delta
                lat_max = float(self.current_lat) + self.current_delta

                # Переводим пиксели в координаты
                click_lon = lon_min + (pos.x() / map_width) * (lon_max - lon_min)
                click_lat = lat_max - (pos.y() / map_height) * (lat_max - lat_min)

                # Ищем объект по координатам
                self.geocode___(click_lon, click_lat)
        elif event.button() == Qt.MouseButton.RightButton:
            # Получаем координаты клика относительно карты
            pos = event.position()

            # Конвертируем координаты клика в географические координаты
            if self.current_lon and self.current_lat and self.current_delta:
                # Размер карты
                map_width = self.map_area.width()
                map_height = self.map_area.height()

                # Вычисляем диапазон координат
                lon_min = float(self.current_lon) - self.current_delta
                lon_max = float(self.current_lon) + self.current_delta
                lat_min = float(self.current_lat) - self.current_delta
                lat_max = float(self.current_lat) + self.current_delta

                # Переводим пиксели в координаты
                click_lon = lon_min + (pos.x() / map_width) * (lon_max - lon_min)
                click_lat = lat_max - (pos.y() / map_height) * (lat_max - lat_min)
                # Ищем объект по координатам
                self.geocode_____(click_lon, click_lat)


    def geocode___(self, click_lon, click_lat):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "",
            "geocode": f"{click_lon},{click_lat}",
            "format": "json"
        }
        response = requests.get(geocoder_api_server, params=geocoder_params)
        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ: {response.text[:200]}")

        if response.status_code != 200:
            print(f"Ошибка: {response.status_code}")
            sys.exit(1)

        json_response = response.json()

        print(f"Ключи в ответе: {list(json_response.keys())}")

        if "error" in json_response:
            print(f"Ошибка API: {json_response['error']}")
            sys.exit(1)

        if "response" not in json_response:
            print(f"Нет ключа 'response' в ответе. Структура ответа: {json_response}")
            sys.exit(1)

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

        self.toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        self.index = '0001'


        self.static_current_lon = click_lon
        self.static_current_lat = click_lat
        if self.index_checkbox.isChecked() and self.index:
            full_address = f"{self.toponym_address}, {self.index}"
            self.full_coordinates.setText(full_address)
        else:
            full_address = self.toponym_address
            self.full_coordinates.setText(full_address)
        self.update_map()

    def geocode_____(self, click_lon, click_lat):
        api_key = ''
        server_address = "https://search-maps.yandex.ru/v1/"

        params = {
            "apikey": api_key,
            "text": "организация",
            "ll": f"{click_lon},{click_lat}",
            "spn": "0.001,0.001"
        }

        response2 = requests.get(server_address, params=params)

        if response2.status_code == 200:
            json_response2 = response2.json()

            if "features" in json_response2 and len(json_response2["features"]) > 0:
                org = json_response2["features"][0]

                name = org["properties"]["CompanyMetaData"]["name"]

                coords = org["geometry"]["coordinates"]
                org_lon, org_lat = coords[0], coords[1]

                R = 6371000

                lat1_rad = math.radians(lat1)
                lon1_rad = math.radians(lon1)
                lat2_rad = math.radians(lat2)
                lon2_rad = math.radians(lon2)

                dlat = lat2_rad - lat1_rad
                dlon = lon2_rad - lon1_rad

                a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

                distance = R * c

                if distance <= 50:
                    address = org["properties"]["CompanyMetaData"]["address"]

                    self.full_coordinates.setText(f"{name}, {address}")
                else:
                    self.full_coordinates.setText("")


                    self.static_current_lon = org_lon
                    self.static_current_lat = org_lat
                    self.show_marker = True
                    self.update_map()
        else:
            print(response2.status_code)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
