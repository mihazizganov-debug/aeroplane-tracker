"""Тесты для классов Storage."""

import json
import os
from typing import Any
from unittest.mock import ANY, mock_open, patch

import pytest

from src.storage.base_storage import BaseStorage
from src.storage.json_storage import JSONStorage


class TestBaseStorage:
    """Тесты абстрактного класса BaseStorage."""

    def test_base_storage_cannot_be_instantiated(self) -> None:
        """Тест, что абстрактный класс нельзя инстанцировать."""
        with pytest.raises(TypeError):
            BaseStorage()  # type: ignore


class TestJSONStorage:
    """Тесты для JSONStorage."""

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_init_creates_file_if_not_exists(self, mock_file: Any, mock_exists: Any, mock_makedirs: Any) -> None:
        """Тест создания файла при инициализации, если его нет."""
        mock_exists.return_value = False

        storage = JSONStorage("data/test.json")

        mock_makedirs.assert_called_once_with("data", exist_ok=True)

        mock_file.assert_any_call("data/test.json", 'w', encoding='utf-8')

        mock_file.assert_any_call("data/test.json", 'r', encoding='utf-8')

        assert mock_file.call_count >= 2

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    def test_init_loads_data_from_file(self, mock_file: Any, mock_exists: Any, mock_makedirs: Any) -> None:
        """Тест загрузки данных из существующего файла."""
        mock_exists.return_value = True

        storage = JSONStorage("test.json")

        assert storage._data == []

    def test_add_item_success(self, tmp_path: Any) -> None:
        """Тест успешного добавления элемента."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        item = {"icao24": "abc123", "callsign": "TEST"}
        storage.add(item)

        assert len(storage) == 1
        assert storage.get_by_icao24("abc123") == item

    def test_add_duplicate_item_raises_error(self, tmp_path: Any) -> None:
        """Тест добавления дубликата."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        item = {"icao24": "abc123", "callsign": "TEST"}
        storage.add(item)

        with pytest.raises(ValueError, match="Самолет с ICAO24 abc123 уже существует"):
            storage.add(item)

    def test_add_many_items(self, tmp_path: Any) -> None:
        """Тест добавления нескольких элементов."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        items = [
            {"icao24": "abc123", "callsign": "TEST1"},
            {"icao24": "def456", "callsign": "TEST2"},
            {"icao24": "abc123", "callsign": "TEST3"},  # дубликат
        ]

        added, skipped = storage.add_many(items)

        assert added == 2
        assert skipped == 1
        assert len(storage) == 2

    def test_get_all_items(self, tmp_path: Any) -> None:
        """Тест получения всех элементов."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        items = [
            {"icao24": "abc123", "callsign": "TEST1"},
            {"icao24": "def456", "callsign": "TEST2"},
        ]
        storage.add_many(items)

        all_items = storage.get_all()
        assert len(all_items) == 2
        assert all_items == items

    def test_get_by_criteria(self, tmp_path: Any) -> None:
        """Тест фильтрации по критериям."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        items = [
            {"icao24": "abc123", "origin_country": "Russia", "altitude": 10000},
            {"icao24": "def456", "origin_country": "USA", "altitude": 12000},
            {"icao24": "ghi789", "origin_country": "Russia", "altitude": 8000},
        ]
        storage.add_many(items)

        russian = storage.get(origin_country="Russia")
        assert len(russian) == 2
        assert all(item["origin_country"] == "Russia" for item in russian)

        high_altitude = storage.get(altitude=12000)
        assert len(high_altitude) == 1
        assert high_altitude[0]["icao24"] == "def456"

    def test_get_by_country(self, tmp_path: Any) -> None:
        """Тест получения по стране."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        items = [
            {"icao24": "abc123", "origin_country": "Russia"},
            {"icao24": "def456", "origin_country": "USA"},
        ]
        storage.add_many(items)

        russian = storage.get_by_country("Russia")
        assert len(russian) == 1
        assert russian[0]["icao24"] == "abc123"

    def test_get_by_icao24(self, tmp_path: Any) -> None:
        """Тест получения по ICAO24."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        items = [
            {"icao24": "abc123", "callsign": "TEST1"},
            {"icao24": "def456", "callsign": "TEST2"},
        ]
        storage.add_many(items)

        item = storage.get_by_icao24("abc123")
        assert item is not None
        assert item["callsign"] == "TEST1"

        not_found = storage.get_by_icao24("xxx")
        assert not_found is None

    def test_delete_by_criteria(self, tmp_path: Any) -> None:
        """Тест удаления по критериям."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        items = [
            {"icao24": "abc123", "origin_country": "Russia"},
            {"icao24": "def456", "origin_country": "USA"},
            {"icao24": "ghi789", "origin_country": "Russia"},
        ]
        storage.add_many(items)

        deleted = storage.delete(origin_country="Russia")
        assert deleted == 2
        assert len(storage) == 1
        assert storage.get_by_icao24("def456") is not None

    def test_delete_no_criteria_returns_zero(self, tmp_path: Any) -> None:
        """Тест удаления без критериев."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        items = [{"icao24": "abc123"}]
        storage.add_many(items)

        deleted = storage.delete()  # без критериев
        assert deleted == 0
        assert len(storage) == 1

    def test_clear_storage(self, tmp_path: Any) -> None:
        """Тест очистки хранилища."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        items = [{"icao24": "abc123"}, {"icao24": "def456"}]
        storage.add_many(items)

        storage.clear()
        assert len(storage) == 0

    def test_len_method(self, tmp_path: Any) -> None:
        """Тест метода __len__."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        assert len(storage) == 0

        storage.add({"icao24": "abc123"})
        assert len(storage) == 1

    def test_str_method(self, tmp_path: Any) -> None:
        """Тест строкового представления."""
        test_file = tmp_path / "test.json"
        storage = JSONStorage(str(test_file))

        storage.add({"icao24": "abc123"})
        assert "JSONStorage(файл=" in str(storage)
        assert "записей=1" in str(storage)
