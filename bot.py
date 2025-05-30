import asyncio
import os

import yt_dlp
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from config import BOT_TOKEN
from database import init_db, set_channel, get_channel

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

init_db()


@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Добавь меня в канал и напиши там любое сообщение, чтобы я запомнил его. Затем скинь мне ссылку на Instagram Reels.")


@dp.message(F.chat.type == ChatType.CHANNEL)
async def register_channel(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0
    set_channel(user_id, chat_id)
    await message.answer(f"Канал {message.chat.title} зарегистрирован! Теперь отправь ссылку на Reels мне в ЛС.")


@dp.message(Command(commands=['setchannel']))
async def manual_set_channel(message: Message):
    args = message.text.strip().split()

    if len(args) != 2:
        await message.answer("Используй: /setchannel <ID_канала>")
        return

    try:
        chat_id = int(args[1])
        user_id = message.from_user.id
        set_channel(user_id, chat_id)
        await message.answer(f"Канал с ID {chat_id} установлен для загрузок.")
    except ValueError:
        await message.answer("ID канала должен быть числом.")


@dp.message(F.text.contains("instagram.com/reels/"))
async def handle_reels(message: Message):
    url = message.text.strip()
    user_id = message.from_user.id

    chat_id = get_channel(user_id)

    if chat_id is None:
        await message.answer("Сначала добавь меня в канал и напиши там любое сообщение.")
        return

    await message.answer("Скачиваю видео...")

    try:
        filename = "video.mp4"
        ydl_opts = {'outtmpl': filename, 'format': 'mp4', }

        loop = asyncio.get_event_loop()

        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        video = FSInputFile(filename)

        await bot.send_video(chat_id, video)
        await message.answer("Видео отправлено в канал!")

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await message.answer(f"Ошибка при скачивании: {str(e)}")


if __name__ == '__main__':
    dp.run_polling(bot)
