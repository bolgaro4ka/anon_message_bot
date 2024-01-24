
import os
from datetime import datetime
import logging
import asyncio
from aiogram.filters.command import Command
import g4f
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from pathlib import Path
#from aiogram.dispatcher.dispatcher import Dispatcher
#from aiogram.client.bot import Bot
from aiogram import *
with open('db/users.json', encoding='utf-8') as f:
    users = json.load(f)

with open('db/sends.json', encoding='utf-8') as f:
    sends = json.load(f)

bot = Bot(token="YOUR_TOKEN")
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Диспетчер
dp = Dispatcher()


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    print(text)
    return text.split()[1] if len(text.split()) > 1 else None

@dp.message(Command("start"))
async def user_registration(msg: types.Message):
    if not str(msg.from_user.id) in users['users']:
        users['users'][str(msg.from_user.id)] = {"name": msg.from_user.full_name, "username": msg.from_user.username, "msg_by": None}
    if not str(msg.from_user.id) in sends['sends']:
        sends['sends'][str(msg.from_user.id)] = []
    #Выделение id рефера
    unique_code = extract_unique_code(msg.text)
    if unique_code:
        await msg.answer(text="🪪 ID реферала найден в ссылке!")
        users['users'][str(msg.from_user.id)]["msg_by"] = unique_code

    else:
        await msg.answer(text="⚠️ Предупреждение! В вашей пригласительной ссылке нету ID\nℹ️ Введите команду /ref <id>\n\n<id> - id человека которому вы хотите написать, узнать свой id можно через /id")
        users['users'][str(msg.from_user.id)]["msg_by"] = None
    await bot.send_message(msg.from_user.id, f"🎉 Ваша ссылка: https://t.me/anon_msg_bb_bot?start={msg.from_user.id}")


@dp.message(Command("ref"))
async def time(msg: types.Message):
    try:
        users['users'][str(msg.from_user.id)]["msg_by"] = str(msg.text).split(' ')[1]
        await bot.send_message(msg.from_user.id, f"✅ Установлен id получателя {str(msg.text).split(' ')[1]}")
    except IndexError as e: await bot.send_message(msg.from_user.id, f"🛑 Через пробел должен быть указан ID получателя. Например: /ref 12345678")



@dp.message(Command("time"))
async def time(msg: types.Message):
    await bot.send_message(msg.from_user.id, f"⌛ Время: {str(datetime.now())[:]}")


@dp.message(Command("id"))
async def help(msg: types.Message):
    if msg.chat.id:
        await bot.send_message(msg.chat.id, '🪪 Ваш ID: ' + str(msg.chat.id)+'\n🪪 ID Получателя: ' + str(msg.chat.id))
    else: await bot.send_message(msg.from_user.id, '🪪 Ваш ID: '+str(msg.from_user.id))

@dp.message(Command("off"))
async def help(msg: types.Message):
    with open('db/users.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(users, ensure_ascii=False))
    await bot.send_message(msg.from_user.id, f"Завершено!")
    with open('db/sends.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(sends, ensure_ascii=False))
    await bot.send_message(msg.from_user.id, f"Завершено!")

@dp.message(Command("message_to"))
async def time(msg: types.Message):
    if users['users'][str(msg.from_user.id)]:
        print(str(msg.text))
        await bot.send_message(int(str(msg.text).split(' ')[1]), ' '.join(str(msg.text).split(' ')[2:]))
        await bot.send_message(msg.from_user.id, ' '.join(str(msg.text).split(' ')[2:])+" доставлено сообщение "+ str(msg.text).split(' ')[1])
    else: await bot.send_message(msg.from_user.id, f"Отказано в доступе!")

@dp.message()
async def echo(msg: types.Message):
    if users['users'][str(msg.from_user.id)]["msg_by"]:
        await bot.send_message(msg.from_user.id, f"✅ Вы отправили сообщение.\nВаше имя скрыто.")
        await bot.send_message(users['users'][str(msg.from_user.id)]["msg_by"], "📨 Вам доставлено анонимное сообщение с текстом:\n\n "+msg.text)
        sends['sends'][str(msg.from_user.id)].append(msg.text)
    else:
        await bot.send_message(msg.from_user.id, f"🛑 Введите команду /ref <id>\n\n<id> - id человека которому вы хотите написать, узнать свой id можно через /id")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
