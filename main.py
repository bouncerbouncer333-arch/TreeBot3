import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, WebAppInfo
from aiohttp import web
import database as db
import graphics as gf

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080)) # Railway сам выдает нужный порт через эту переменную

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ДЛЯ MINI APP ---

async def handle_index(request):
    """Отдает HTML страницу с деревом"""
    try:
        with open("templates/tree.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        return web.Response(text=f"Ошибка загрузки шаблона: {e}", status=500)

async def handle_api_family(request):
    """Отдает структуру семьи в формате JSON для JavaScript"""
    user_id = request.query.get("user_id")
    if not user_id:
        return web.json_response({"error": "No user_id provided"}, status=400)
    
    family_data = db.get_family_structure(int(user_id))
    if not family_data:
        return web.json_response({"error": "User not found"}, status=404)
        
    return web.json_response(family_data)

async def start_web_server():
    """Запуск веб-сервера aiohttp"""
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/api/family', handle_api_family)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Веб-сервер Mini App запущен на порту {PORT}")

# --- КОМАНДЫ БОТА ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    db.register_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет! 👋 Я бот Семейное Древо.\n\n"
        "📜 Доступные команды:\n"
        "/profile — Твой статус и дети\n"
        "/tree — Посмотреть интерактивное древо 🌳\n"
        "/marry — Пожениться (ответом)\n"
        "/divorce — Развестись\n"
        "/adopt — Усыновить ребенка (ответом)\n"
        "/abandon — Отказаться от ребенка (ответом)"
    )

@dp.message(Command("tree"))
async def cmd_tree(message: types.Message):
    db.register_user(message.from_user.id, message.from_user.username)
    
    # Ссылка на твое приложение в Railway. Бот сам поймет её, если в Railway настроен Public Domain
    # Если домен не привязан, здесь должна быть точная ссылка на твой Railway-деплой
    app_url = f"https://{request.host}" if 'request' in locals() else "https://" + os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
    
    if not os.getenv("RAILWAY_PUBLIC_DOMAIN"):
        await message.answer("⚠️ Ошибка: На Railway не настроен публичный домен (Networking -> Generate Domain)!")
        return

    builder = InlineKeyboardBuilder()
    # Создаем кнопку Mini App, которая открывает наш сайт прямо внутри TG
    builder.button(
        text="Посмотреть Древо 🌳", 
        web_app=WebAppInfo(url=f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}/")
    )
    
    await message.answer("Нажми на кнопку ниже, чтобы открыть свое интерактивное семейное древо:", reply_markup=builder.as_markup())

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    db.register_user(message.from_user.id, message.from_user.username)
    user_data = db.get_user(message.from_user.id)
    status = user_data[3] 
    
    if status == 'single':
        status_text = "Холост / Не замужем 🕊️"
    elif status == 'married':
        spouse_data = db.get_user(user_data[2])
        spouse_name = f"@{spouse_data[1]}" if spouse_data and spouse_data[1] else "кем-то"
        status_text = f"В браке с {spouse_name} ❤️"
    elif status == 'divorced':
        status_text = "В разводе 💔"
    else:
        status_text = "Неизвестно"

    children = db.get_children(message.from_user.id)
    children_text = "\n"
    if children:
        children_text += "\n👶 Дети:\n" + "\n".join([f"— @{c[1]}" for c in children])
    else:
        children_text += "\n👶 Детей нет"

    await message.answer(f"👤 Ваш профиль:\nНик: @{message.from_user.username}\nСтатус: {status_text}{children_text}")

@dp.message(Command("marry"))
async def cmd_marry(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Ответь этой командой на сообщение человека!")
        return
    proposer = message.from_user
    proposed = message.reply_to_message.from_user
    if proposer.id == proposed.id:
        await message.answer("Нельзя жениться на себе! 😅")
        return
    db.register_user(proposer.id, proposer.username)
    db.register_user(proposed.id, proposed.username)
    user1, user2 = db.get_user(proposer.id), db.get_user(proposed.id)
    if user1[3] == 'married' or user2[3] == 'married':
        await message.answer("Кто-то из вас уже в браке! Сначала пропишите /divorce.")
        return
    parents = [p[0] for p in db.get_parents(proposer.id)]
    children = [c[0] for c in db.get_children(proposer.id)]
    if proposed.id in parents or proposed.id in children:
        await message.answer("Ошибка: Брак с прямыми родственниками запрещен! 🛑")
        return
    builder = InlineKeyboardBuilder()
    builder.button(text="Принять 💍", callback_data=f"marryacc_{proposer.id}_{proposed.id}")
    builder.button(text="Отклонить ❌", callback_data=f"marrydec_{proposer.id}_{proposed.id}")
    await message.answer(f"❤️ @{proposer.username} предлагает брак @{proposed.username}!\n@{proposed.username}, согласен(сна)?", reply_markup=builder.as_markup())

@dp.message(Command("divorce"))
async def cmd_divorce(message: types.Message):
    db.register_user(message.from_user.id, message.from_user.username)
    user_data = db.get_user(message.from_user.id)
    if user_data[3] != 'married':
        await message.answer("Вы не в браке! 🤷‍♂️")
        return
    spouse_id = user_data[2]
    spouse_data = db.get_user(spouse_id)
    db.divorce_users(message.from_user.id, spouse_id)
    photo_path = gf.generate_certificate("divorced", message.from_user.username, spouse_data[1])
    await message.answer_photo(photo=types.FSInputFile(photo_path), caption=f"💔 @{message.from_user.username} оформил(а) развод с @{spouse_data[1]}.")

@dp.message(Command("adopt"))
async def cmd_adopt(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение ребенка!")
        return
    parent, child = message.from_user, message.reply_to_message.from_user
    if parent.id == child.id:
        await message.answer("Нельзя усыновить самого себя! 🤔")
        return
    db.register_user(parent.id, parent.username)
    db.register_user(child.id, child.username)
    if db.get_children_count(parent.id) >= 5:
        await message.answer("У вас уже есть 5 детей! Это максимальный лимит. 🛑")
        return
    user_data = db.get_user(parent.id)
    if user_data[3] == 'married' and user_data[2] == child.id:
        await message.answer("Нельзя усыновить своего
