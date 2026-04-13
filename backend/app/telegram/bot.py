import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = os.getenv("TELEGRAM_WEBAPP_URL")


async def start_handler(message: types.Message) -> None:
    if WEB_APP_URL:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Открыть диагностику",
                        web_app=WebAppInfo(url=WEB_APP_URL),
                    )
                ]
            ],
            resize_keyboard=True,
        )

        await message.answer(
            "Добро пожаловать в MindTrace.\n\n"
            "Нажмите кнопку ниже, чтобы открыть диагностику.",
            reply_markup=keyboard,
        )
        return

    await message.answer(
        "Добро пожаловать в MindTrace.\n\n"
        "Бот уже подключен.\n"
        "Следующий шаг — подключить публичный HTTPS URL для Mini App.",
    )


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
