"""Вспомогательные функции для работы с самолетами."""

from typing import List, Dict, Any
from src.models.aeroplane import Aeroplane


def filter_by_country(planes: List[Aeroplane], country: str) -> List[Aeroplane]:
    """Фильтрация самолетов по стране регистрации."""
    return [p for p in planes if country.lower() in p.origin_country.lower()]


def sort_by_altitude(planes: List[Aeroplane], reverse: bool = True) -> List[Aeroplane]:
    """Сортировка самолетов по высоте."""
    return sorted(planes, reverse=reverse)


def get_top_n(planes: List[Aeroplane], n: int) -> List[Aeroplane]:
    """Получение топ N самолетов."""
    return planes[:n]


def format_plane_info(plane: Aeroplane) -> str:
    """Форматирование информации о самолете для вывода."""
    return str(plane)
