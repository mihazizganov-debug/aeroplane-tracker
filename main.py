#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Точка входа в программу. Демонстрация всех возможностей проекта."""

from typing import Any, Dict, List

from src.api.aeroplanes_api import AeroplanesAPI
from src.models.aeroplane import Aeroplane
from src.storage.json_storage import JSONStorage


def print_menu() -> None:
    """Вывод меню."""
    print("\n" + "=" * 60)
    print("AEROPLANE TRACKER - МЕНЮ")
    print("=" * 60)
    print("1. Поиск самолетов по стране")
    print("2. Показать топ N самолетов по высоте")
    print("3. Показать самолеты по стране регистрации")
    print("4. Сравнить два самолета")
    print("5. Сохранить текущие самолеты в файл")
    print("6. Загрузить самолеты из файла")
    print("7. Показать сохраненные самолеты")
    print("8. Очистить файл")
    print("9. Выход")
    print("-" * 60)


def search_by_country(api: Any) -> List:
    """Поиск самолетов по стране."""
    country = input("\nВведите название страны (на английском): ")

    try:
        # Получаем данные через API
        data = api.get_data(country)

        # Преобразуем в список объектов Aeroplane
        planes = Aeroplane.cast_to_object_list(data)

        print(f"\n✅ Найдено самолетов: {len(planes)}")

        if planes:
            print(f"\n📊 Самолеты над {country}:")
            for i, plane in enumerate(planes[:10], 1):
                print(f"  {i}. {plane}")
        else:
            print(f"❌ Над {country} нет самолетов в данный момент")

        return planes

    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
        return []


def show_top_by_altitude(planes: List) -> None:
    """Показать топ N самолетов по высоте."""
    if not planes:
        print("\n⚠️ Сначала выполните поиск самолетов (пункт 1)")
        return

    try:
        n = int(input("\nВведите количество самолетов для вывода в топ: "))

        # Сортируем по высоте (от большей к меньшей)
        sorted_planes = sorted(planes, reverse=True)

        print(f"\n📊 ТОП-{min(n, len(sorted_planes))} самолетов по высоте:")
        for i, plane in enumerate(sorted_planes[:n], 1):
            print(f"  {i}. {plane}")

    except ValueError:
        print("⚠️ Введите корректное число")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")


def filter_by_origin_country(planes: List) -> None:
    """Фильтр самолетов по стране регистрации."""
    if not planes:
        print("\n⚠️ Сначала выполните поиск самолетов (пункт 1)")
        return

    country = input("\nВведите страну регистрации для фильтрации: ")

    filtered = [p for p in planes if country.lower() in p.origin_country.lower()]

    print(f"\n✅ Найдено самолетов из {country}: {len(filtered)}")
    if filtered:
        for i, plane in enumerate(filtered[:10], 1):
            print(f"  {i}. {plane}")


def compare_two_planes(planes: List) -> None:
    """Сравнение двух самолетов."""
    if not planes:
        print("\n⚠️ Сначала выполните поиск самолетов (пункт 1)")
        return

    if len(planes) < 2:
        print("\n⚠️ Нужно минимум 2 самолета для сравнения")
        return

    try:
        print("\nДоступные самолеты:")
        for i, plane in enumerate(planes[:10], 1):
            print(f"  {i}. {plane.callsign or 'Unknown'} ({plane.origin_country})")

        idx1 = int(input("\nВыберите номер первого самолета: ")) - 1
        idx2 = int(input("Выберите номер второго самолета: ")) - 1

        if idx1 < 0 or idx2 < 0 or idx1 >= len(planes) or idx2 >= len(planes):
            print("⚠️ Неверный номер")
            return

        p1 = planes[idx1]
        p2 = planes[idx2]

        print("\n" + "-" * 40)
        print("СРАВНЕНИЕ САМОЛЕТОВ:")
        print(f"1. {p1}")
        print(f"2. {p2}")
        print("-" * 40)

        # Сравнение по высоте
        if p1 > p2:
            print(f"✅ {p1.callsign or 'Первый'} летит ВЫШЕ")
        elif p1 < p2:
            print(f"✅ {p2.callsign or 'Второй'} летит ВЫШЕ")
        else:
            print("✅ Самолеты на одной высоте")

        # Сравнение по скорости
        if (p1.speed or 0) > (p2.speed or 0):
            print(f"⚡ {p1.callsign or 'Первый'} БЫСТРЕЕ")
        elif (p1.speed or 0) < (p2.speed or 0):
            print(f"⚡ {p2.callsign or 'Второй'} БЫСТРЕЕ")
        else:
            print("⚡ Скорость одинаковая")

    except ValueError:
        print("⚠️ Введите корректное число")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")


def save_to_file(planes: List) -> None:
    """Сохранение текущих самолетов в JSON-файл."""
    if not planes:
        print("\n⚠️ Нет самолетов для сохранения")
        return

    storage = JSONStorage("data/aeroplanes.json")

    # Преобразуем объекты Aeroplane в словари
    planes_dict = [plane.to_dict() for plane in planes]

    added, skipped = storage.add_many(planes_dict)

    print("\n💾 Результат сохранения:")  # ← ИСПРАВЛЕНО!
    print(f"   ✅ Добавлено: {added}")
    print(f"   ⏭️  Пропущено (дубликаты): {skipped}")
    print(f"   📊 Всего в файле: {len(storage)}")


def load_from_file() -> list:
    """Загрузка самолетов из JSON-файла."""
    storage = JSONStorage("data/aeroplanes.json")

    planes_dict = storage.get_all()

    if not planes_dict:
        print("\n📂 Файл пуст")
        return []

    # Преобразуем словари в объекты Aeroplane
    planes = []
    for p_dict in planes_dict:
        try:
            plane = Aeroplane(
                icao24=p_dict.get("icao24", ""),
                callsign=p_dict.get("callsign"),
                origin_country=p_dict.get("origin_country", ""),
                altitude=p_dict.get("altitude"),
                speed=p_dict.get("speed"),
                longitude=p_dict.get("longitude"),
                latitude=p_dict.get("latitude"),
                on_ground=p_dict.get("on_ground", False),
            )
            planes.append(plane)
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке самолета {p_dict.get('icao24')}: {e}")

    print(f"\n📂 Загружено самолетов: {len(planes)}")
    return planes


def show_saved_planes() -> None:
    """Показать сохраненные самолеты."""
    storage = JSONStorage("data/aeroplanes.json")
    planes_dict = storage.get_all()

    if not planes_dict:
        print("\n📂 Файл пуст")
        return

    print(f"\n📂 СОХРАНЕННЫЕ САМОЛЕТЫ (всего: {len(planes_dict)}):")

    # Группировка по странам
    by_country: Dict = {}
    for p in planes_dict:
        country = p.get("origin_country", "Unknown")
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(p)

    for country, planes_list in sorted(by_country.items()):
        print(f"\n  🌍 {country}: {len(planes_list)}")
        for i, p in enumerate(planes_list[:5], 1):
            callsign = p.get("callsign", "Unknown")
            altitude = p.get("altitude", "—")
            speed = p.get("speed", "—")
            if altitude != "—":
                altitude = f"{altitude:.0f} м"
            if speed != "—":
                speed = f"{speed * 3.6:.0f} км/ч"
            print(f"     {i}. {callsign}: {altitude}, {speed}")


def clear_file() -> None:
    """Очистка файла."""
    storage = JSONStorage("data/aeroplanes.json")
    count = len(storage)
    storage.clear()
    print(f"\n🗑️  Файл очищен. Удалено записей: {count}")


def user_interaction() -> None:
    """Главная функция взаимодействия с пользователем."""
    print("=" * 60)
    print("ДОБРО ПОЖАЛОВАТЬ В AEROPLANE TRACKER")
    print("=" * 60)
    print("\n📋 О проекте:")
    print("  • Получение данных о самолетах через OpenSky API")
    print("  • Поиск по географическим координатам стран (OpenStreetMap)")
    print("  • Класс Aeroplane с валидацией и методами сравнения")
    print("  • Сортировка и фильтрация данных")
    print("  • Сохранение и загрузка данных в JSON")

    # Создаем экземпляр API
    api = AeroplanesAPI()
    current_planes = []

    while True:
        print_menu()
        choice = input("Ваш выбор (1-9): ")

        if choice == "9":
            print("\n👋 До свидания!")
            break

        elif choice == "1":
            current_planes = search_by_country(api)

        elif choice == "2":
            show_top_by_altitude(current_planes)

        elif choice == "3":
            filter_by_origin_country(current_planes)

        elif choice == "4":
            compare_two_planes(current_planes)

        elif choice == "5":
            save_to_file(current_planes)

        elif choice == "6":
            current_planes = load_from_file()

        elif choice == "7":
            show_saved_planes()

        elif choice == "8":
            clear_file()

        else:
            print("⚠️ Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    user_interaction()
