from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
import asyncio

# .env fayldan o‘qish
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("❌ BOT_TOKEN yoki CHANNEL_ID .env faylda topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Har bir foydalanuvchining yuborgan postini vaqtinchalik saqlaymiz
user_posts = {}

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer(
        "👋 Salom!\nMenga rasm, video yoki post yuboring.\n"
        "Men uni kanalga joylashdan oldin sizdan tasdiq so‘rayman."
    )

@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_content(msg: types.Message):
    user_id = msg.from_user.id
    user_posts[user_id] = msg

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Kanalga joylash", callback_data="send"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")
    )

    await msg.reply("Postni kanalga joylamoqchimisiz?", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in ["send", "cancel"])
async def process_decision(call: types.CallbackQuery):
    user_id = call.from_user.id
    decision = call.data

    if decision == "send":
        if user_id in user_posts:
            try:
                msg = user_posts[user_id]
                await msg.copy_to(CHANNEL_ID)
                await call.message.answer("✅ Post kanalga yuborildi!")
                del user_posts[user_id]
            except Exception as e:
                await call.message.answer(f"❌ Xatolik: {e}")
        else:
            await call.message.answer("❗ Sizda yuboriladigan post topilmadi.")
    else:
        await call.message.answer("❌ Bekor qilindi.")
        if user_id in user_posts:
            del user_posts[user_id]

    await call.answer()

if __name__ == "__main__":
    print("🤖 Bot ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
