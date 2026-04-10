# ============================================================
# 📝 CONSTANTS - Textlarni saqlash (Free Fire uchun)
# ============================================================

# ============================================================
# MENYU TUGMALARI
# ============================================================
BTN_PROFILE = "👤 Profil"
BTN_EARN_POINTS = "🎯 Ball yig'ish"
BTN_ORDER_POINTS = "� Olmos olish (Ball orqali)"
BTN_BUY_DIAMONDS = "💎 Olmos sotib olish"
BTN_MY_ORDERS = "📦 Buyurtmalarim"
BTN_HELP = "🆘 Yordam"
BTN_CANCEL = "❌ Bekor qilish"
BTN_BACK_TO_MAIN = "🔙 Asosiy menyu"

# ============================================================
# ADMIN MENYU TUGMALARI
# ============================================================
BTN_ADMIN_STATS = "📊 Statistika"
BTN_ADMIN_USERS = "👥 Foydalanuvchilar"
BTN_ADMIN_CARDS = "💳 Kartalar"
BTN_ADMIN_ORDERS = "📋 Yangi so'rovlar"
BTN_ADMIN_BROADCAST = "📢 Xabar yuborish"
BTN_ADMIN_SETTINGS = "⚙️ Sozlamalar"
BTN_ADMIN_BACK = "🔙 Admin menyu"
BTN_ADMIN_MIGRATE = "🔑 Adminni ko'chirish"
BTN_ADMIN_BACK_TO_MENU = "🔙 Oddiy menyu"

# ============================================================
# XABARLAR
# ============================================================
MSG_WELCOME = (
    "🔥 <b>Xush kelibsiz, {full_name}!</b>\n\n"
    "🎮 Bu bot orqali siz <b>Free Fire</b> o'yini uchun\n"
    "bepul olmos (diamonds) olishingiz yoki sotib olishingiz mumkin!\n\n"
    "📌 <b>Asosiy qoidalar:</b>\n"
    "1️⃣ Do'stlaringizni taklif qiling — ball yig'ing\n"
    "2️⃣ Yig'ilgan ballarni olmosga almashtiring\n"
    "3️⃣ Yoki karta orqali arzon narxda sotib oling!"
)

MSG_SUBSCRIBE_REQUIRED = (
    "⚠️ <b>Kanalga a'zo bo'ling!</b>\n\n"
    "Davom etish uchun {channel_user} kanaliga a'zo bo'lishingiz shart."
)

MSG_ORDER_CONFIRM = (
    "✅ <b>Olmos so'rovi #{order_id} qabul qilindi!</b>\n\n"
    "Tez orada admin ko'rib chiqadi va olmoslarni yuboradi."
)

MSG_ORDER_REJECTED = (
    "❌ <b>Olmos so'rovingiz rad etildi.</b>\n\n"
    "📋 So'rov #{order_id}\n"
    "📝 Sabab: {reason}\n\n"
    "💎 {points} ball hisobingizga qaytarildi."
)

MSG_CANCELLED = "❌ Amaliyot bekor qilindi."

MSG_BANNED = (
    "🚫 <b>Siz bloklandingiz!</b>\n\n"
    "Qoidalarni buzganingiz uchun botdan foydalanish huquqingiz cheklangan."
)

# ============================================================
# XATOLIK XABARLARI
# ============================================================
ERR_NOT_ENOUGH_POINTS = "❌ Sizda yetarli ball yo'q!"
ERR_ORDER_NOT_FOUND = "❌ Buyurtma topilmadi!"
ERR_USER_NOT_FOUND = "❌ Foydalanuvchi topilmadi!"
ERR_INVALID_FF_ID = "❌ Noto'g'ri FF ID!"
ERR_SUBSCRIPTION_FAILED = "❌ Kanalga a'zo bo'lishda xatolik!"

# ============================================================
# ADMIN XABARLARI
# ============================================================
ADMIN_MSG_STATS = (
    "📊 <b>Bot statistikasi</b>\n\n"
    "👥 Foydalanuvchilar: {users}\n"
    "📦 Buyurtmalar: {orders}\n"
    "💎 Jami ball: {points}\n"
    "🎯 Referallar: {referrals}"
)

ADMIN_MSG_NO_PENDING = "✅ Hozircha kutilayotgan so'rovlar yo'q."

ADMIN_MSG_REJECT_REASON = (
    "❌ <b>Buyurtma #{order_id} ni rad etish</b>\n\n"
    "Rad etish sababini yozing:"
)

ADMIN_MSG_REJECTED = (
    "✅ Buyurtma #{order_id} rad etildi. Foydalanuvchiga {points} ball qaytarildi."
)

# ============================================================
# SOZLAMALAR
# ============================================================
DEFAULT_POINTS_PER_REFERRAL = 50
DEFAULT_MIN_POINTS_FOR_ORDER = 100
DEFAULT_CHANNEL_USERNAME = "@kanal"
DEFAULT_CHANNEL_ID = ""

# ============================================================
# FSM HOLATLARI
# ============================================================
STATE_WAITING_FF_ID = "FF ID kiritish"
STATE_WAITING_CONFIRM = "Tasdiqlash"
STATE_WAITING_BROADCAST = "Xabar yuborish"
STATE_WAITING_USER_SEARCH = "Foydalanuvchi qidirish"
STATE_WAITING_SETTING_VALUE = "Sozlamani o'zgartirish"
STATE_WAITING_REJECT_REASON = "Rad etish sababi"

# ============================================================
# DATABASE SOZLAMALARI
# ============================================================
DB_PATH = "bot_database.db"  # Local uchun
DB_PATH_RAILWAY = "/data/bot_database.db"  # Railway uchun
