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
        "📜 Доступные команды:\n"
        "/profile — Твой профиль и список детей\n"
        "/marry — Пожениться (ответом на сообщение)\n"
        "/divorce — Развестись\n"
        "/adopt — Усыновить ребенка (ответом на сообщение)\n"
        "/abandon — Отказаться от ребенка (ответом на сообщение)"
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

    user1 = db.get_user(proposer.id)
    user2 = db.get_user(proposed.id)

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
    photo_path = gf.generate_certificate("divorced", message.from_user.username, spouse_data[1])
    await message.answer_photo(photo=types.FSInputFile(photo_path), caption=f"💔 @{message.from_user.username} оформил(а) развод с @{spouse_data[1]}.")

@dp.message(Command("adopt"))
async def cmd_adopt(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение ребенка!")
        return

    parent = message.from_user
    child = message.reply_to_message.from_user

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
        await message.answer("Нельзя усыновить своего супруга(у)! 😅")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="Согласен 👍", callback_data=f"adoptacc_{parent.id}_{child.id}")
    builder.button(text="Не согласен 👎", callback_data=f"adoptdec_{parent.id}_{child.id}")

    await message.answer(
        f"👶 @{parent.username} хочет усыновить/удочерить @{child.username}!\n"
        f"@{child.username}, ты согласен стать частью семьи?",
        reply_markup=builder.as_markup()
    )

@dp.message(Command("abandon"))
async def cmd_abandon(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение ребенка, от которого вы хотите отказаться!")
        return

    parent = message.from_user
    child = message.reply_to_message.from_user

    children_ids = [c[0] for c in db.get_children(parent.id)]
    if child.id not in children_ids:
        await message.answer("Этот пользователь не является вашим ребенком! 🤷‍♂️")
        return

    user_data = db.get_user(parent.id)
    
    if user_data[3] == 'married':
        spouse_id = user_data[2]
        builder = InlineKeyboardBuilder()
        builder.button(text="Согласен ✅", callback_data=f"abacc_{parent.id}_{spouse_id}_{child.id}")
        builder.button(text="Против ❌", callback_data=f"abdec_{parent.id}_{spouse_id}_{child.id}")
        await message.answer(
            f"⚠️ @{parent.username} хочет отказаться от ребенка @{child.username}.\n"
            f"Так как вы в браке, требуется согласие супруга(и). Что скажешь?",
            reply_markup=builder.as_markup()
        )
    else:
        db.remove_child(parent.id, child.id)
        # Чисто текстовый ответ без генерации картинки
        await message.answer(f"📉 Связи разорваны. @{parent.username} официально отказался от родительских прав на @{child.username}.")

@dp.callback_query(lambda c: c.data.startswith('marry') or c.data.startswith('adopt') or c.data.startswith('ab'))
async def process_callbacks(callback_query: types.CallbackQuery):
    data = callback_query.data.split('_')
    action = data[0]

    if action in ['marryacc', 'marrydec']:
        p_id, prod_id = int(data[1]), int(data[2])
        if callback_query.from_user.id != prod_id:
            await callback_query.answer("Это предложение не вам!", show_alert=True)
            return
        if action == 'marryacc':
            db.marry_users(p_id, prod_id)
            u1, u2 = db.get_user(p_id)[1], db.get_user(prod_id)[1]
            photo_path = gf.generate_certificate("marriage", u1, u2)
            await callback_query.message.delete()
            await callback_query.message.answer_photo(photo=types.FSInputFile(photo_path), caption=f"🎉 Брак заключен между @{u1} и @{u2}!")
        else:
            await callback_query.message.edit_text("💔 Предложение отклонено.")

    elif action in ['adoptacc', 'adoptdec']:
        p_id, c_id = int(data[1]), int(data[2])
        if callback_query.from_user.id != c_id:
            await callback_query.answer("Это приглашение не вам!", show_alert=True)
            return
        if action == 'adoptacc':
            db.adopt_child(p_id, c_id)
            parent_data = db.get_user(p_id)
            if parent_data[3] == 'married':
                db.adopt_child(parent_data[2], c_id)
            u1, u2 = parent_data[1], db.get_user(c_id)[1]
            await callback_query.message.delete()
            # Чисто текстовый ответ
            await callback_query.message.answer(f"👶 Официально! @{u2} теперь в семье у @{u1}! 🎉")
        else:
            await callback_query.message.edit_text("❌ Усыновление отклонено.")

    elif action in ['abacc', 'abdec']:
        p_id, s_id, c_id = int(data[1]), int(data[2]), int(data[3])
        if callback_query.from_user.id != s_id:
            await callback_query.answer("Голосовать должен супруг(а)!", show_alert=True)
            return
        if action == 'abacc':
            db.remove_child(p_id, c_id)
            db.remove_child(s_id, c_id)
            u1, u2 = db.get_user(p_id)[1], db.get_user(c_id)[1]
            await callback_query.message.delete()
            # Чисто текстовый ответ
            await callback_query.message.answer(f"📉 По обоюдному согласию родителей, @{u2} был исключен из семьи.")
        else:
            await callback_query.message.edit_text("❌ Второй родитель против. Отказ от ребенка отменен.")
            
    await callback_query.answer()

async def main():
    db.init_db()
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
