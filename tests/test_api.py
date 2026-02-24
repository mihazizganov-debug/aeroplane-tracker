"""Тесты для классов API."""

import pytest
from typing import Any
from unittest.mock import Mock, patch
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError as RequestsConnectionError

from src.api.base_api import BaseAPI
from src.api.aeroplanes_api import AeroplanesAPI


class TestBaseAPI:
    """Тесты абстрактного класса BaseAPI."""

    def test_base_api_cannot_be_instantiated(self) -> None:
        """Тест, что абстрактный класс нельзя инстанцировать."""
        with pytest.raises(TypeError):
            # Создаем конкретную реализацию для теста
            class ConcreteAPI(BaseAPI):
                def _connect(self, endpoint: str, params: Any = None) -> dict:
                    return {}

                def get_data(self, country: str) -> dict:
                    return {}

            # Пытаемся создать экземпляр абстрактного класса
            BaseAPI("https://test.com")  # type: ignore

    def test_base_api_strip_trailing_slash(self) -> None:
        """Тест, что базовый URL обрезает слеш в конце."""
        class TestAPI(BaseAPI):
            def _connect(self, endpoint: str, params: Any = None) -> dict:
                return {}

            def get_data(self, country: str) -> dict:
                return {}

        api = TestAPI("https://test.com/")
        assert api._base_url == "https://test.com"


class TestAeroplanesAPI:
    """Тесты для AeroplanesAPI."""

    @patch("src.api.aeroplanes_api.requests.get")
    def test_get_country_coordinates_success(self, mock_get: Any) -> None:
        """Тест успешного получения координат страны."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"boundingbox": ["41.67", "83.33", "-141.00", "-52.32"]}]
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api._get_country_coordinates("Canada")

        assert result == ["41.67", "83.33", "-141.00", "-52.32"]
        mock_get.assert_called_once()

    @patch("src.api.aeroplanes_api.requests.get")
    def test_get_country_coordinates_not_found(self, mock_get: Any) -> None:
        """Тест: страна не найдена."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        api = AeroplanesAPI()

        with pytest.raises(ValueError, match="Страна 'Atlantis' не найдена"):
            api._get_country_coordinates("Atlantis")

    @patch("src.api.aeroplanes_api.requests.get")
    def test_get_country_coordinates_invalid_boundingbox(self, mock_get: Any) -> None:
        """Тест: некорректный boundingbox."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"boundingbox": ["41.67"]}]
        mock_get.return_value = mock_response

        api = AeroplanesAPI()

        with pytest.raises(ValueError, match="Некорректные координаты для страны 'Canada'"):
            api._get_country_coordinates("Canada")

    @patch("src.api.aeroplanes_api.requests.get")
    def test_connect_success(self, mock_get: Any) -> None:
        """Тест успешного подключения к API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api._connect("https://test.com", params={"key": "value"})

        assert result == {"test": "data"}
        mock_get.assert_called_once_with(
            url="https://test.com", params={"key": "value"}, headers={}, auth=None, timeout=10
        )

    @patch("src.api.aeroplanes_api.requests.get")
    def test_connect_with_nominatim_headers(self, mock_get: Any) -> None:
        """Тест подключения к nominatim с User-Agent."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        api = AeroplanesAPI(user_agent="test-agent/1.0")
        api._connect("https://nominatim.openstreetmap.org/search")

        mock_get.assert_called_once_with(
            url="https://nominatim.openstreetmap.org/search",
            params=None,
            headers={"User-Agent": "test-agent/1.0"},
            auth=None,
            timeout=10,
        )

    @patch("src.api.aeroplanes_api.requests.get")
    def test_connect_with_auth(self, mock_get: Any) -> None:
        """Тест подключения с аутентификацией."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"OPENSKY_USERNAME": "user", "OPENSKY_PASSWORD": "pass"}):
            api = AeroplanesAPI()
            api._connect("https://opensky-network.org/api/states/all")

            mock_get.assert_called_once_with(
                url="https://opensky-network.org/api/states/all",
                params=None,
                headers={},
                auth=("user", "pass"),
                timeout=10,
            )

    @patch("src.api.aeroplanes_api.requests.get")
    def test_connect_error_status(self, mock_get: Any) -> None:
        """Тест ошибки при статусе не 200."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        api = AeroplanesAPI()

        with pytest.raises(ValueError, match="API вернул ошибку 404: Not Found"):
            api._connect("https://test.com")

    @patch("src.api.aeroplanes_api.requests.get")
    def test_connect_timeout(self, mock_get: Any) -> None:
        """Тест таймаута подключения."""
        mock_get.side_effect = Timeout("Connection timed out")
        api = AeroplanesAPI()

        with pytest.raises(ConnectionError) as excinfo:
            api._connect("https://test.com")

        assert "Превышен таймаут подключения к https://test.com" in str(excinfo.value)

    @patch("src.api.aeroplanes_api.requests.get")
    def test_connect_connection_error(self, mock_get: Any) -> None:
        """Тест ошибки подключения."""
        mock_get.side_effect = RequestsConnectionError("Failed to connect")
        api = AeroplanesAPI()

        with pytest.raises(ConnectionError) as excinfo:
            api._connect("https://test.com")

        assert "Ошибка подключения к https://test.com" in str(excinfo.value)

    @patch("src.api.aeroplanes_api.AeroplanesAPI._get_country_coordinates")
    @patch("src.api.aeroplanes_api.AeroplanesAPI._connect")
    def test_get_data_success(self, mock_connect: Any, mock_get_coordinates: Any) -> None:
        """Тест успешного получения данных о самолетах."""
        mock_get_coordinates.return_value = ["50.0", "60.0", "10.0", "20.0"]
        mock_connect.return_value = {"states": [["test", "data"]]}

        api = AeroplanesAPI()
        result = api.get_data("Germany")

        assert result == {"states": [["test", "data"]]}
        mock_get_coordinates.assert_called_once_with("Germany")
        mock_connect.assert_called_once_with(
            api._opensky_url, {"lamin": "50.0", "lamax": "60.0", "lomin": "10.0", "lomax": "20.0"}
        )
        assert api.aeroplanes == {"states": [["test", "data"]]}

    @patch("src.api.aeroplanes_api.AeroplanesAPI._get_country_coordinates")
    def test_get_data_country_not_found(self, mock_get_coordinates: Any) -> None:
        """Тест: страна не найдена."""
        mock_get_coordinates.side_effect = ValueError("Страна 'Unknown' не найдена")

        api = AeroplanesAPI()

        with pytest.raises(ValueError, match="Страна 'Unknown' не найдена"):
            api.get_data("Unknown")

    def test_aeroplanes_property(self) -> None:
        """Тест геттера aeroplanes."""
        api = AeroplanesAPI()
        assert api.aeroplanes is None

        api._aeroplanes = {"test": "data"}
        assert api.aeroplanes == {"test": "data"}
