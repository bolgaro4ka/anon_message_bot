import os
from datetime import datetime
import logging
import asyncio
from aiogram.filters.command import Command
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from aiogram import *
from aiogram.types import InputFile
import aiogram.exceptions
import os
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("TELEGRAM_KEY", "not_so_secret")

with open("db/users.json", encoding="utf-8") as f:
    users = json.load(f)

with open("db/sends.json", encoding="utf-8") as f:
    sends = json.load(f)

bot = Bot(token=SECRET_KEY)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Диспетчер
dp = Dispatcher()
count = 0


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    print(text)
    return text.split()[1] if len(text.split()) > 1 else None


@dp.message(Command("start"))
async def user_registration(msg: types.Message):
    current_chat = msg.chat.id

    if not str(current_chat) in users["users"]:
        users["users"][str(current_chat)] = {
            "name": msg.from_user.full_name if not current_chat != abs(current_chat) else msg.chat.full_name,
            "username": msg.from_user.username if current_chat == abs(current_chat) else [f"Bot Adder: {msg.from_user.username}", f"Chat username: {msg.chat.id}"],
            "msg_by": None,
        }
    if not str(current_chat) in sends["sends"]:
        sends["sends"][str(current_chat)] = []
    # Выделение id рефера
    unique_code = extract_unique_code(msg.text)
    if unique_code:
        await msg.answer(text=f"🪪 ID реферала найден! Это {users['users'][users['users'][str(current_chat)]['msg_by']]['name']}")
        users["users"][str(current_chat)]["msg_by"] = unique_code
    elif users["users"][str(current_chat)]["msg_by"]:
        await msg.answer(text=f"🪪 ID реферала найден! Это {users['users'][users['users'][str(current_chat)]['msg_by']]['name']}")
    else:
        await msg.answer(text="⚠️ Предупреждение! В вашей пригласительной ссылке нету ID\nℹ️ Введите команду /ref <id>\n\n<id> - id человека которому вы хотите написать, узнать свой id можно через /id")
        users["users"][str(current_chat)]["msg_by"] = None
    await bot.send_message(current_chat, f"🎉 Ваша ссылка: https://t.me/anon_msg_bb_bot?start={current_chat}")


@dp.message(Command("ref"))
async def time(msg: types.Message):
    current_chat = msg.chat.id
    try:
        users["users"][str(current_chat)]["msg_by"] = str(msg.text).split(" ")[1]
        await bot.send_message(current_chat, f"✅ Установлен id получателя {str(msg.text).split(' ')[1]}")
    except IndexError as e:
        await bot.send_message(current_chat, f"🛑 Через пробел должен быть указан ID получателя. Например: /ref 12345678")


@dp.message(Command("time"))
async def time(msg: types.Message):
    current_chat = msg.chat.id
    await bot.send_message(current_chat, f"⌛ Время: {str(datetime.now())[:]}")


@dp.message(Command("id"))
async def help(msg: types.Message):
    current_chat = msg.chat.id
    if current_chat != abs(current_chat):
        await bot.send_message(msg.chat.id, "🪪 Ваш ID: " + str(msg.from_user.id) + "\n🪪 ID группы: " + str(msg.chat.id) + "\n🪪 ID Получателя: " + str(users["users"][str(current_chat)]["msg_by"]))
    else:
        await bot.send_message(current_chat, "🪪 Ваш ID: " + str(current_chat) + "\n🪪 ID Получателя: " + str(users["users"][str(current_chat)]["msg_by"]))


@dp.message(Command("off"))
async def help(msg: types.Message):
    current_chat = msg.chat.id
    with open("db/users.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(users, ensure_ascii=False))
    await bot.send_message(current_chat, f"Завершено!")
    with open("db/sends.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(sends, ensure_ascii=False))
    await bot.send_message(current_chat, f"Завершено!")


@dp.message(Command("message_to"))
async def time(msg: types.Message):
    current_chat = msg.chat.id
    if users["users"][str(current_chat)]:
        print(str(msg.text))
        await bot.send_message(int(str(msg.text).split(" ")[1]), " ".join(str(msg.text).split(" ")[2:]))
        await bot.send_message(current_chat, " ".join(str(msg.text).split(" ")[2:]) + " доставлено сообщение " + str(msg.text).split(" ")[1])
    else:
        await bot.send_message(current_chat, f"Отказано в доступе!")


@dp.message(Command("message_to_all"))
async def time(msg: types.Message):
    current_chat = msg.chat.id
    if users["users"][str(current_chat)]:
        print(str(msg.text))
        for ids in users["users"].keys():
            try:
                print(ids)
                await bot.send_message(int(ids), " ".join(str(msg.text).split(" ")[1:]))
                await bot.send_message(current_chat, " ".join(str(msg.text).split(" ")[1:]) + " доставлено сообщение " + ids)
            except:
                continue
    else:
        await bot.send_message(current_chat, f"Отказано в доступе!")


@dp.message()
async def echo(msg: types.Message):
    global count
    current_chat = msg.chat.id
    if msg.content_type == types.ContentType.PHOTO:
        file_id = str(msg.photo[-1].file_id)
        try:
            os.mkdir(f"./db/images/{current_chat}")
        except FileExistsError:
            pass
        file = await bot.get_file(file_id)  # Get file path
        await bot.download_file(file.file_path, f"./db/images/{current_chat}/{str(file_id)[:-20]}.jpg")
        try:
            await bot.send_photo(users["users"][str(current_chat)]["msg_by"], photo=types.FSInputFile(f"./db/images/{current_chat}/{str(file_id)[:-20]}.jpg"), caption="📨 Вам пришло новое анонимное изображение!")
            await bot.send_message(current_chat, f"✅ Вы отправили изображение {users['users'][users['users'][str(current_chat)]['msg_by']]['name']}.\nВаше имя скрыто.")

        except aiogram.exceptions.TelegramForbiddenError:
            await bot.send_message(current_chat, f"❌ Отправка не удалась! Похоже {users['users'][users['users'][str(current_chat)]['msg_by']]['name']} заблокировал бота!")
        finally:
            if not current_chat != abs(current_chat):
                sends["sends"][str(current_chat)].append([f"AnonIMAGE(./db/images/{current_chat}/{str(file_id)[:-20]}.jpg)", str(users["users"][str(current_chat)]["msg_by"])])
            else:
                sends["sends"][str(current_chat)].append([f"AnonIMAGE(./db/images/{current_chat}/{str(file_id)[:-20]}.jpg)", str(msg.from_user.id), msg.chat.full_name])
    elif users["users"][str(current_chat)]["msg_by"]:

        try:
            await bot.send_message(users["users"][str(current_chat)]["msg_by"], "📨 Вам доставлено анонимное сообщение с текстом:\n\n " + msg.text)
            await bot.send_message(current_chat, f"✅ Вы отправили сообщение {users['users'][users['users'][str(current_chat)]['msg_by']]['name']}.\nВаше имя скрыто.")
        except aiogram.exceptions.TelegramForbiddenError:
            await bot.send_message(current_chat, f"❌ Отправка не удалась! Похоже {users['users'][users['users'][str(current_chat)]['msg_by']]['name']} заблокировал бота!")

        except aiogram.exceptions.TelegramBadRequest:
            print("Unk")

        if not current_chat != abs(current_chat):
            sends["sends"][str(current_chat)].append([msg.text, str(users["users"][str(current_chat)]["msg_by"])])
            print("for user")
        else:
            sends["sends"][str(current_chat)].append([msg.text, str(msg.from_user.id), msg.chat.full_name])
            print(f"for group {msg.chat.id}")
    else:
        await bot.send_message(current_chat, f"🛑 Введите команду /ref <id>\n\n<id> - id человека которому вы хотите написать, узнать свой id можно через /id")

    with open("db/users.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(users, ensure_ascii=False))
    print(f'Автосохранение (пользователей): {count}. Тригер: {users["users"][str(current_chat)]["name"]}, {str(current_chat)}')
    with open("db/sends.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(sends, ensure_ascii=False))
    print(f"Автосохранение (сообщений): {count}")
    count += 1


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
