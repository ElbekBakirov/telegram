import os
from dotenv import load_dotenv

load_dotenv()

# Bot token
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# Admin ID'lari (list)
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

# Majburiy kanal
CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "@kanal")

# "Otziv" guruhi ID
OTZIV_GROUP_ID: str = os.getenv("OTZIV_GROUP_ID", "")

# Ball tizimi
POINTS_PER_REFERRAL: int = int(os.getenv("POINTS_PER_REFERRAL", "50"))
MIN_POINTS_FOR_ORDER: int = int(os.getenv("MIN_POINTS_FOR_ORDER", "100"))

# Database fayli (Railway Volume qo'shish uchun moslangan)
DB_PATH: str = os.getenv("DB_PATH", "bot_database.db")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable topilmadi!")

if not ADMIN_IDS:
    raise ValueError(
        "❌ ADMIN_IDS environment variable topilmadi yoki noto'g'ri format! "
        "Misol: ADMIN_IDS=123456789 yoki ADMIN_IDS=123456789,987654321"
    )

if not CHANNEL_ID:
    raise ValueError(
        "❌ CHANNEL_ID environment variable topilmadi yoki bo'sh! "
        "Misol: CHANNEL_ID=-1001234567890"
    )

if not CHANNEL_USERNAME:
    raise ValueError(
        "❌ CHANNEL_USERNAME environment variable topilmadi yoki bo'sh! "
        "Misol: CHANNEL_USERNAME=@mening_kanalim"
    )
