import asyncio
import os
from aiogram import Bot
from dotenv import load_dotenv

async def clear_webhook():
    """Botni eski webhook'lardan tozalash"""
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    
    if not token:
        print("❌ BOT_TOKEN topilmadi!")
        return
    
    bot = Bot(token=token)
    try:
        # Webhookni to'liq o'chirish
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook muvaffaqiyatli o'chirildi!")
        
        # Bot ma'lumotlarini tekshirish
        me = await bot.get_me()
        print(f"🤖 Bot @{me.username} tayyor!")
        
    except Exception as e:
        print(f"❌ Xato: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(clear_webhook())
