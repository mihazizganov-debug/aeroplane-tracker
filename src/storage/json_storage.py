"""Класс для работы с JSON-файлами как хранилищем данных."""

import json
import os
from typing import Any, Dict, List, Optional, Tuple, cast

from src.storage.base_storage import BaseStorage


class JSONStorage(BaseStorage):
    """Класс для работы с JSON-файлами.

    Сохраняет данные в формате JSON. Поддерживает добавление,
    получение и удаление записей без дубликатов.
    """

    def __init__(self, filename: str = "data/aeroplanes.json") -> None:
        """Инициализация JSON-хранилища."""
        self._filename = filename
        self._ensure_file_exists()
        self._data = self._load_data()

    def _ensure_file_exists(self) -> None:
        """Проверка существования файла и создание при необходимости."""
        # Создаем папку data, если её нет
        os.makedirs(os.path.dirname(self._filename), exist_ok=True)

        # Создаем файл с пустым списком, если его нет
        if not os.path.exists(self._filename):
            with open(self._filename, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_data(self) -> List[Dict[str, Any]]:
        """Загрузка данных из JSON-файла."""
        try:
            with open(self._filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Явно приводим к нужному типу
                if isinstance(data, list):
                    return cast(List[Dict[str, Any]], data)
                return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self) -> None:
        """Сохранение данных в JSON-файл."""
        with open(self._filename, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def add(self, item: Dict[str, Any]) -> None:
        """Добавление элемента в хранилище.

        Проверяет наличие элемента по ICAO24 и не добавляет дубликаты.
        """
        # Проверяем на дубликат по ICAO24
        for existing in self._data:
            if existing.get("icao24") == item.get("icao24"):
                raise ValueError(f"Самолет с ICAO24 {item.get('icao24')} уже существует")

        self._data.append(item)
        self._save_data()

    def add_many(self, items: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Добавление нескольких элементов."""
        added = 0
        skipped = 0

        for item in items:
            try:
                self.add(item)
                added += 1
            except ValueError:
                skipped += 1

        return added, skipped

    def get(self, **criteria: Any) -> List[Dict[str, Any]]:
        """Получение элементов по критериям."""
        result = self._data

        for key, value in criteria.items():
            if value is not None:
                result = [item for item in result if item.get(key) == value]

        return result

    def get_all(self) -> List[Dict[str, Any]]:
        """Получение всех элементов."""
        return self._data.copy()

    def delete(self, **criteria: Any) -> int:
        """Удаление элементов по критериям."""
        initial_count = len(self._data)

        if not criteria:
            return 0

        self._data = [
            item for item in self._data if not all(item.get(k) == v for k, v in criteria.items() if v is not None)
        ]

        deleted = initial_count - len(self._data)
        if deleted > 0:
            self._save_data()

        return deleted

    def clear(self) -> None:
        """Очистка всего хранилища."""
        self._data = []
        self._save_data()

    def get_by_icao24(self, icao24: str) -> Optional[Dict[str, Any]]:
        """Получение самолета по ICAO24."""
        for item in self._data:
            if item.get("icao24") == icao24:
                return item
        return None

    def get_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Получение самолетов по стране регистрации."""
        return self.get(origin_country=country)

    def __len__(self) -> int:
        """Количество элементов в хранилище."""
        return len(self._data)

    def __str__(self) -> str:
        """Строковое представление."""
        return f"JSONStorage(файл={self._filename}, записей={len(self._data)})"
