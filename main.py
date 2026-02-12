import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QSlider, QCheckBox, QRadioButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QButtonGroup
)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("API")
        self.resize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.top_input = QLineEdit()
        self.top_input.setPlaceholderText("Type Here")
        main_layout.addWidget(self.top_input)

        self.map_area = QLabel("TextLabel")
        self.map_area.setStyleSheet("background-color: #e6e6e6; border: 1px solid gray;")
        self.map_area.setMinimumHeight(400)
        self.map_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.map_area)



        bottom_layout = QGridLayout()

        self.index_checkbox = QCheckBox("Индекс")
        bottom_layout.addWidget(self.index_checkbox, 0, 0)

        self.search_input = QLineEdit()
        bottom_layout.addWidget(self.search_input, 0, 1)

        self.search_button = QPushButton("Искать")
        bottom_layout.addWidget(self.search_button, 0, 2)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
