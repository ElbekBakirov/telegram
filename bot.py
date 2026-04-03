import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import router as user_router
from admin import router as admin_router
from middlewares import AntiSpamMiddleware, BanCheckMiddleware

# ============================================================
# LOG TIZIMI
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# ASOSIY FUNKSIYA
# ============================================================
async def main():
    """Botni ishga tushirish."""
    
    # Ma'lumotlar bazasini yaratish
    logger.info("📦 Ma'lumotlar bazasi yaratilmoqda...")
    await init_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor!")

    # Bot va Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware'larni ro'yxatdan o'tkazamiz
    dp.message.middleware(AntiSpamMiddleware())
    dp.message.middleware(BanCheckMiddleware())

    # Boshlang'ich sozlamalarni bazaga yozish (agar bo'sh bo'lsa)
    from database import get_setting, set_setting
    from config import ADMIN_IDS, CHANNEL_ID, CHANNEL_USERNAME
    if not await get_setting("admin_id"):
        await set_setting("admin_id", str(ADMIN_IDS[0]))
    if not await get_setting("channel_id"):
        await set_setting("channel_id", CHANNEL_ID)
    if not await get_setting("channel_username"):
        await set_setting("channel_username", CHANNEL_USERNAME)

    # Router'larni ulash
    dp.include_router(admin_router)   # Admin birinchi (ustunlik)
    dp.include_router(user_router)    # Foydalanuvchi

    # Botni ishga tushirish
    bot_info = await bot.get_me()
    logger.info(f"🤖 Bot ishga tushdi: @{bot_info.username}")
    logger.info(f"🆔 Bot ID: {bot_info.id}")
    logger.info("⏳ Xabarlarni kutmoqda...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("🛑 Bot to'xtatildi.")


# ============================================================
# ISHGA TUSHIRISH
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot Ctrl+C bilan to'xtatildi.")
