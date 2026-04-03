import logging
from aiogram import Bot
from config import ADMIN_IDS
from database import get_setting

# ============================================================
# LOG TIZIMI
# ============================================================
logger = logging.getLogger(__name__)


# ============================================================
# ADMIN TEKSHIRUVI
# ============================================================
async def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish (Bazani tekshiradi)."""
    # 1. Bazadan adminni olamiz
    admin_id_db = await get_setting("admin_id")
    if admin_id_db and str(user_id) == str(admin_id_db):
        return True
        
    # 2. Agar bazada bo'lmasa, .env dan tekshiramiz
    return user_id in ADMIN_IDS


async def notify_admins(bot: Bot, text: str, reply_markup=None):
    """Barcha adminlarga xabar yuborish."""
    admin_id_db = await get_setting("admin_id")
    ids = set(ADMIN_IDS)
    if admin_id_db:
        try:
            ids.add(int(admin_id_db))
        except ValueError:
            pass
        
    for admin_id in ids:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML", reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Admin {admin_id} ga xabar yuborishda xato: {e}")
