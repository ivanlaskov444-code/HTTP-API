import sys
from io import BytesIO
import requests
from PIL import Image

toponyms_to_find = [
    "Воронеж",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Красноярск",
    "Челябинск",
    "Самара",
    "Ростов-на-Дону"
]
for city in toponyms_to_find:
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
        "geocode": city,
        "format": "json"
    }

    response = requests.get(geocoder_api_server, params=geocoder_params)
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ: {response.text[:200]}")  # Печатаем первые 200 символов ответа

    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}")
        sys.exit(1)

    json_response = response.json()

    # Проверяем структуру ответа
    print(f"Ключи в ответе: {list(json_response.keys())}")

    # Если есть ошибка
    if "error" in json_response:
        print(f"Ошибка API: {json_response['error']}")
        sys.exit(1)

    # Проверяем наличие response
    if "response" not in json_response:
        print(f"Нет ключа 'response' в ответе. Структура ответа: {json_response}")
        sys.exit(1)

    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    print(f"Координаты: {toponym_longitude}, {toponym_lattitude}")

    # Получаем размеры города (bounding box)
    envelope = toponym["boundedBy"]["Envelope"]
    lower_corner = envelope["lowerCorner"].split(" ")
    upper_corner = envelope["upperCorner"].split(" ")

    # Вычисляем размеры города
    lon1, lat1 = float(lower_corner[0]), float(lower_corner[1])
    lon2, lat2 = float(upper_corner[0]), float(upper_corner[1])

    # Вычисляем общий размер города
    city_width = abs(lon2 - lon1)
    city_height = abs(lat2 - lat1)


    delta_lon = city_width / 20
    delta_lat = city_height / 20

    delta = "0.05"
    apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": f"{delta_lon},{delta_lat}",
        "apikey": apikey,
        "size": "650,450"
    }

    map_api_server = "https://static-maps.yandex.ru/v1"
    response = requests.get(map_api_server, params=map_params)

    if response.status_code == 200:
        im = BytesIO(response.content)
        opened_image = Image.open(im)
        opened_image.show()
    else:
        print(f"Ошибка StaticMaps API: {response.status_code}")