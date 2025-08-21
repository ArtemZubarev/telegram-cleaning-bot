import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiohttp import web  # для "фейкового" веб-сервера на Render

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "8080"))  # Render передает порт через переменную PORT

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список номеров
rooms = [
    "101", "102", "103", "104",
    "201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212",
    "301", "302", "305", "306", "307", "308", "309", "310", "311", "312", "313",
    "A1", "A2"
]

# FSM для неисправности
class ProblemForm(StatesGroup):
    description = State()
    location = State()
    photo = State()

# Главное меню (номера + хостел)
def rooms_menu():
    keyboard = []
    for room in rooms:
        keyboard.append([InlineKeyboardButton(text=room, callback_data=f"room_{room}")])
    keyboard.append([InlineKeyboardButton(text="Хостел", callback_data="hostel_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Действия для номера
def room_actions(room_number):
    keyboard = [
        [InlineKeyboardButton(text="Уборка выполнена", callback_data=f"clean_done_{room_number}")],
        [InlineKeyboardButton(text="В номере неисправность", callback_data=f"problem_{room_number}")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_rooms")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Типы уборки для номера
def cleaning_types(room_number):
    keyboard = [
        [InlineKeyboardButton(text="Текущая", callback_data=f"type_current_{room_number}")],
        [InlineKeyboardButton(text="После выезда", callback_data=f"type_checkout_{room_number}")],
        [InlineKeyboardButton(text="Генеральная", callback_data=f"type_general_{room_number}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопка возврата к списку номеров
def back_to_rooms_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="К номерам", callback_data="back_to_rooms")]
    ])

# --- Хостел ---
# Меню хостела
def hostel_menu():
    keyboard = [
        [InlineKeyboardButton(text="1 комната", callback_data="hostel_room1")],
        [InlineKeyboardButton(text="2 комната", callback_data="hostel_room2")],
        [InlineKeyboardButton(text="3 комната", callback_data="hostel_room3")],
        [InlineKeyboardButton(text="4 комната", callback_data="hostel_room4")],
        [InlineKeyboardButton(text="Общая зона", callback_data="hostel_common")],
        [InlineKeyboardButton(text="С/У верхний", callback_data="hostel_wc_top")],
        [InlineKeyboardButton(text="С/У нижний", callback_data="hostel_wc_bottom")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_rooms")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Меню для комнаты хостела
def hostel_room_menu(room_number: int):
    hostel_rooms = {
        1: [f"M{i}" for i in range(1, 9)],
        2: [f"M{i}" for i in range(9, 17)],
        3: [f"M{i}" for i in range(17, 25)],
        4: [f"M{i}" for i in range(25, 29)],
    }
    keyboard = []
    for r in hostel_rooms[room_number]:
        keyboard.append([InlineKeyboardButton(text=r, callback_data=f"hostel_bed_{r}")])
    keyboard.append([InlineKeyboardButton(text="--", callback_data="none")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="hostel_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Действия для кровати/зоны
def hostel_actions(name):
    keyboard = [
        [InlineKeyboardButton(text="Уборка выполнена", callback_data=f"hostel_clean_{name}")],
        [InlineKeyboardButton(text="В номере неисправность", callback_data=f"hostel_problem_{name}")],
        [InlineKeyboardButton(text="Назад", callback_data="hostel_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# После "Уборка выполнена" (в хостеле)
def hostel_clean_menu(name):
    keyboard = [
        [InlineKeyboardButton(text="Смена белья", callback_data=f"hostel_bed_change_{name}")],
        [InlineKeyboardButton(text="Назад", callback_data=f"hostel_bed_{name}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопки мест неисправности (шаг FSM)
def location_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Прихожая", callback_data="loc_hall")],
        [InlineKeyboardButton(text="Комната", callback_data="loc_room")],
        [InlineKeyboardButton(text="Туалет", callback_data="loc_wc")]
    ])

# --- Handlers ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Добро пожаловать! Выберите комнату:", reply_markup=rooms_menu())

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    user = callback.from_user

    # --- ОБЫЧНЫЕ НОМЕРА ---
    if data == "back_to_rooms":
        await state.clear()
        await callback.message.edit_text("Выберите комнату:", reply_markup=rooms_menu())

    elif data.startswith("room_"):
        room_number = data.split("_")[1]
        await state.clear()
        await callback.message.edit_text(f"Комната {room_number}. Выберите действие:", reply_markup=room_actions(room_number))

    elif data.startswith("clean_done_"):
        room_number = data.split("_")[2]
        await callback.message.edit_text(f"Выберите тип уборки для комнаты {room_number}:", reply_markup=cleaning_types(room_number))

    elif data.startswith("type_"):
        parts = data.split("_")
        cleaning_type = parts[1]
        room_number = parts[2]
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        await callback.message.edit_text(
            f"Спасибо!\n\n"
            f"Комната: {room_number}\n"
            f"Тип уборки: {cleaning_type}\n"
            f"Время: {time_now}\n"
            f"Пользователь: {user.full_name} (@{user.username})",
            reply_markup=back_to_rooms_button()
        )

    elif data.startswith("problem_"):
        room_number = data.split("_")[1]
        await state.set_state(ProblemForm.description)
        await state.update_data(room=room_number)
        await callback.message.edit_text(
            f"Комната {room_number}\n\nОпишите неисправность:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data=f"room_{room_number}")]
            ])
        )

    # --- ХОСТЕЛ ---
    elif data == "hostel_menu":
        await state.clear()
        await callback.message.edit_text("Выберите зону хостела:", reply_markup=hostel_menu())

    elif data.startswith("hostel_room"):
        room_number = int(data.replace("hostel_room", ""))
        await callback.message.edit_text(f"Хостел — {room_number} комната:", reply_markup=hostel_room_menu(room_number))

    elif data.startswith("hostel_bed_"):
        bed = data.replace("hostel_bed_", "")
        await callback.message.edit_text(f"Место {bed}. Выберите действие:", reply_markup=hostel_actions(bed))

    elif data.startswith("hostel_clean_"):
        bed = data.replace("hostel_clean_", "")
        await callback.message.edit_text(f"{bed}: выберите действие:", reply_markup=hostel_clean_menu(bed))

    elif data.startswith("hostel_bed_change_"):
        bed = data.replace("hostel_bed_change_", "")
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        await callback.message.edit_text(
            f"Спасибо!\n\n"
            f"Хостел: {bed}\n"
            f"Действие: Смена белья\n"
            f"Время: {time_now}\n"
            f"Пользователь: {user.full_name} (@{user.username})",
            reply_markup=back_to_rooms_button()
        )

    elif data in ["hostel_common", "hostel_wc_top", "hostel_wc_bottom"]:
        mapping = {
            "hostel_common": "Общая зона",
            "hostel_wc_top": "С/У верхний",
            "hostel_wc_bottom": "С/У нижний"
        }
        zone = mapping[data]
        await callback.message.edit_text(f"{zone}. Выберите действие:", reply_markup=hostel_actions(zone))

    elif data.startswith("hostel_problem_"):
        place = data.replace("hostel_problem_", "")
        await state.set_state(ProblemForm.description)
        await state.update_data(room=place)
        await callback.message.edit_text(
            f"{place}\n\nОпишите неисправность:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="hostel_menu")]
            ])
        )

    elif data.startswith("loc_"):
        location = data.split("_")[1]
        await state.update_data(location=location)
        await state.set_state(ProblemForm.photo)
        await callback.message.edit_text("Сделайте фото неисправности или напишите 'Нет'.")

    elif data == "none":
        # кнопка "--" в списке мест — ничего не делаем
        pass

    await callback.answer()

# --- FSM обработчики ---
@dp.message(ProblemForm.description)
async def problem_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ProblemForm.location)
    await message.answer("Укажите место:", reply_markup=location_keyboard())

@dp.message(ProblemForm.photo, F.photo | F.text)
async def problem_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = message.from_user
    room_number = data["room"]
    description = data["description"]
    location = data.get("location")
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if message.photo:
        file_id = message.photo[-1].file_id
        photo_info = f"Фото file_id: {file_id}"
    else:
        photo_info = message.text

    # тут можно вызвать запись в Google Sheets
    # append_to_google_sheets(room_number, description, location, photo_info, time_now, user.full_name, user.username)

    await message.answer(
        f"Спасибо! Данные зафиксированы ✅\n\n"
        f"Объект: {room_number}\n"
        f"Описание: {description}\n"
        f"Место: {location}\n"
        f"Фото/текст: {photo_info}\n"
        f"Время: {time_now}\n"
        f"Пользователь: {user.full_name} (@{user.username})",
        reply_markup=back_to_rooms_button()
    )

    await state.clear()

# --- Фейковый HTTP-сервер для Render ---
async def _health(_):
    return web.Response(text="ok")

async def _root(_):
    return web.Response(text="Bot is running")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", _root)
    app.router.add_get("/health", _health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"✅ Web server running on port {PORT}")

# --- RUN ---
async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        start_webserver()
    )

if __name__ == "__main__":
    asyncio.run(main())
