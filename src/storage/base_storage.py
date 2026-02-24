"""Абстрактный класс для работы с хранилищами данных.

Определяет интерфейс для всех классов, работающих с файлами и базами данных.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseStorage(ABC):
    """Абстрактный класс для работы с хранилищами данных.

    Определяет методы для добавления, получения и удаления данных.
    """

    @abstractmethod
    def add(self, item: Dict[str, Any]) -> None:
        """Добавление элемента в хранилище."""
        pass

    @abstractmethod
    def get(self, **criteria: Any) -> List[Dict[str, Any]]:
        """Получение элементов из хранилища по критериям."""
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        """Получение всех элементов из хранилища."""
        pass

    @abstractmethod
    def delete(self, **criteria: Any) -> int:
        """Удаление элементов из хранилища по критериям."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Очистка всего хранилища."""
        pass
