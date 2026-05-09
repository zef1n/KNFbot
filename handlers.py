import logging
from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import (
    AREA_NAMES,
    CITY_NAMES,
    AreaCallback,
    CityCallback,
    DateCallback,
    NavCallback,
    areas_keyboard,
    cancel_keyboard,
    cities_keyboard,
    date_keyboard,
    main_menu,
    results_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


class Form(StatesGroup):
    city = State()
    area = State()
    date = State()
    date_manual = State()
    result = State()


# ─── /start ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "<b>👋 Привет!</b>\n\n"
        "Я помогу найти интересный досуг в твоём городе.\n"
        "Нажми кнопку ниже, чтобы начать 👇",
        reply_markup=main_menu(),
    )


# ─── Reply keyboard buttons ───────────────────────────────────────────────────

@router.message(F.text == "🔍 Найти досуг")
async def search_start(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🌆 <b>Шаг 1 из 3</b> — Выбери город:",
        reply_markup=cities_keyboard(),
    )
    await state.set_state(Form.city)


@router.message(F.text == "ℹ️ О боте")
async def about_handler(message: types.Message) -> None:
    await message.answer(
        "<b>ℹ️ О боте</b>\n\n"
        "Помогаю найти мероприятия и досуг в городах Урала.\n\n"
        "<b>Поддерживаемые города:</b>\n"
        "✅ Екатеринбург\n"
        "🚧 Челябинск <i>(скоро)</i>\n"
        "🚧 Магнитогорск <i>(скоро)</i>\n"
        "🚧 Тюмень <i>(скоро)</i>",
    )


@router.message(F.text == "❓ Помощь")
@router.message(Command("help"))
async def help_handler(message: types.Message) -> None:
    await message.answer(
        "<b>❓ Помощь</b>\n\n"
        "• Нажми <b>🔍 Найти досуг</b> и следуй шагам\n"
        "• Выбери город → район → дату\n"
        "• Получи список мероприятий\n\n"
        "<b>Команды:</b>\n"
        "/start — перезапустить бота\n"
        "/cancel — отменить текущий поиск",
    )


@router.message(Command("cancel"))
async def cancel_command(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Поиск отменён.", reply_markup=main_menu())


# ─── City selection (inline) ──────────────────────────────────────────────────

@router.callback_query(CityCallback.filter(), Form.city)
async def choose_city(
    callback: types.CallbackQuery,
    callback_data: CityCallback,
    state: FSMContext,
) -> None:
    if not callback.message:
        await callback.answer()
        return

    city_code = callback_data.code
    city_name = CITY_NAMES[city_code]

    if city_code != "ekb":
        await callback.answer(f"🚧 {city_name} пока в разработке", show_alert=True)
        return

    await state.update_data(city_code=city_code, city=city_name)
    await callback.message.edit_text(
        f"🌆 Город: <b>{city_name}</b>\n\n"
        "🏙 <b>Шаг 2 из 3</b> — Выбери район:",
        reply_markup=areas_keyboard(city_code),
    )
    await state.set_state(Form.area)
    await callback.answer()


# ─── Area selection (inline) ──────────────────────────────────────────────────

@router.callback_query(AreaCallback.filter(), Form.area)
async def choose_area(
    callback: types.CallbackQuery,
    callback_data: AreaCallback,
    state: FSMContext,
) -> None:
    if not callback.message:
        await callback.answer()
        return

    area_name = AREA_NAMES.get(callback_data.code)
    if not area_name:
        await callback.answer()
        return

    data = await state.get_data()
    city_name = data.get("city", "")

    await state.update_data(area=area_name)
    await callback.message.edit_text(
        f"🌆 Город: <b>{city_name}</b>\n"
        f"🏙 Район: <b>{area_name}</b>\n\n"
        "📅 <b>Шаг 3 из 3</b> — Выбери дату:",
        reply_markup=date_keyboard(),
    )
    await state.set_state(Form.date)
    await callback.answer()


# ─── Date selection (inline quick buttons) ────────────────────────────────────

@router.callback_query(DateCallback.filter(), Form.date)
async def choose_date(
    callback: types.CallbackQuery,
    callback_data: DateCallback,
    state: FSMContext,
) -> None:
    if not callback.message:
        await callback.answer()
        return

    if callback_data.value == "manual":
        await callback.message.edit_text(
            "✏️ Введи дату в формате <code>ДД.ММ.ГГГГ</code>\n"
            "Например: <code>25.12.2026</code>",
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(Form.date_manual)
        await callback.answer()
        return

    await _show_results(callback.message, state, callback_data.value, edit=True)
    await callback.answer()


# ─── Date manual input ────────────────────────────────────────────────────────

@router.message(Form.date_manual)
async def process_manual_date(message: types.Message, state: FSMContext) -> None:
    try:
        d = datetime.strptime(message.text.strip(), "%d.%m.%Y")
    except ValueError:
        await message.answer(
            "❌ Неверный формат!\n"
            "Введи дату как <code>01.01.2026</code>",
            reply_markup=cancel_keyboard(),
        )
        return

    await _show_results(message, state, d.strftime("%d.%m.%Y"), edit=False)


# ─── Navigation callbacks (stateless — work from any state) ──────────────────

@router.callback_query(NavCallback.filter(F.to == "city"))
async def nav_to_city(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        await callback.answer()
        return
    await state.set_state(Form.city)
    await callback.message.edit_text(
        "🌆 <b>Шаг 1 из 3</b> — Выбери город:",
        reply_markup=cities_keyboard(),
    )
    await callback.answer()


@router.callback_query(NavCallback.filter(F.to == "area"))
async def nav_to_area(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        await callback.answer()
        return
    data = await state.get_data()
    city_code = data.get("city_code", "ekb")
    city_name = data.get("city", "")
    await state.set_state(Form.area)
    await callback.message.edit_text(
        f"🌆 Город: <b>{city_name}</b>\n\n"
        "🏙 <b>Шаг 2 из 3</b> — Выбери район:",
        reply_markup=areas_keyboard(city_code),
    )
    await callback.answer()


@router.callback_query(NavCallback.filter(F.to == "date"))
async def nav_to_date(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        await callback.answer()
        return
    data = await state.get_data()
    city_name = data.get("city", "")
    area_name = data.get("area", "")
    await state.set_state(Form.date)
    await callback.message.edit_text(
        f"🌆 Город: <b>{city_name}</b>\n"
        f"🏙 Район: <b>{area_name}</b>\n\n"
        "📅 <b>Шаг 3 из 3</b> — Выбери дату:",
        reply_markup=date_keyboard(),
    )
    await callback.answer()


@router.callback_query(NavCallback.filter(F.to == "cancel"))
async def nav_cancel(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text("❌ Поиск отменён.")
    await callback.answer()


@router.callback_query(NavCallback.filter(F.to == "new"))
async def nav_new_search(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text(
        "🌆 <b>Шаг 1 из 3</b> — Выбери город:",
        reply_markup=cities_keyboard(),
    )
    await state.set_state(Form.city)
    await callback.answer()


# ─── Catch-all: unknown messages outside any state ───────────────────────────

@router.message()
async def unknown_message(message: types.Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        await message.answer("Используй кнопки меню 👇", reply_markup=main_menu())


# ─── Helper ──────────────────────────────────────────────────────────────────

async def _show_results(
    target: types.Message,
    state: FSMContext,
    date_str: str,
    edit: bool,
) -> None:
    data = await state.get_data()
    city = data.get("city", "—")
    area = data.get("area", "—")

    await state.update_data(date=date_str)
    await state.set_state(Form.result)

    text = (
        f"✅ <b>Город:</b> {city}\n"
        f"✅ <b>Район:</b> {area}\n"
        f"📅 <b>Дата:</b> {date_str}\n\n"
        "😔 <b>Мероприятий пока нет.</b>\n"
        "Попробуй другую дату или район."
    )

    # TODO: здесь будет запрос к API/БД с реальными результатами
    if edit:
        await target.edit_text(text, reply_markup=results_keyboard())
    else:
        await target.answer(text, reply_markup=results_keyboard())
