# main.py
from src.api.aeroplanes_api import AeroplanesAPI


def user_interaction():
    """Функция для взаимодействия с пользователем."""
    print("=" * 60)
    print("ДОБРО ПОЖАЛОВАТЬ В AEROPLANE TRACKER")
    print("=" * 60)

    # Создаем экземпляр API
    api = AeroplanesAPI()

    # Ввод страны
    country = input("\nВведите название страны (на английском): ")

    try:
        # Получаем данные
        data = api.get_data(country)
        states = data.get('states', [])

        print(f"\n✅ Найдено самолетов: {len(states)}")

        if states:
            # Показываем первые 5
            print(f"\n📊 Первые 5 самолетов над {country}:")
            for i, state in enumerate(states[:5], 1):
                callsign = state[1].strip() if state[1] else "Неизвестно"
                origin = state[2] if state[2] else "Неизвестно"
                altitude = state[7] if state[7] else 0
                speed = state[9] if state[9] else 0

                print(f"\n  {i}. {callsign}")
                print(f"     Страна регистрации: {origin}")
                print(f"     Высота: {altitude:.0f} м")
                print(f"     Скорость: {speed:.0f} м/с ({speed * 3.6:.0f} км/ч)")
        else:
            print(f"❌ Над {country} нет самолетов в данный момент")

    except Exception as e:
        print(f"⚠️ Ошибка: {e}")


if __name__ == "__main__":
    user_interaction()