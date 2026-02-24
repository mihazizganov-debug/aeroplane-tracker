"""Тесты для класса Aeroplane."""

from typing import Any, Dict, List, Optional

import pytest

from src.models.aeroplane import Aeroplane


class TestAeroplaneInitialization:
    """Тесты инициализации и валидации."""

    def test_create_valid_aeroplane(self) -> None:
        """Тест создания самолета с корректными данными."""
        plane = Aeroplane(
            icao24="abc123",
            callsign="AFL123",
            origin_country="Russia",
            altitude=10000.0,
            speed=250.0,
            longitude=37.5,
            latitude=55.5,
            on_ground=False,
        )

        assert plane.icao24 == "abc123"
        assert plane.callsign == "AFL123"
        assert plane.origin_country == "Russia"
        assert plane.altitude == 10000.0
        assert plane.speed == 250.0
        assert plane.longitude == 37.5
        assert plane.latitude == 55.5
        assert plane.on_ground is False
        assert plane.speed_kmh == 900.0  # 250 * 3.6

    def test_create_with_optional_fields_none(self) -> None:
        """Тест создания с необязательными полями равными None."""
        plane = Aeroplane(icao24="abc123", callsign=None, origin_country="Russia", altitude=None, speed=None)

        assert plane.callsign is None
        assert plane.altitude is None
        assert plane.speed is None
        assert plane.longitude is None
        assert plane.latitude is None
        assert plane.on_ground is False

    def test_validate_icao24_empty(self) -> None:
        """Тест валидации: пустой ICAO24."""
        with pytest.raises(ValueError, match="ICAO24 должен быть непустой строкой"):
            Aeroplane(icao24="", callsign="TEST", origin_country="Test", altitude=10000, speed=200)

    def test_validate_icao24_not_string(self) -> None:
        """Тест валидации: ICAO24 не строка."""
        with pytest.raises(ValueError, match="ICAO24 должен быть непустой строкой"):
            Aeroplane(icao24=12345, callsign="TEST", origin_country="Test", altitude=10000, speed=200)  # type: ignore

    def test_validate_country_empty(self) -> None:
        """Тест валидации: пустая страна."""
        with pytest.raises(ValueError, match="Страна регистрации должна быть непустой строкой"):
            Aeroplane(icao24="abc123", callsign="TEST", origin_country="", altitude=10000, speed=200)

    def test_validate_altitude_out_of_range_low(self) -> None:
        """Тест валидации: высота ниже -1000."""
        with pytest.raises(ValueError, match="Некорректное значение высоты: -2000"):
            Aeroplane(icao24="abc123", callsign="TEST", origin_country="Test", altitude=-2000.0, speed=200)

    def test_validate_altitude_out_of_range_high(self) -> None:
        """Тест валидации: высота выше 20000."""
        with pytest.raises(ValueError, match="Некорректное значение высоты: 25000"):
            Aeroplane(icao24="abc123", callsign="TEST", origin_country="Test", altitude=25000.0, speed=200)

    def test_validate_altitude_not_number(self) -> None:
        """Тест валидации: высота не число."""
        with pytest.raises(ValueError, match="Высота должна быть числом"):
            Aeroplane(
                icao24="abc123", callsign="TEST", origin_country="Test", altitude="high", speed=200  # type: ignore
            )

    def test_validate_speed_negative(self) -> None:
        """Тест валидации: отрицательная скорость."""
        with pytest.raises(ValueError, match="Некорректное значение скорости: -50"):
            Aeroplane(icao24="abc123", callsign="TEST", origin_country="Test", altitude=10000, speed=-50.0)

    def test_validate_speed_too_high(self) -> None:
        """Тест валидации: скорость выше 500 м/с."""
        with pytest.raises(ValueError, match="Некорректное значение скорости: 600"):
            Aeroplane(icao24="abc123", callsign="TEST", origin_country="Test", altitude=10000, speed=600.0)

    def test_validate_callsign_not_string(self) -> None:
        """Тест валидации: позывной не строка."""
        with pytest.raises(ValueError, match="Позывной должен быть строкой или None"):
            Aeroplane(
                icao24="abc123", callsign=12345, origin_country="Test", altitude=10000, speed=200  # type: ignore
            )


class TestAeroplaneComparison:
    """Тесты методов сравнения."""

    @pytest.fixture
    def plane1(self) -> Aeroplane:
        return Aeroplane("icao1", "FLT1", "Russia", 10000, 200)

    @pytest.fixture
    def plane2(self) -> Aeroplane:
        return Aeroplane("icao2", "FLT2", "USA", 12000, 250)

    @pytest.fixture
    def plane3(self) -> Aeroplane:
        return Aeroplane("icao3", "FLT3", "Germany", 8000, 180)

    def test_less_than(self, plane1: Aeroplane, plane2: Aeroplane, plane3: Aeroplane) -> None:
        """Тест оператора <."""
        assert plane1 < plane2  # 10000 < 12000
        assert plane3 < plane1  # 8000 < 10000
        assert not (plane2 < plane1)  # 12000 не < 10000

    def test_greater_than(self, plane1: Aeroplane, plane2: Aeroplane, plane3: Aeroplane) -> None:
        """Тест оператора >."""
        assert plane2 > plane1  # 12000 > 10000
        assert plane1 > plane3  # 10000 > 8000
        assert not (plane1 > plane2)  # 10000 не > 12000

    def test_less_equal(self, plane1: Aeroplane, plane2: Aeroplane) -> None:
        """Тест оператора <=."""
        assert plane1 <= plane2  # 10000 <= 12000
        assert plane1 <= plane1  # равенство
        assert not (plane2 <= plane1)  # 12000 не <= 10000

    def test_greater_equal(self, plane1: Aeroplane, plane2: Aeroplane) -> None:
        """Тест оператора >=."""
        assert plane2 >= plane1  # 12000 >= 10000
        assert plane1 >= plane1  # равенство
        assert not (plane1 >= plane2)  # 10000 не >= 12000

    def test_equality_by_icao24(self) -> None:
        """Тест сравнения на равенство по ICAO24."""
        plane_a = Aeroplane("same123", "FLT1", "Russia", 10000, 200)
        plane_b = Aeroplane("same123", "FLT2", "USA", 12000, 250)
        plane_c = Aeroplane("diff456", "FLT3", "Germany", 8000, 180)

        assert plane_a == plane_b  # одинаковый ICAO24
        assert not (plane_a == plane_c)  # разные ICAO24

    def test_comparison_with_non_aeroplane(self, plane1: Aeroplane) -> None:
        """Тест сравнения с объектом не Aeroplane."""
        assert (plane1 == "not a plane") is False
        assert (plane1 != "not a plane") is True


class TestAeroplaneConversion:
    """Тесты методов преобразования."""

    def test_to_dict(self) -> None:
        """Тест преобразования в словарь."""
        plane = Aeroplane(
            icao24="abc123",
            callsign="AFL123",
            origin_country="Russia",
            altitude=10000.0,
            speed=250.0,
            longitude=37.5,
            latitude=55.5,
            on_ground=False,
        )

        expected = {
            "icao24": "abc123",
            "callsign": "AFL123",
            "origin_country": "Russia",
            "altitude": 10000.0,
            "speed": 250.0,
            "longitude": 37.5,
            "latitude": 55.5,
            "on_ground": False,
        }

        assert plane.to_dict() == expected

    def test_from_dict(self) -> None:
        """Тест создания из словаря."""
        data = {
            "icao24": "abc123",
            "callsign": "AFL123",
            "origin_country": "Russia",
            "altitude": 10000.0,
            "speed": 250.0,
            "longitude": 37.5,
            "latitude": 55.5,
            "on_ground": False,
        }

        plane = Aeroplane.from_dict(data)

        assert plane.icao24 == "abc123"
        assert plane.callsign == "AFL123"
        assert plane.origin_country == "Russia"
        assert plane.altitude == 10000.0
        assert plane.speed == 250.0
        assert plane.longitude == 37.5
        assert plane.latitude == 55.5
        assert plane.on_ground is False

    def test_from_dict_missing_fields(self) -> None:
        """Тест создания из словаря с пропущенными полями."""
        data = {
            "icao24": "abc123",
            "origin_country": "Russia",
        }

        plane = Aeroplane.from_dict(data)

        assert plane.icao24 == "abc123"
        assert plane.callsign is None
        assert plane.origin_country == "Russia"
        assert plane.altitude is None
        assert plane.speed is None
        assert plane.longitude is None
        assert plane.latitude is None
        assert plane.on_ground is False


class TestAeroplaneCastFromAPI:
    """Тесты преобразования из API ответа."""

    def test_cast_to_object_list_valid(self) -> None:
        """Тест преобразования корректных данных."""
        api_response: Dict[str, Any] = {
            "states": [
                [
                    "4b1812",
                    "SWR438A",
                    "Switzerland",
                    None,
                    None,
                    -0.0168,
                    51.0888,
                    4267.2,
                    False,
                    189.7,
                    None,
                    None,
                    None,
                    None,
                    None,
                    False,
                    0,
                ],
                [
                    "abc123",
                    "AFL123",
                    "Russia",
                    None,
                    None,
                    37.5,
                    55.5,
                    10668.0,
                    False,
                    250.5,
                    None,
                    None,
                    None,
                    None,
                    None,
                    False,
                    0,
                ],
            ]
        }

        planes = Aeroplane.cast_to_object_list(api_response)

        assert len(planes) == 2
        assert planes[0].callsign == "SWR438A"
        assert planes[0].origin_country == "Switzerland"
        assert planes[0].altitude == 4267.2
        assert planes[0].speed == 189.7

        assert planes[1].callsign == "AFL123"
        assert planes[1].origin_country == "Russia"
        assert planes[1].altitude == 10668.0
        assert planes[1].speed == 250.5

    def test_cast_to_object_list_with_nulls(self) -> None:
        """Тест преобразования с null значениями."""
        api_response: Dict[str, Any] = {
            "states": [
                [
                    "xyz789",
                    None,
                    "USA",
                    None,
                    None,
                    -75.0,
                    40.0,
                    None,
                    True,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    False,
                    0,
                ],
            ]
        }

        planes = Aeroplane.cast_to_object_list(api_response)

        assert len(planes) == 1
        assert planes[0].callsign is None
        assert planes[0].altitude is None
        assert planes[0].speed is None
        assert planes[0].on_ground is True

    def test_cast_to_object_list_empty_states(self) -> None:
        """Тест преобразования с пустым списком states."""
        api_response: Dict[str, Any] = {"states": []}
        planes = Aeroplane.cast_to_object_list(api_response)
        assert len(planes) == 0

    def test_cast_to_object_list_missing_states_key(self) -> None:
        """Тест преобразования без ключа states."""
        api_response: Dict[str, Any] = {}
        planes = Aeroplane.cast_to_object_list(api_response)
        assert len(planes) == 0

    def test_cast_to_object_list_skips_invalid(self) -> None:
        """Тест пропуска некорректных записей."""
        api_response: Dict[str, Any] = {
            "states": [
                [
                    "valid1",
                    "FLT1",
                    "Country1",
                    None,
                    None,
                    10,
                    20,
                    1000,
                    False,
                    100,
                    None,
                    None,
                    None,
                    None,
                    None,
                    False,
                    0,
                ],
                ["invalid", "FLT2"],  # слишком короткий список
                [
                    "valid2",
                    "FLT3",
                    "Country2",
                    None,
                    None,
                    30,
                    40,
                    2000,
                    False,
                    200,
                    None,
                    None,
                    None,
                    None,
                    None,
                    False,
                    0,
                ],
            ]
        }

        planes = Aeroplane.cast_to_object_list(api_response)
        assert len(planes) == 2  # пропустил invalid


class TestAeroplaneStringRepresentation:
    """Тесты строкового представления."""

    def test_str_with_all_fields(self) -> None:
        """Тест __str__ со всеми полями."""
        plane = Aeroplane("abc123", "AFL123", "Russia", 10000.0, 250.0)
        expected = "AFL123 (Russia): 10000 м, 900 км/ч"
        assert str(plane) == expected

    def test_str_with_missing_fields(self) -> None:
        """Тест __str__ с пропущенными полями."""
        plane = Aeroplane("abc123", None, "Russia", None, None)
        expected = "Unknown (Russia): —, —"
        assert str(plane) == expected

    def test_repr(self) -> None:
        """Тест __repr__."""
        plane = Aeroplane("abc123", "AFL123", "Russia", 10000.0, 250.0)
        expected = "Aeroplane(icao24=abc123, callsign=AFL123)"
        assert repr(plane) == expected
