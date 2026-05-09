from datetime import date, timedelta

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


# ─── Callback data factories ──────────────────────────────────────────────────

class CityCallback(CallbackData, prefix="city"):
    code: str


class AreaCallback(CallbackData, prefix="area"):
    code: str


class DateCallback(CallbackData, prefix="date"):
    value: str  # "DD.MM.YYYY" or "manual"


class NavCallback(CallbackData, prefix="nav"):
    to: str  # "city" | "area" | "date" | "cancel" | "new"


# ─── Data maps ────────────────────────────────────────────────────────────────

CITY_NAMES: dict[str, str] = {
    "ekb": "Екатеринбург",
    "chlb": "Челябинск",
    "mgn": "Магнитогорск",
    "tmn": "Тюмень",
}

AREA_NAMES: dict[str, str] = {
    "akadem_ekb": "Академический",
    "vis_ekb": "Верх-Иссетский",
    "zhd_ekb": "Железнодорожный",
    "kir_ekb": "Кировский",
    "len_ekb": "Ленинский",
    "oct_ekb": "Октябрьский",
    "oed_ekb": "Орджоникидзевский",
    "chk_ekb": "Чкаловский",
}


# ─── Reply keyboard (persistent main menu) ────────────────────────────────────

def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔍 Найти досуг"),
        KeyboardButton(text="ℹ️ О боте"),
    )
    builder.row(KeyboardButton(text="❓ Помощь"))
    return builder.as_markup(resize_keyboard=True, persistent=True)


# ─── Inline keyboards ─────────────────────────────────────────────────────────

def cities_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, name in CITY_NAMES.items():
        builder.button(text=name, callback_data=CityCallback(code=code))
    builder.adjust(2)
    return builder.as_markup()


def areas_keyboard(city_code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, name in AREA_NAMES.items():
        if code.endswith(f"_{city_code}"):
            builder.button(text=name, callback_data=AreaCallback(code=code))
    # Back button last — with 8 areas adjust(2) gives rows [2,2,2,2,1], back alone
    builder.button(text="◀️ Назад", callback_data=NavCallback(to="city"))
    builder.adjust(2)
    return builder.as_markup()


def _quick_dates(today: date) -> list[tuple[str, date]]:
    result: list[tuple[str, date]] = [
        (f"📅 Сегодня, {today.strftime('%d.%m')}", today),
        (f"📅 Завтра, {(today + timedelta(1)).strftime('%d.%m')}", today + timedelta(1)),
    ]
    days_to_sat = (5 - today.weekday()) % 7 or 7
    sat = today + timedelta(days_to_sat)
    if days_to_sat > 1:
        result.append((f"🗓 Суббота, {sat.strftime('%d.%m')}", sat))

    days_to_sun = (6 - today.weekday()) % 7 or 7
    sun = today + timedelta(days_to_sun)
    if days_to_sun > 1:
        result.append((f"🗓 Воскресенье, {sun.strftime('%d.%m')}", sun))

    return result


def date_keyboard() -> InlineKeyboardMarkup:
    today = date.today()
    quick = _quick_dates(today)

    date_builder = InlineKeyboardBuilder()
    for label, d in quick:
        date_builder.button(
            text=label,
            callback_data=DateCallback(value=d.strftime("%d.%m.%Y")),
        )
    date_builder.adjust(2)

    extra_builder = InlineKeyboardBuilder()
    extra_builder.button(
        text="✏️ Ввести дату вручную",
        callback_data=DateCallback(value="manual"),
    )
    extra_builder.button(text="◀️ Назад", callback_data=NavCallback(to="area"))
    extra_builder.adjust(1)

    date_builder.attach(extra_builder)
    return date_builder.as_markup()


def results_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Новый поиск", callback_data=NavCallback(to="new"))
    builder.button(text="📅 Изменить дату", callback_data=NavCallback(to="date"))
    builder.adjust(1)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data=NavCallback(to="cancel"))
    return builder.as_markup()
