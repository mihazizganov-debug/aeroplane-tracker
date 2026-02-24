"""Класс для работы с API OpenStreetMap и OpenSky Network.

Реализует получение географических координат стран и информации о самолетах.
"""

import os
from typing import Any, Dict, List, Optional, cast

import requests
from dotenv import load_dotenv
from requests import Response

from src.api.base_api import BaseAPI

# Загружаем переменные окружения из .env файла
load_dotenv()


class AeroplanesAPI(BaseAPI):
    """Класс для работы с API сервисов отслеживания самолетов.

    Получает координаты страны через nominatim.openstreetmap.org
    и информацию о самолетах через opensky-network.org.
    """

    def __init__(self, timeout: int = 10, user_agent: str = "aeroplane-tracker/1.0") -> None:
        """Инициализация API клиента."""
        super().__init__(base_url="", timeout=timeout)
        self._openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self._opensky_url = "https://opensky-network.org/api/states/all"
        self._aeroplanes: Optional[Dict[str, Any]] = None
        self._user_agent = user_agent

        # Загружаем credentials из .env для OpenSky API (опционально)
        self._username = os.getenv("OPENSKY_USERNAME")
        self._password = os.getenv("OPENSKY_PASSWORD")

    def _connect(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Приватный метод для выполнения HTTP-запроса."""
        try:
            # Для nominatim требуется специальный заголовок User-Agent
            headers = {}
            if "nominatim" in url:
                headers = {"User-Agent": self._user_agent}

            # Добавляем аутентификацию для OpenSky API если есть credentials
            auth = None
            if self._username and self._password and "opensky" in url:
                auth = (self._username, self._password)

            response: Response = requests.get(
                url=url, params=params, headers=headers, auth=auth, timeout=self._timeout
            )

            # Проверяем статус-код ответа
            if response.status_code != 200:
                raise ValueError(f"API вернул ошибку {response.status_code}: {response.text}")

            return response.json()  # type: ignore

        except requests.Timeout:
            raise ConnectionError(f"Превышен таймаут подключения к {url}")
        except requests.ConnectionError:
            raise ConnectionError(f"Ошибка подключения к {url}")
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка при выполнении запроса: {e}")

    def _get_country_coordinates(self, country: str) -> List[str]:
        """Получение географических координат страны."""
        params = {
            "country": country,
            "format": "json",
            "limit": 1,
        }

        data = self._connect(self._openstreetmap_url, params)

        if not data:
            raise ValueError(f"Страна '{country}' не найдена")

        boundingbox = data[0].get("boundingbox")  # type: ignore
        if not boundingbox or len(boundingbox) != 4:
            raise ValueError(f"Некорректные координаты для страны '{country}'")

        return boundingbox  # type: ignore

    def get_data(self, country: str) -> Dict[str, Any]:
        """Получение данных о самолетах в воздушном пространстве страны."""
        # Получаем координаты страны
        boundingbox = self._get_country_coordinates(country)

        # Формируем параметры для OpenSky API
        params = {
            "lamin": boundingbox[0],  # южная широта
            "lamax": boundingbox[1],  # северная широта
            "lomin": boundingbox[2],  # западная долгота
            "lomax": boundingbox[3],  # восточная долгота
        }

        # Запрашиваем данные о самолетах
        self._aeroplanes = self._connect(self._opensky_url, params)
        return self._aeroplanes

    @property
    def aeroplanes(self) -> Optional[Dict[str, Any]]:
        """Геттер для последних полученных данных о самолетах."""
        return self._aeroplanes
