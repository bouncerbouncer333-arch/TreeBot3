import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database as db
import graphics as gf

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    db.register_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет! 👋 Я бот Семейное Древо.\n\n"
        "📜 Доступные команды для теста:\n"
        "/profile — Твой профиль\n"
        "/marry — Пожениться (ответом на сообщение человека)\n"
        "/divorce — Развестись"
    )

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

    await message.answer(f"👤 Ваш профиль:\nНик: @{message.from_user.username}\nСтатус: {status_text}")

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

    user1 = db.get_user(proposer.id)
    user2 = db.get_user(proposed.id)

    if user1[3] == 'married' or user2[3] == 'married':
        await message.answer("Кто-то из вас уже в браке! Сначала пропишите /divorce.")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="Принять 💍", callback_data=f"marryacc_{proposer.id}_{proposed.id}")
    builder.button(text="Отклонить ❌", callback_data=f"marrydec_{proposer.id}_{proposed.id}")

    await message.answer(
        f"❤️ @{proposer.username} предлагает брак @{proposed.username}!\n"
        f"@{proposed.username}, согласен(сна)?",
        reply_markup=builder.as_markup()
    )

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
    
    # Генерация свидетельства о разводе
    photo_path = gf.generate_certificate("divorced", message.from_user.username, spouse_data[1])
    
    await message.answer_photo(
        photo=types.FSInputFile(photo_path),
        caption=f"💔 @{message.from_user.username} оформил(а) развод с @{spouse_data[1]}."
    )

@dp.callback_query(lambda c: c.data.startswith('marry'))
async def process_callbacks(callback_query: types.CallbackQuery):
    data = callback_query.data.split('_')
    action = data[0]
    p_id, prod_id = int(data[1]), int(data[2])

    if callback_query.from_user.id != prod_id:
        await callback_query.answer("Это предложение не вам!", show_alert=True)
        return

    if action == 'marryacc':
        db.marry_users(p_id, prod_id)
        u1, u2 = db.get_user(p_id)[1], db.get_user(prod_id)[1]
        
        # Генерация свидетельства о браке
        photo_path = gf.generate_certificate("marriage", u1, u2)
        
        await callback_query.message.delete()
        await callback_query.message.answer_photo(
            photo=types.FSInputFile(photo_path),
            caption=f"🎉 Брак заключен между @{u1} и @{u2}!"
        )
    else:
        await callback_query.message.edit_text("💔 Предложение отклонено.")
    await callback_query.answer()

async def main():
    db.init_db()
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
