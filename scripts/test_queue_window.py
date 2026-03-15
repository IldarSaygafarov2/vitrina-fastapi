#!/usr/bin/env python3
"""
Проверка логики окна 9:00–21:00 для очереди объявлений.
Запуск: python scripts/test_queue_window.py

Требует: pip install pytz
"""
from datetime import datetime, timedelta, time

import pytz

TZ = pytz.timezone("Asia/Tashkent")


def adjust_queue_send_time_to_allowed_window(dt: datetime) -> datetime:
    """Копия из tgbot.utils.helpers для изолированного теста."""
    tz = pytz.timezone("Asia/Tashkent")
    if dt.tzinfo is None:
        dt_utc = pytz.utc.localize(dt)
    else:
        dt_utc = dt.astimezone(pytz.utc)
    local = dt_utc.astimezone(tz)
    if local.time() > time(21, 0):
        next_day = local.date() + timedelta(days=1)
        local = tz.localize(datetime.combine(next_day, time(9, 0)))
    elif local.hour < 9:
        local = tz.localize(datetime.combine(local.date(), time(9, 0)))
    return local.astimezone(pytz.utc).replace(tzinfo=None)


def fmt(dt: datetime, tz=pytz.UTC) -> str:
    """Форматирует datetime для вывода."""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    local = dt.astimezone(TZ)
    return f"{local.strftime('%d.%m.%Y %H:%M')} (Тшк) / {dt.strftime('%H:%M')} UTC"


def test_case(name: str, input_dt: datetime, expected_hour_tashkent: int):
    """Тестирует один кейс."""
    result = adjust_queue_send_time_to_allowed_window(input_dt)
    result_local = pytz.utc.localize(result).astimezone(TZ)
    ok = result_local.hour == expected_hour_tashkent
    status = "✓" if ok else "✗"
    print(f"{status} {name}")
    print(f"  Вход:  {fmt(pytz.utc.localize(input_dt))}")
    print(f"  Выход: {fmt(pytz.utc.localize(result))}")
    if not ok:
        print(f"  Ожидалось: {expected_hour_tashkent}:00 (Тшк)")
    print()
    return ok


def main():
    print("=" * 60)
    print("Проверка adjust_queue_send_time_to_allowed_window")
    print("Окно: 9:00–21:00 (Asia/Tashkent)")
    print("=" * 60)

    # Tashkent = UTC+5, поэтому:
    # 9:00 Тшк = 4:00 UTC, 21:00 Тшк = 16:00 UTC
    base_date = datetime.utcnow().date()

    tests = [
        # (название, input UTC, ожидаемый час в Тшк)
        ("Внутри окна (14:30 Тшк)", datetime.combine(base_date, datetime.min.time().replace(hour=9, minute=30)), 14),
        ("Внутри окна (20:00 Тшк)", datetime.combine(base_date, datetime.min.time().replace(hour=15, minute=0)), 20),
        ("Позже 21:00 → 9:00 след. дня", datetime.combine(base_date, datetime.min.time().replace(hour=17, minute=0)), 9),
        ("Ровно 21:00 — остаётся", datetime.combine(base_date, datetime.min.time().replace(hour=16, minute=0)), 21),
        ("Раньше 9:00 → 9:00 того же дня", datetime.combine(base_date, datetime.min.time().replace(hour=2, minute=0)), 9),
        ("Ночь 3:00 Тшк → 9:00", datetime.combine(base_date, datetime.min.time().replace(hour=22, minute=0)), 9),
    ]

    ok_count = 0
    for name, input_dt, expected in tests:
        if test_case(name, input_dt, expected):
            ok_count += 1

    print("-" * 60)
    print(f"Результат: {ok_count}/{len(tests)} тестов пройдено")
    if ok_count < len(tests):
        sys.exit(1)

    # Симуляция: последнее объявление в 20:58, +5 мин = ?
    print("=" * 60)
    print("Симуляция: последнее объявление в 20:58 Тшк, +5 мин")
    print("=" * 60)
    # 20:58 Тшк = 15:58 UTC
    last_send = datetime.combine(base_date, datetime.min.time().replace(hour=15, minute=58))
    plus_5 = last_send + timedelta(minutes=5)
    adjusted = adjust_queue_send_time_to_allowed_window(plus_5)
    adj_local = pytz.utc.localize(adjusted).astimezone(TZ)
    print(f"Было бы без коррекции: {fmt(pytz.utc.localize(plus_5))}")
    print(f"После коррекции:       {fmt(pytz.utc.localize(adjusted))}")
    print(f"→ Перенос на след. день 9:00: {adj_local.hour == 9 and adj_local.minute == 0}")
    print()


if __name__ == "__main__":
    main()
