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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_lon = None
        self.current_lat = None
        self.current_delta = 0.001

        self.setWindowTitle("API")
        self.resize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.map_area = QLabel("TextLabel")
        main_layout.addWidget(self.map_area)
        self.map_area.setFixedSize(900, 450)



        bottom_layout = QGridLayout()

        self.index_checkbox = QCheckBox("Индекс")
        bottom_layout.addWidget(self.index_checkbox, 0, 0)


        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("")
        main_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Искать")
        bottom_layout.addWidget(self.search_button, 0, 2)
        self.search_button.clicked.connect(self.click)

        self.reset_button = QPushButton("Сброс")
        bottom_layout.addWidget(self.reset_button, 1, 2)

        self.radio_basic = QRadioButton("Базовая")
        self.radio_transport = QRadioButton("Транспорт")
        self.radio_auto = QRadioButton("Автомобильная")
        self.radio_admin = QRadioButton("Административная")

        bottom_layout.addWidget(self.radio_basic, 1, 0)
        bottom_layout.addWidget(self.radio_transport, 1, 1)
        bottom_layout.addWidget(self.radio_auto, 2, 0)
        bottom_layout.addWidget(self.radio_admin, 2, 1)

        self.radio_light = QRadioButton("Светлая")
        self.radio_dark = QRadioButton("Темная")

        bottom_layout.addWidget(self.radio_light, 0, 3)
        bottom_layout.addWidget(self.radio_dark, 1, 3)

        main_layout.addLayout(bottom_layout)

    def click(self):
        query = self.search_input.text()
        if query:
            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
            geocoder_params = {
                "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
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

            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            print(f"Координаты: {toponym_longitude}, {toponym_lattitude}")

            self.current_lon = toponym_longitude
            self.current_lat = toponym_lattitude
            self.update_map()
            return



    def update_map(self):
        if self.current_lon and self.current_lat:
            apikey = "c68b689a-9ae2-43b0-a84c-9e0508fa3f3d"
            map_params = {
                "ll": f"{self.current_lon},{self.current_lat}",
                "spn": f"{self.current_delta},{self.current_delta}",
                "apikey": apikey,
                "size": "650,450"
            }
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
        if key == Qt.Key.Key_Up:
            self.current_delta += 0.001
            self.update_map()
        elif key == Qt.Key.Key_Down:
            self.current_delta -= 0.0001
            self.update_map()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
