from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import asyncio

from config import ADMIN_IDS, OTZIV_GROUP_ID
from utils import is_admin, notify_admins
from database import (
    get_order,
    get_pending_orders,
    update_order_status,
    add_points,
    deduct_points,
    get_stats,
    get_all_users,
    get_user,
    ban_user,
    unban_user,
    get_setting,
    set_setting,
    add_payment_card,
    get_all_payment_cards,
    get_payment_card,
    delete_payment_card,
    get_active_payment_card,
)
from keyboards import (
    admin_menu_kb,
    main_menu_kb,
    admin_order_kb,
    user_manage_kb,
    settings_manage_kb,
    cancel_kb
)

router = Router()


# ============================================================
# 🛑 HOLATNI BEKOR QILISH (MAJBURIY CLEAR STATE)
# ============================================================
@router.message(F.text == "❌ Bekor qilish")
@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    """Har qanday holatni bekor qilish va menyuga qaytish."""
    current_state = await state.get_state()
    if current_state is None:
        return
        
    await state.clear()
    await message.answer(
        "❌ Amaliyot bekor qilindi.",
        reply_markup=admin_menu_kb() if await is_admin(message.from_user.id) else main_menu_kb()
    )


# ============================================================
# LOG TIZIMI
# ============================================================
logger = logging.getLogger(__name__)


# ============================================================
# FSM HOLATLARI
# ============================================================
class AdminState(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_search = State()
    waiting_for_setting_value = State()
    waiting_for_reject_reason = State()
    # Migratsiya holatlari
    waiting_for_new_admin_id = State()
    waiting_for_new_channel_id = State()
    waiting_for_new_channel_user = State()
    waiting_for_migration_msg = State()
    waiting_for_migration_confirm = State()

    # Karta boshqarish holatlari
    waiting_for_card_number = State()
    waiting_for_card_holder = State()
    waiting_for_expiry_date = State()
    waiting_for_bank_name = State()


# ============================================================
# 🔑 ADMIN KO'CHIRISH (MIGRATION)
# ============================================================
@router.message(F.text == "🔑 Adminni ko'chirish")
async def start_migration(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    
    # Faqat asosiy adminlar (config dagi) ko'chira olsin deb cheklash mumkin
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⚠️ Botni faqat asosiy Owner (Egasi) ko'chira oladi!")
        return

    await state.set_state(AdminState.waiting_for_new_admin_id)
    await message.answer(
        "🔑 <b>Admin Ko'chirish Tizimi (V2.0)</b>\n\n"
        "Ushbu amal botni boshqa admin va kanalga to'liq o'tkazadi.\n\n"
        "1️⃣ Yangi adminning <b>Telegram ID</b> raqamini yuboring:",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )


@router.message(AdminState.waiting_for_new_admin_id)
async def process_new_admin_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ ID faqat raqamlardan iborat bo'lishi kerak!")
        return
    
    await state.update_data(new_admin_id=message.text)
    await state.set_state(AdminState.waiting_for_new_channel_id)
    await message.answer("2️⃣ Yangi <b>Kanal ID</b> raqamini yuboring (masalan: -100...):", reply_markup=cancel_kb())


@router.message(AdminState.waiting_for_new_channel_id)
async def process_new_channel_id(message: Message, state: FSMContext):
    if not (message.text.startswith("-100") and message.text[1:].isdigit() or message.text.startswith("-") and message.text[1:].isdigit()):
        await message.answer("❌ Noto'g'ri Kanal ID!")
        return
    
    await state.update_data(new_channel_id=message.text)
    await state.set_state(AdminState.waiting_for_new_channel_user)
    await message.answer("3️⃣ Yangi <b>Kanal Username</b> sini yuboring (@ belgisiz):", reply_markup=cancel_kb())


@router.message(AdminState.waiting_for_new_channel_user)
async def process_new_channel_user(message: Message, state: FSMContext):
    user_name = message.text.replace("@", "").strip()
    await state.update_data(new_channel_user=f"@{user_name}")
    await state.set_state(AdminState.waiting_for_migration_msg)
    await message.answer(
        "4️⃣ <b>Migratsiya xabarini yuboring.</b>\n\n"
        "Ushbu xabar barcha foydalanuvchilarga yuboriladi va yangi shartlar haqida ma'lumot beradi.\n"
        "(Rasm, video yoki matn yuborishingiz mumkin):",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )


@router.message(AdminState.waiting_for_migration_msg)
async def process_migration_msg(message: Message, state: FSMContext):
    # Xabarni saqlaymiz (copy qilish uchun id sini va chat id sini)
    await state.update_data(msg_id=message.message_id, msg_chat_id=message.chat.id)
    
    data = await state.get_data()
    await state.set_state(AdminState.waiting_for_migration_confirm)
    
    confirm_text = (
        f"⚠️ <b>DIQQAT! MA'LUMOTLARNI TASDIQLANG:</b>\n\n"
        f"👤 Yangi Admin: <code>{data['new_admin_id']}</code>\n"
        f"📺 Yangi Kanal ID: <code>{data['new_channel_id']}</code>\n"
        f"📝 Yangi Kanal: {data['new_channel_user']}\n\n"
        f"Tasdiqlaysizmi? Bot darhol yangi adminga o'tadi va barcha foydalanuvchilarga xabar yuboradi!"
    )
    
    await message.answer(
        confirm_text, 
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ TASDIQLASH", callback_data="confirm_migration")],
            [InlineKeyboardButton(text="❌ BEKOR QILISH", callback_data="cancel_migration")]
        ])
    )


@router.callback_query(F.data == "confirm_migration")
async def finalize_migration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # 1. Bazani yangilash
    await set_setting("admin_id", data['new_admin_id'])
    await set_setting("channel_id", data['new_channel_id'])
    await set_setting("channel_username", data['new_channel_user'])
    
    # 2. Xabarni hamma yuborish (Reklama kabi)
    users = await get_all_users()
    await callback.message.edit_text("🚀 Migratsiya boshlandi, xabarlar yuborilmoqda...")
    
    count = 0
    for u in users:
        try:
            await callback.bot.copy_message(
                chat_id=u['user_id'],
                from_chat_id=data['msg_chat_id'],
                message_id=data['msg_id']
            )
            count += 1
            await asyncio.sleep(0.05) # Rate limit dan qochish
        except Exception:
            pass
            
    await callback.message.answer(
        f"✅ <b>Muvaffaqiyatli!</b>\n\n"
        f"Bot yangi adminga topshirildi.\n"
        f"Yuborilgan xabarlar: {count} ta.\n"
        f"Sizning adminlik huquqingiz hozir bekor qilinadi.",
        parse_mode="HTML"
    )
    
    try:
        await callback.bot.send_message(
            data['new_admin_id'], 
            "🎉 <b>Tabriklaymiz!</b>\n\nBot sizning boshqaruvingizga o'tdi. /admin buyrug'ini yuboring.",
            parse_mode="HTML",
            reply_markup=admin_menu_kb()
        )
    except: pass
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_migration")
async def cancel_migration_proc(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Migratsiya bekor qilindi.")
    await callback.answer()


# ============================================================
# ADMIN PANEL KIRISH
# ============================================================
@router.message(F.text == "/admin")
async def cmd_admin(message: Message):
    if not await is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🛡 <b>Admin Panel (V2.0)</b>\n\n"
        "Xizmat ko'rsatishga tayyorman, admin!",
        parse_mode="HTML",
        reply_markup=admin_menu_kb()
    )


# ============================================================
# 👥 FOYDALANUVCHILAR BOSHQARUVI
# ============================================================
@router.message(F.text == "👥 Foydalanuvchilar")
async def manage_users(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    
    users = await get_all_users()
    text = f"👥 <b>Foydalanuvchilar (Jami: {len(users)})</b>\n\n"
    
    # Oxirgi 20 tasini ko'rsatamiz
    for u in users[:20]:
        username = f"@{u['username']}" if u['username'] else "yo'q"
        text += f"• {u['full_name']} | {username} | (<code>{u['user_id']}</code>) | {u['points']} ball\n"
    
    text += "\n✏️ Foydalanuvchini boshqarish uchun uning <b>ID</b> raqamini yuboring:"
    
    await state.set_state(AdminState.waiting_for_user_search)
    await message.answer(text, parse_mode="HTML", reply_markup=cancel_kb())


@router.message(AdminState.waiting_for_user_search)
async def search_user(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    
    if not message.text.isdigit():
        await message.answer("❌ ID raqam yuboring!")
        return
        
    user_id = int(message.text)
    user = await get_user(user_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi!")
        return
        
    ban_status = "Ha" if user['is_banned'] else "Yo'q"
    username = f"@{user['username']}" if user['username'] else "yo'q"
    await message.answer(
        f"👤 <b>Foydalanuvchi ma'lumotlari:</b>\n\n"
        f"Ism: {user['full_name']}\n"
        f"Username: {username}\n"
        f"ID: <code>{user['user_id']}</code>\n"
        f"Ball: {user['points']}\n"
        f"Bloklangan: {ban_status}",
        parse_mode="HTML",
        reply_markup=user_manage_kb(user['user_id'], user['is_banned'])
    )


@router.callback_query(F.data.startswith("admin_ban:"))
async def ban_user_callback(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await ban_user(user_id)
    await callback.message.edit_reply_markup(reply_markup=user_manage_kb(user_id, True))
    await callback.answer("🚫 Foydalanuvchi bloklandi!")


@router.callback_query(F.data.startswith("admin_unban:"))
async def unban_user_callback(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await unban_user(user_id)
    await callback.message.edit_reply_markup(reply_markup=user_manage_kb(user_id, False))
    await callback.answer("🔓 Blokdan chiqarildi!")


# ============================================================
# 📢 REKLAMA (MAILING)
# ============================================================
@router.message(F.text == "📢 Reklama yuborish")
async def start_broadcast(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    
    await state.set_state(AdminState.waiting_for_broadcast)
    await message.answer("📢 <b>Reklama xabarini yuboring.</b>\n\nHar qanday (text, rasm, video) xabar o'z shaklida barcha foydalanuvchilarga yuboriladi.", parse_mode="HTML", reply_markup=cancel_kb())


@router.message(AdminState.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    
    users = await get_all_users()
    count = 0
    await message.answer(f"🚀 Reklama yuborish boshlandi (Jami: {len(users)})...")
    
    for u in users:
        try:
            await message.copy_to(chat_id=u['user_id'])
            count += 1
            await asyncio.sleep(0.05) # Rate limit dan qochish
        except Exception:
            pass
            
    await message.answer(f"✅ Reklama yakunlandi! {count} ta foydalanuvchiga yuborildi.")
    await state.clear()


# ============================================================
# ⚙️ SOZLAMALAR
# ============================================================
@router.message(F.text == "⚙️ Bot sozlamalari")
async def show_settings(message: Message):
    if not await is_admin(message.from_user.id): return
    
    await message.answer(
        "⚙️ <b>Bot sozlamalari</b>\n\n"
        "Quyidagi parametrlarni o'zgartirishingiz mumkin:",
        parse_mode="HTML",
        reply_markup=settings_manage_kb()
    )


@router.callback_query(F.data.startswith("edit_setting:"))
async def edit_setting_start(callback: CallbackQuery, state: FSMContext):
    setting_key = callback.data.split(":")[1]
    await state.update_data(setting_key=setting_key)
    await state.set_state(AdminState.waiting_for_setting_value)
    await callback.message.answer(f"✏️ Yangi qiymatni yuboring (Kalit: {setting_key}):", reply_markup=cancel_kb())
    await callback.answer()


@router.message(AdminState.waiting_for_setting_value)
async def save_setting(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("setting_key")
    val = message.text.strip()
    
    await set_setting(key, val)
    await message.answer(f"✅ Saqlandi: {key} = {val}")
    await state.clear()


# ============================================================
# BUYURTMANI TASDIQLASH VA "OTZIV" GURUHI
# ============================================================
@router.callback_query(F.data.startswith("admin_approve:"))
async def approve_order_proc(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = await get_order(order_id)
    user = await get_user(order["user_id"])
    
    await update_order_status(order_id, "approved")
    
    # 📢 OTZIV GURUHIGA YUBORISH
    otziv_id = await get_setting("otziv_id", OTZIV_GROUP_ID)
    username = f"@{user['username']}" if user['username'] else user['full_name']
    
    otziv_text = (
        f"🎉 <b>Yangi Olmos topshirildi!</b>\n\n"
        f"👤 Foydalanuvchi: {username}\n"
        f"💎 Miqdori: {order['points_spent']} ballik\n"
        f"🎮 FF ID: <code>{order['ff_id']}</code>\n"
        f"✅ Holat: <b>Muvaffaqiyatli topshirildi</b>\n\n"
        f"🔥 Siz ham ball yig'ing va bepul olmos oling!"
    )
    
    try:
        await callback.bot.send_message(chat_id=otziv_id, text=otziv_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Otziv yuborishda xatolik: {e}")

    await callback.message.edit_text(f"✅ Buyurtma #{order_id} tasdiqlandi va Otzivga post yuborildi!")
    
    try:
        await callback.bot.send_message(order['user_id'], "🎉 Buyurtmangiz tasdiqlandi! Olmoslar o'yiningizga yuborildi.")
    except: pass
    await callback.answer()


@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    if not await is_admin(message.from_user.id): return
    
    stats = await get_stats()
    
    text = (
        f"📊 <b>Umumiy Bot Statistikasi</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"├ Jami: <b>{stats['total_users']} ta</b>\n"
        f"├ Bugun qo'shildi: <b>{stats['today_users']} ta</b>\n"
        f"└ Jami tizimdagi ballar: <b>{stats['total_points']} 💎</b>\n\n"
        
        f"📦 <b>Buyurtmalar (Ball orqali):</b>\n"
        f"├ Jami: <b>{stats['total_orders']} ta</b>\n"
        f"├ Kutilmoqda: ⏳ <b>{stats['pending_orders']} ta</b>\n"
        f"├ Tasdiqlandi: ✅ <b>{stats['approved_orders']} ta</b>\n"
        f"├ Rad etildi: ❌ <b>{stats['rejected_orders']} ta</b>\n"
        f"└ Bugungi buyurtmalar: <b>{stats['today_orders']} ta</b>\n\n"
        
        f"🏆 <b>Top 5 Taklif qiluvchilar:</b>\n"
    )
    
    for i, r in enumerate(stats['top_referrals'], 1):
        text += f"{i}. {r['full_name']} — <b>{r['ref_count']} ta</b>\n"
        
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🔙 Oddiy menyu")
async def back_to_main(message: Message):
    await message.answer("Bosh menyuga qaytdingiz.", reply_markup=main_menu_kb())


# ============================================================
# 📋 YANGI SO'ROVLAR (PENDING ORDERS)
# ============================================================
@router.message(F.text == "📋 Yangi so'rovlar")
async def show_pending_orders(message: Message):
    if not await is_admin(message.from_user.id):
        return

    orders = await get_pending_orders()

    if not orders:
        await message.answer("✅ Hozircha kutilayotgan buyurtmalar yo'q.")
        return

    await message.answer(f"📋 <b>Kutilayotgan buyurtmalar: {len(orders)} ta</b>", parse_mode="HTML")

    for order in orders:
        username = f"@{order['username']}" if order['username'] else order['full_name']
        text = (
            f"🆕 <b>Buyurtma #{order['id']}</b>\n\n"
            f"👤 Foydalanuvchi: {username}\n"
            f"🎮 FF ID: <code>{order['ff_id']}</code>\n"
            f"💎 Ball: <b>{order['points_spent']}</b>\n"
            f"📅 Vaqt: {order['created_at'][:16]}"
        )
        await message.answer(text, parse_mode="HTML", reply_markup=admin_order_kb(order['id']))


# ============================================================
# ❌ BUYURTMANI RAD ETISH
# ============================================================
@router.callback_query(F.data.startswith("admin_reject:"))
async def reject_order_proc(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])
    await state.update_data(reject_order_id=order_id)
    await state.set_state(AdminState.waiting_for_reject_reason)
    await callback.message.answer(
        f"❌ <b>Buyurtma #{order_id} rad etilmoqda.</b>\n\n"
        f"Rad etish sababini yozing:",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )
    await callback.answer()


@router.message(AdminState.waiting_for_reject_reason)
async def process_reject_reason(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    data = await state.get_data()
    order_id = data.get("reject_order_id")
    reason = message.text.strip()

    order = await get_order(order_id)
    if not order:
        await message.answer("❌ Buyurtma topilmadi!")
        await state.clear()
        return

    await update_order_status(order_id, "rejected", reason)

    await message.answer(
        f"✅ Buyurtma #{order_id} rad etildi.\nSabab: {reason}",
        reply_markup=admin_menu_kb()
    )

    try:
        await message.bot.send_message(
            order['user_id'],
            f"❌ <b>Buyurtmangiz rad etildi!</b>\n\n"
            f"Buyurtma #{order_id}\n"
            f"Sabab: {reason}\n\n"
            f"Savollar bo'lsa admin bilan bog'laning.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await state.clear()


# ============================================================
# 💎 BALL QO'SHISH / AYIRISH
# ============================================================
@router.callback_query(F.data.startswith("admin_add_points:"))
async def admin_add_points_cb(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = int(parts[1])
    points = int(parts[2])

    await add_points(user_id, points)
    user = await get_user(user_id)

    await callback.answer(f"✅ +{points} ball qo'shildi!", show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=user_manage_kb(user_id, user['is_banned']))

    try:
        await callback.bot.send_message(
            user_id,
            f"🎉 Hisobingizga <b>+{points} ball</b> qo'shildi!",
            parse_mode="HTML"
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin_sub_points:"))
async def admin_sub_points_cb(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = int(parts[1])
    points = int(parts[2])

    user = await get_user(user_id)
    if not user or user['points'] < points:
        await callback.answer("❌ Foydalanuvchida yetarli ball yo'q!", show_alert=True)
        return

    await deduct_points(user_id, points)
    user = await get_user(user_id)

    await callback.answer(f"✅ -{points} ball ayirildi!", show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=user_manage_kb(user_id, user['is_banned']))

    try:
        await callback.bot.send_message(
            user_id,
            f"⚠️ Hisobingizdan <b>-{points} ball</b> ayirildi.",
            parse_mode="HTML"
        )
    except Exception:
        pass


# ============================================================
# ❌ BUYURTMANI BEKOR QILISH (FOYDALANUVCHI TOMONIDAN)
# ============================================================
@router.callback_query(F.data == "cancel_order")
async def cancel_order_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await callback.answer()


# ============================================================
# 💳 KARTA BOSHQARISH
# ============================================================

@router.message(F.text == "💳 Kartalar")
async def show_cards(message: Message):
    logger.info(f"📋 Kartalar handler ishga tushdi: {message.from_user.id}")
    if not await is_admin(message.from_user.id):
        logger.warning(f"⚠️ Foydalanuvchi admin emas: {message.from_user.id}")
        return

    cards = await get_all_payment_cards()
    logger.info(f"📋 Kartalar soni: {len(cards)}")
    if not cards:
        await message.answer(
            "📋 <b>Hozircha karta yo'q.</b>\n\n"
            "Yangi karta qo'shish uchun quyidagi tugmani bosing.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Karta qo'shish", callback_data="add_card")],
                    [InlineKeyboardButton(text="🔙 Admin menyu", callback_data="back_to_admin")]
                ]
            ),
            parse_mode="HTML"
        )
        return

    text = "💳 <b>Mavjud kartalar:</b>\n\n"
    buttons = []
    for card in cards:
        text += (
            f"🔹 <b>ID: {card['id']}</b>\n"
            f"🏦 Bank: {card['bank_name']}\n"
            f"💳 Karta: {card['card_number']}\n"
            f"👤 Egal: {card['card_holder']}\n"
            f"📅 Muddat: {card['expiry_date']}\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
        )
        buttons.append([InlineKeyboardButton(text=f"🗑️ O'chirish (ID: {card['id']})", callback_data=f"delete_card:{card['id']}")])

    buttons.append([InlineKeyboardButton(text="➕ Karta qo'shish", callback_data="add_card")])
    buttons.append([InlineKeyboardButton(text="🔙 Admin menyu", callback_data="back_to_admin")])

    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "add_card")
async def start_add_card(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return

    await state.set_state(AdminState.waiting_for_card_number)
    await callback.message.edit_text(
        "💳 <b>Yangi karta qo'shish</b>\n\n"
        "Karta raqamini kiriting (misol: 8600 1234 5678 9012):",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_admin")]
            ]
        ),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_for_card_number)
async def process_card_number(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    card_number = message.text.strip()
    await state.update_data(card_number=card_number)
    await state.set_state(AdminState.waiting_for_card_holder)

    await message.answer(
        "👤 <b>Karta egasining ismini kiriting:</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_admin")]
            ]
        ),
        parse_mode="HTML"
    )


@router.message(AdminState.waiting_for_card_holder)
async def process_card_holder(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    card_holder = message.text.strip()
    await state.update_data(card_holder=card_holder)
    await state.set_state(AdminState.waiting_for_expiry_date)

    await message.answer(
        "📅 <b>Muddatni kiriting (MM/YY formatida):</b>\n\n"
        "Misol: 12/25",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_admin")]
            ]
        ),
        parse_mode="HTML"
    )


@router.message(AdminState.waiting_for_expiry_date)
async def process_expiry_date(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    expiry_date = message.text.strip()
    await state.update_data(expiry_date=expiry_date)
    await state.set_state(AdminState.waiting_for_bank_name)

    await message.answer(
        "🏦 <b>Bank nomini kiriting:</b>\n\n"
        "Misol: UzumBank, TBC Bank, Payme",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_admin")]
            ]
        ),
        parse_mode="HTML"
    )


@router.message(AdminState.waiting_for_bank_name)
async def process_bank_name(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    bank_name = message.text.strip()
    data = await state.get_data()

    card_number = data.get("card_number")
    card_holder = data.get("card_holder")
    expiry_date = data.get("expiry_date")

    # Karta qo'shish
    card_id = await add_payment_card(card_number, card_holder, expiry_date, bank_name)

    await message.answer(
        f"✅ <b>Karta muvaffaqiyatli qo'shildi!</b>\n\n"
        f"🔹 ID: {card_id}\n"
        f"💳 Karta: {card_number}\n"
        f"👤 Egal: {card_holder}\n"
        f"📅 Muddat: {expiry_date}\n"
        f"🏦 Bank: {bank_name}",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML"
    )
    await state.clear()


@router.callback_query(F.data.startswith("delete_card:"))
async def delete_card(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return

    card_id = int(callback.data.split(":")[1])
    await delete_payment_card(card_id)

    await callback.answer("✅ Karta o'chirildi!", show_alert=True)
    await callback.message.edit_text(
        "✅ Karta o'chirildi.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin menyu", callback_data="back_to_admin")]
            ]
        )
    )


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "👮‍♂️ <b>Admin Panel</b>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()
