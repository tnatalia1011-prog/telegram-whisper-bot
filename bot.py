import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ContentType
from groq import Groq
from aiohttp import web

# Вставьте ваш токен Telegram и API ключ Groq здесь
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8857753059:AAH53d6sUO3jaBipCD0jez6aCNRNPwHfTGo")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "ВАШ_GROQ_API_KEY")

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(level=logging.INFO)

@dp.message(F.content_type == ContentType.VOICE)
async def handle_voice(message: types.Message):
    status_message = await message.answer("🎙 Обрабатываю ваше сообщение...")
    try:
        voice = message.voice
        file_id = voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        file_name = f"{file_id}.ogg"
        await bot.download_file(file_path, file_name)
        
        with open(file_name, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="text"
            )
        
        os.remove(file_name)
        
        if transcript.strip():
            await message.answer(transcript)
        else:
            await message.answer("Не удалось распознать речь.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке аудио.")
    finally:
        await status_message.delete()

@dp.message(F.content_type == ContentType.AUDIO)
async def handle_audio(message: types.Message):
    status_message = await message.answer("🎵 Обрабатываю аудиофайл...")
    try:
        audio = message.audio
        file_id = audio.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        file_name = f"{file_id}.mp3"
        await bot.download_file(file_path, file_name)
        
        with open(file_name, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="text"
            )
        
        os.remove(file_name)
        
        if transcript.strip():
            await message.answer(transcript)
        else:
            await message.answer("Не удалось распознать речь.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке аудио.")
    finally:
        await status_message.delete()

@dp.message(F.text == "/start")
async def send_welcome(message: types.Message):
    await message.answer("Привет! Пришли мне голосовое сообщение или аудиофайл, и я превращу его в текст.")

# Простая веб-страница для Render, чтобы он не перезагружал бота
async def handle_web(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000)))
    await site.start()

async def main():
    # Запускаем веб-сервер и бота одновременно
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
