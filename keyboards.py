from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from config import CHANNEL_USERNAME
from constants import (
    BTN_PROFILE,
    BTN_EARN_POINTS,
    BTN_ORDER_POINTS,
    BTN_BUY_DIAMONDS,
    BTN_MY_ORDERS,
    BTN_HELP,
    BTN_ADMIN_STATS,
    BTN_ADMIN_USERS,
    BTN_ADMIN_CARDS,
    BTN_ADMIN_ORDERS,
    BTN_ADMIN_BROADCAST,
    BTN_ADMIN_SETTINGS,
    BTN_ADMIN_BACK,
    BTN_ADMIN_MIGRATE,
    BTN_BACK_TO_MAIN,
    BTN_CANCEL,
)


# ============================================================
# ASOSIY MENYU (Reply Keyboard)
# ============================================================

def main_menu_kb() -> ReplyKeyboardMarkup:
    """Foydalanuvchi uchun asosiy menyu."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_PROFILE), KeyboardButton(text=BTN_EARN_POINTS)],
            [KeyboardButton(text=BTN_ORDER_POINTS), KeyboardButton(text=BTN_BUY_DIAMONDS)],
            [KeyboardButton(text=BTN_MY_ORDERS), KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Menyudan tanlang..."
    )


def admin_menu_kb() -> ReplyKeyboardMarkup:
    """Admin uchun kengaytirilgan asosiy menyu."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ADMIN_ORDERS), KeyboardButton(text=BTN_ADMIN_USERS)],
            [KeyboardButton(text=BTN_ADMIN_CARDS), KeyboardButton(text=BTN_ADMIN_BROADCAST)],
            [KeyboardButton(text=BTN_ADMIN_SETTINGS), KeyboardButton(text=BTN_ADMIN_STATS)],
            [KeyboardButton(text=BTN_ADMIN_MIGRATE), KeyboardButton(text=BTN_ADMIN_BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Admin paneli (V2.0)..."
    )


# ============================================================
# INLINE TUGMALAR
# ============================================================

def channel_check_kb() -> InlineKeyboardMarkup:
    """Kanalga a'zo bo'lishni tekshirish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga o'tish", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription")],
    ])


def order_confirm_kb(points: int) -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_order:{points}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order"),
        ],
    ])


def admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    """Admin uchun buyurtma boshqaruv tugmalari."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_approve:{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_reject:{order_id}"),
        ],
    ])


def user_manage_kb(user_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    """Admin uchun foydalanuvchini boshqarish tugmalari."""
    ban_text = "🔓 Blokdan chiqarish" if is_banned else "🚫 Bloklash"
    ban_data = f"admin_unban:{user_id}" if is_banned else f"admin_ban:{user_id}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ban_text, callback_data=ban_data)],
        [InlineKeyboardButton(text="💎 Ball qo'shish (50)", callback_data=f"admin_add_points:{user_id}:50")],
        [InlineKeyboardButton(text="💎 Ball ayirish (50)", callback_data=f"admin_sub_points:{user_id}:50")],
    ])


def settings_manage_kb() -> InlineKeyboardMarkup:
    """Admin uchun sozlamalarni boshqarish tugmalari."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Karta ma'lumotlarini o'zgartirish", callback_data="edit_setting:card_info")],
        [InlineKeyboardButton(text="📞 Telefon raqamni o'zgartirish", callback_data="edit_setting:card_phone")],
        [InlineKeyboardButton(text="💰 Minimal ballni o'zgartirish", callback_data="edit_setting:min_points")],
        [InlineKeyboardButton(text="💎 Referal ballini o'zgartirish", callback_data="edit_setting:ref_points")],
    ])


def back_to_menu_kb() -> InlineKeyboardMarkup:
    """Menyuga qaytish tugmasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Menyuga qaytish", callback_data="back_to_menu")],
    ])


def cancel_kb() -> ReplyKeyboardMarkup:
    """Holatni bekor qilish uchun Reply tugma."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True
    )
