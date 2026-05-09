import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import BaseMiddleware
from collections import defaultdict
import time
from keyboards import cities, ekb_areas, Back_button
from config import TOKEN_API


bot = Bot(token=TOKEN_API)
dp = Dispatcher()


class Form(StatesGroup):
    city = State()
    area = State()
    date = State()

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit=1):
        self.limit = limit
        self.users = defaultdict(float)

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        current_time = time.time()

        if current_time - self.users[user_id] < self.limit:
            return

        self.users[user_id] = current_time

        return await handler(event, data)

dp.message.middleware(AntiSpamMiddleware(limit=1))

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "👋 Привет! Я помогу выбрать досуг\n\nВыбери город:",
        reply_markup=cities
    )

    await state.set_state(Form.city)


@dp.callback_query(Form.city)
async def choose_city(callback: types.CallbackQuery, state: FSMContext):

    if callback.data == "ekb":
        await state.update_data(city="Екатеринбург")

        await callback.message.answer(
            "🏙 Выбери район:",
            reply_markup=ekb_areas
        )

        await state.set_state(Form.area)

    else:
        await callback.message.answer(
            "🚧 Город пока в разработке",
            reply_markup=Back_button
        )

    await callback.answer()

@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.city)
    await callback.message.answer("Выбери город:", reply_markup=cities)
    await callback.answer()

@dp.callback_query(F.data == "Back")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.city)
    await callback.message.answer("Выбери город:", reply_markup=cities)
    await callback.answer()

@dp.callback_query(Form.area)
async def choose_area(callback: types.CallbackQuery, state: FSMContext):

    if callback.data.endswith("_ekb"):
        await state.update_data(area=callback.data)

        await callback.message.answer(
            "📅 Введи дату в формате ДД.ММ.ГГГГ\n"
            "Например: 25.12.2026"
        )

        await state.set_state(Form.date)

    await callback.answer()


@dp.message(Form.date)
async def process_date(message: types.Message, state: FSMContext):

    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")

        data = await state.get_data()

        await state.update_data(date=date.strftime("%d.%m.%Y"))

        await message.answer(
            f"✅ Город: {data.get('city')}\n"
            f"✅ Район: {data.get('area')}\n"
            f"📅 Дата: {date.strftime('%d.%m.%Y')}\n\n"
            f"🔍 Так давай посмотрим что ты можешь посетить"
        )

        await state.clear()

    except ValueError:
        await message.answer(
            "❌ Неверный формат!\n"
            "Пример: 01.01.2026"
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())