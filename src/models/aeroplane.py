"""Модуль для работы с данными о самолетах.

Содержит класс Aeroplane, представляющий информацию о воздушном судне.
"""

from typing import Any, Dict, List, Optional


class Aeroplane:
    """Класс для представления информации о самолете.

    Использует __slots__ для экономии памяти при работе с большим количеством объектов.

    Attributes:
        _icao24: Уникальный идентификатор борта
        _callsign: Позывной рейса
        _origin_country: Страна регистрации
        _altitude: Высота полета (метры)
        _speed: Скорость полета (м/с)
        _longitude: Долгота
        _latitude: Широта
        _on_ground: Находится ли на земле
    """

    __slots__ = (
        '_icao24', '_callsign', '_origin_country', '_altitude',
        '_speed', '_longitude', '_latitude', '_on_ground'
    )

    def __init__(
        self,
        icao24: str,
        callsign: Optional[str],
        origin_country: str,
        altitude: Optional[float],
        speed: Optional[float],
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        on_ground: bool = False
    ) -> None:
        """Инициализация объекта самолета.

        Args:
            icao24: Уникальный идентификатор борта
            callsign: Позывной рейса
            origin_country: Страна регистрации
            altitude: Высота полета в метрах
            speed: Скорость полета в м/с
            longitude: Долгота
            latitude: Широта
            on_ground: Находится ли на земле

        Raises:
            ValueError: При некорректных значениях параметров
        """
        self._icao24 = self._validate_icao24(icao24)
        self._callsign = self._validate_callsign(callsign)
        self._origin_country = self._validate_country(origin_country)
        self._altitude = self._validate_altitude(altitude)
        self._speed = self._validate_speed(speed)
        self._longitude = longitude  # без валидации
        self._latitude = latitude    # без валидации
        self._on_ground = on_ground

    # ============ Приватные методы валидации ============

    @staticmethod
    def _validate_icao24(icao24: str) -> str:
        """Валидация ICAO24 кода."""
        if not icao24 or not isinstance(icao24, str):
            raise ValueError("ICAO24 должен быть непустой строкой")
        return icao24.strip()

    @staticmethod
    def _validate_callsign(callsign: Optional[str]) -> Optional[str]:
        """Валидация позывного."""
        if callsign is not None and not isinstance(callsign, str):
            raise ValueError("Позывной должен быть строкой или None")
        return callsign.strip() if callsign else None

    @staticmethod
    def _validate_country(country: str) -> str:
        """Валидация страны регистрации."""
        if not country or not isinstance(country, str):
            raise ValueError("Страна регистрации должна быть непустой строкой")
        return country.strip()

    @staticmethod
    def _validate_altitude(altitude: Optional[float]) -> Optional[float]:
        """Валидация высоты полета."""
        if altitude is not None:
            if not isinstance(altitude, (int, float)):
                raise ValueError("Высота должна быть числом")
            if altitude < -1000 or altitude > 20000:
                raise ValueError(f"Некорректное значение высоты: {altitude}")
        return float(altitude) if altitude is not None else None

    @staticmethod
    def _validate_speed(speed: Optional[float]) -> Optional[float]:
        """Валидация скорости полета."""
        if speed is not None:
            if not isinstance(speed, (int, float)):
                raise ValueError("Скорость должна быть числом")
            if speed < 0 or speed > 500:
                raise ValueError(f"Некорректное значение скорости: {speed}")
        return float(speed) if speed is not None else None

    # ============ Методы сравнения (по высоте) ============

    def __lt__(self, other: 'Aeroplane') -> bool:
        """Сравнение меньше (по высоте)."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self._altitude or 0) < (other._altitude or 0)

    def __le__(self, other: 'Aeroplane') -> bool:
        """Сравнение меньше или равно (по высоте)."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self._altitude or 0) <= (other._altitude or 0)

    def __gt__(self, other: 'Aeroplane') -> bool:
        """Сравнение больше (по высоте)."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self._altitude or 0) > (other._altitude or 0)

    def __ge__(self, other: 'Aeroplane') -> bool:
        """Сравнение больше или равно (по высоте)."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self._altitude or 0) >= (other._altitude or 0)

    def __eq__(self, other: object) -> bool:
        """Сравнение на равенство (по ICAO24)."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._icao24 == other._icao24

    # ============ Геттеры ============

    @property
    def icao24(self) -> str:
        """ICAO24 идентификатор."""
        return self._icao24

    @property
    def callsign(self) -> Optional[str]:
        """Позывной."""
        return self._callsign

    @property
    def origin_country(self) -> str:
        """Страна регистрации."""
        return self._origin_country

    @property
    def altitude(self) -> Optional[float]:
        """Высота полета (м)."""
        return self._altitude

    @property
    def speed(self) -> Optional[float]:
        """Скорость полета (м/с)."""
        return self._speed

    @property
    def speed_kmh(self) -> Optional[float]:
        """Скорость полета (км/ч)."""
        return self._speed * 3.6 if self._speed is not None else None

    @property
    def longitude(self) -> Optional[float]:
        """Долгота."""
        return self._longitude

    @property
    def latitude(self) -> Optional[float]:
        """Широта."""
        return self._latitude

    @property
    def on_ground(self) -> bool:
        """Находится ли на земле."""
        return self._on_ground

    # ============ Методы преобразования ============

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь.

        Returns:
            Dict[str, Any]: Словарь с данными самолета
        """
        return {
            'icao24': self._icao24,
            'callsign': self._callsign,
            'origin_country': self._origin_country,
            'altitude': self._altitude,
            'speed': self._speed,
            'longitude': self._longitude,
            'latitude': self._latitude,
            'on_ground': self._on_ground
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Aeroplane':
        """Создание объекта из словаря.

        Args:
            data: Словарь с данными самолета

        Returns:
            Aeroplane: Объект самолета
        """
        return cls(
            icao24=data.get('icao24', ''),
            callsign=data.get('callsign'),
            origin_country=data.get('origin_country', ''),
            altitude=data.get('altitude'),
            speed=data.get('speed'),
            longitude=data.get('longitude'),
            latitude=data.get('latitude'),
            on_ground=data.get('on_ground', False)
        )

    @classmethod
    def cast_to_object_list(cls, data: Dict[str, Any]) -> List['Aeroplane']:
        """Преобразование JSON-ответа от API в список объектов самолетов.

        Args:
            data: Данные от OpenSky API (словарь с ключом 'states')

        Returns:
            List[Aeroplane]: Список объектов самолетов
        """
        aeroplanes = []
        states = data.get('states', [])

        for state in states:
            try:
                aeroplane = cls(
                    icao24=state[0] if len(state) > 0 else '',
                    callsign=state[1].strip() if len(state) > 1 and state[1] else None,
                    origin_country=state[2] if len(state) > 2 and state[2] else 'Unknown',
                    altitude=float(state[7]) if len(state) > 7 and state[7] is not None else None,
                    speed=float(state[9]) if len(state) > 9 and state[9] is not None else None,
                    longitude=float(state[5]) if len(state) > 5 and state[5] is not None else None,
                    latitude=float(state[6]) if len(state) > 6 and state[6] is not None else None,
                    on_ground=bool(state[8]) if len(state) > 8 and state[8] is not None else False
                )
                aeroplanes.append(aeroplane)
            except (ValueError, TypeError, IndexError):
                continue

        return aeroplanes

    def __str__(self) -> str:
        """Строковое представление самолета."""
        callsign = self._callsign or 'Unknown'
        altitude = f"{self._altitude:.0f} м" if self._altitude is not None else "—"
        speed = f"{self.speed_kmh:.0f} км/ч" if self._speed is not None else "—"
        return f"{callsign} ({self._origin_country}): {altitude}, {speed}"

    def __repr__(self) -> str:
        """Представление для отладки."""
        return f"Aeroplane(icao24={self._icao24}, callsign={self._callsign})"