"""Абстрактный класс для работы с внешними API.

Содержит базовую структуру для всех API-клиентов проекта.
Реализует принцип открытости/закрытости (OCP) из SOLID.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAPI(ABC):
    """Абстрактный класс для работы с API сервисами.

    Определяет интерфейс для всех классов, работающих с внешними API.
    Требует реализации методов подключения и получения данных.
    """

    def __init__(self, base_url: str, timeout: int = 10) -> None:
        """Инициализация базового API класса."""
        self._base_url = base_url.rstrip('/')
        self._timeout = timeout

    @abstractmethod
    def _connect(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Приватный метод для подключения к API и выполнения запроса."""
        pass

    @abstractmethod
    def get_data(self, country: str) -> Dict[str, Any]:
        """Получение данных о самолетах по названию страны."""
        pass