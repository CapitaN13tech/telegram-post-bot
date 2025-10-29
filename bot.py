from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_posts = {}

@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer(
        "👋 Salom!\nMenga rasm, video yoki post yuboring.\n"
        "Men uni kanalga joylashdan oldin sizdan tasdiq so‘rayman."
    )

@dp.message(F.content_type.in_({ContentType.PHOTO, ContentType.VIDEO, ContentType.TEXT, ContentType.DOCUMENT}))
async def handle_content(msg: Message):
    user_id = msg.from_user.id
    user_posts[user_id] = msg

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Kanalga joylash", callback_data="send")
    kb.button(text="❌ Bekor qilish", callback_data="cancel")

    await msg.reply("Postni kanalga joylamoqchimisiz?", reply_markup=kb.as_markup())

@dp.callback_query(F.data.in_({"send", "cancel"}))
async def process_decision(call: CallbackQuery):
    user_id = call.from_user.id
    decision = call.data

    if decision == "send":
        msg = user_posts.get(user_id)
        if msg:
            try:
                await msg.copy_to(CHANNEL_ID)
                await call.message.answer("✅ Post kanalga yuborildi!")
                del user_posts[user_id]
            except Exception as e:
                await call.message.answer(f"❌ Xatolik: {e}")
        else:
            await call.message.answer("❗ Sizda yuboriladigan post topilmadi.")
    else:
        await call.message.answer("❌ Bekor qilindi.")
        user_posts.pop(user_id, None)

    await call.answer()

async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
