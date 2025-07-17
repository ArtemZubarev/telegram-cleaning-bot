import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import os

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Главная клавиатура по твоей схеме
def main_menu():
    keyboard = [
        [InlineKeyboardButton(text="Начать уборку", callback_data="start_cleaning")],
        [InlineKeyboardButton(text="Закончить уборку", callback_data="finish_cleaning")],
        [InlineKeyboardButton(text="Отчет", callback_data="report")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# /start команда
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Добро пожаловать!\nВыберите действие:",
        reply_markup=main_menu()
    )

# Обработка нажатий кнопок
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data

    if data == "start_cleaning":
        await callback.message.edit_text(
            "Вы начали уборку.",
            reply_markup=main_menu()
        )
    elif data == "finish_cleaning":
        await callback.message.edit_text(
            "Вы закончили уборку.",
            reply_markup=main_menu()
        )
    elif data == "report":
        await callback.message.edit_text(
            "Отчет отправлен.",
            reply_markup=main_menu()
        )
    else:
        await callback.message.edit_text(
            "Неизвестная команда.",
            reply_markup=main_menu()
        )

    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
