from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

import environs


@dataclass
class ReminderConfig:
    buy_reminder_days: int
    rent_reminder_days: int

    buy_reminder_minutes: int
    rent_reminder_minutes: int

    use_minutes: bool = False  # для локальной разработки: 5 мин аренда, 10 мин продажа

    # Для теста окна 9–21: симуляция времени "последней отправки" (HH:MM, Тшк)
    # Пример: QUEUE_DEV_SIMULATE_TIME=20:58 — считать что последнее объявление в 20:58
    queue_dev_simulate_time: Optional[str] = None

    @staticmethod
    def from_env(env: environs.Env) -> "ReminderConfig":
        return ReminderConfig(
            rent_reminder_days=env.int("RENT_REMINDER_DAYS"),
            buy_reminder_days=env.int("BUY_REMINDER_DAYS"),
            rent_reminder_minutes=env.int("RENT_REMINDER_MINUTES"),
            buy_reminder_minutes=env.int("BUY_REMINDER_MINUTES"),
            use_minutes=env.bool("REMINDER_USE_MINUTES", False),
            queue_dev_simulate_time=env.str("QUEUE_DEV_SIMULATE_TIME", default="").strip() or None,
        )

    def get_reminder_timedelta(self, operation_type: str) -> timedelta:
        """Возвращает интервал для проверки актуальности (для аренды или продажи)."""
        if self.use_minutes:
            minutes = (
                self.rent_reminder_minutes
                if operation_type == "Аренда"
                else self.buy_reminder_minutes
            )
            return timedelta(minutes=minutes)
        days = (
            self.rent_reminder_days
            if operation_type == "Аренда"
            else self.buy_reminder_days
        )
        return timedelta(days=days)
