import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список комнат
rooms = [
    "101", "102", "103", "104", 
    "201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212",
    "301", "302", "305", "306", "307", "308", "309", "310", "311", "312", "313",
    "A1", "A2"
]

# Главное меню с комнатами
def rooms_menu():
    keyboard = []
    for room in rooms:
        keyboard.append([InlineKeyboardButton(text=room, callback_data=f"room_{room}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопки после выбора комнаты
def room_actions(room_number):
    keyboard = [
        [InlineKeyboardButton(text="Уборка выполнена", callback_data=f"clean_done_{room_number}")],
        [InlineKeyboardButton(text="В номере неисправность", callback_data=f"problem_{room_number}")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_rooms")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Выбор типа уборки
def cleaning_types(room_number):
    keyboard = [
        [InlineKeyboardButton(text="Текущая", callback_data=f"type_current_{room_number}")],
        [InlineKeyboardButton(text="После выезда", callback_data=f"type_checkout_{room_number}")],
        [InlineKeyboardButton(text="Генеральная", callback_data=f"type_general_{room_number}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопка к списку номеров
def back_to_rooms_button():
    keyboard = [
        [InlineKeyboardButton(text="К номерам", callback_data="back_to_rooms")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Добро пожаловать! Выберите комнату:", reply_markup=rooms_menu())

# Callback обработчик
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    user = callback.from_user

    # Назад к списку комнат
    if data == "back_to_rooms":
        await callback.message.edit_text("Выберите комнату:", reply_markup=rooms_menu())

    # Выбор комнаты
    elif data.startswith("room_"):
        room_number = data.split("_")[1]
        await callback.message.edit_text(f"Комната {room_number}. Выберите действие:", reply_markup=room_actions(room_number))

    # Уборка выполнена → выбор типа
    elif data.startswith("clean_done_"):
        room_number = data.split("_")[2]
        await callback.message.edit_text(f"Выберите тип уборки для комнаты {room_number}:", reply_markup=cleaning_types(room_number))

    # Выбор типа уборки
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

    # В номере неисправность
    elif data.startswith("problem_"):
        room_number = data.split("_")[1]
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        await callback.message.edit_text(
            f"Спасибо!\n\n"
            f"Комната: {room_number}\n"
            f"Сообщено о неисправности.\n"
            f"Время: {time_now}\n"
            f"Пользователь: {user.full_name} (@{user.username})",
            reply_markup=back_to_rooms_button()
        )

    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
