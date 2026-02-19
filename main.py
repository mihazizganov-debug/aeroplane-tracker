#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Точка входа в программу. Демонстрация всех возможностей проекта."""

from src.api.aeroplanes_api import AeroplanesAPI
from src.models.aeroplane import Aeroplane


def print_menu():
    """Вывод меню."""
    print("\n" + "=" * 60)
    print("AEROPLANE TRACKER - МЕНЮ")
    print("=" * 60)
    print("1. Поиск самолетов по стране")
    print("2. Показать топ N самолетов по высоте")
    print("3. Показать самолеты по стране регистрации")
    print("4. Сравнить два самолета")
    print("5. Выход")
    print("-" * 60)


def search_by_country(api):
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
            for i, plane in enumerate(planes[:10], 1):  # Показываем первые 10
                print(f"  {i}. {plane}")
        else:
            print(f"❌ Над {country} нет самолетов в данный момент")

        return planes

    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
        return []


def show_top_by_altitude(planes):
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


def filter_by_origin_country(planes):
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


def compare_two_planes(planes):
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


def user_interaction():
    """Главная функция взаимодействия с пользователем."""
    print("=" * 60)
    print("ДОБРО ПОЖАЛОВАТЬ В AEROPLANE TRACKER")
    print("=" * 60)
    print("\n📋 О проекте:")
    print("  • Получение данных о самолетах через OpenSky API")
    print("  • Поиск по географическим координатам стран (OpenStreetMap)")
    print("  • Класс Aeroplane с валидацией и методами сравнения")
    print("  • Сортировка и фильтрация данных")

    # Создаем экземпляр API
    api = AeroplanesAPI()
    current_planes = []

    while True:
        print_menu()
        choice = input("Ваш выбор (1-5): ")

        if choice == "5":
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

        else:
            print("⚠️ Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    user_interaction()