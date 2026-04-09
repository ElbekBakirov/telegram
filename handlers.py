from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)

from utils import notify_admins
from config import (
    CHANNEL_ID,
    CHANNEL_USERNAME,
    POINTS_PER_REFERRAL,
    MIN_POINTS_FOR_ORDER,
)
from database import (
    get_user,
    create_user,
    add_points,
    deduct_points,
    get_user_by_referral,
    count_referrals,
    save_referral,
    already_referred,
    create_order,
    get_user_orders,
    get_setting,
)
from keyboards import (
    main_menu_kb,
    channel_check_kb,
    order_confirm_kb,
    admin_order_kb,
)

router = Router()


# ============================================================
# FSM HOLATLARI
# ============================================================
class OrderState(StatesGroup):
    waiting_for_ff_id = State()
    waiting_for_confirm = State()


# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================
async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchining kanalga a'zo ekanligini tekshirish."""
    try:
        # Bazadan kanal ID sini olish, bo'lmasa configdagini ishlatish
        channel_id = await get_setting("channel_id", CHANNEL_ID)
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"❌ obuna tekshirishda xato (User: {user_id}): {e}")
        return False


# ============================================================
# /start BUYRUG'I
# ============================================================
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Botga kirganda ishlaydigan handler."""
    logger.info(f"📥 /start qabul qilindi: {message.from_user.id} ({message.from_user.full_name})")
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name

    # Referal kodi borligini tekshirish
    args = message.text.split()
    referral_code = args[1] if len(args) > 1 else None

    # Foydalanuvchini bazadan tekshirish
    user = await get_user(user_id)

    if not user:
        referred_by = None
        if referral_code:
            referrer = await get_user_by_referral(referral_code)
            if referrer and referrer["user_id"] != user_id:
                referred_by = referrer["user_id"]

        user = await create_user(user_id, username, full_name, referred_by)

        if referred_by:
            is_subscribed = await check_subscription(message.bot, user_id)
            if is_subscribed:
                if not await already_referred(user_id):
                    # Bazadan ball miqdorini olish
                    points_award = int(await get_setting("ref_points", POINTS_PER_REFERRAL))
                    await add_points(referred_by, points_award)
                    await save_referral(referred_by, user_id, points_award)
                    try:
                        await message.bot.send_message(
                            referred_by,
                            f"🎉 <b>Yangi referal!</b>\n\n"
                            f"Sizning havolangiz orqali yangi foydalanuvchi qo'shildi.\n"
                            f"💎 <b>+{points_award} ball</b> hisobingizga qo'shildi!",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass

    min_points = await get_setting("min_points", MIN_POINTS_FOR_ORDER)
    ref_points = await get_setting("ref_points", POINTS_PER_REFERRAL)

    await message.answer(
        f"🔥 <b>Xush kelibsiz, {full_name}!</b>\n\n"
        f"🎮 Bu bot orqali siz <b>Free Fire</b> o'yini uchun\n"
        f"bepul olmos (donat) olishingiz yoki sotib olishingiz mumkin!\n\n"
        f"📌 <b>Asosiy qoidalar:</b>\n"
        f"1️⃣ Do'stlaringizni taklif qiling — ball yig'ing\n"
        f"2️⃣ Yig'ilgan ballarni olmosga almashtiring\n"
        f"3️⃣ Yoki karta orqali arzon narxda sotib oling!\n\n"
        f"💎 Minimal yechib olish: <b>{min_points} ball</b>\n"
        f"🎯 Har bir referal: <b>+{ref_points} ball</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ============================================================
# 👤 PROFIL
# ============================================================
@router.message(F.text == "👤 Profil")
async def show_profile(message: Message):
    user = await get_user(message.from_user.id)
    ref_count = await count_referrals(user["user_id"])
    username = f"@{user['username']}" if user["username"] else "—"

    await message.answer(
        f"👤 <b>Sizning profilingiz</b>\n\n"
        f"┌ 🆔 ID: <code>{user['user_id']}</code>\n"
        f"├ 👤 Ism: <b>{user['full_name']}</b>\n"
        f"├ 📝 Username: {username}\n"
        f"├ 💎 Balans: <b>{user['points']} ball</b>\n"
        f"├ 👥 Referallar: <b>{ref_count} ta</b>\n"
        f"└ 📅 Ro'yxatdan: {user['joined_at'][:10]}",
        parse_mode="HTML",
    )


# ============================================================
# 🎯 BALL YIG'ISH (Yaxshilangan Referal Post)
# ============================================================
@router.message(F.text == "🎯 Ball yig'ish")
async def earn_points(message: Message):
    user = await get_user(message.from_user.id)
    bot_info = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user['referral_code']}"
    
    channel_user = await get_setting("channel_username", CHANNEL_USERNAME)
    ref_points = await get_setting("ref_points", POINTS_PER_REFERRAL)

    # Do'stlarga yuborish uchun tayyor post
    share_text = (
        f"🎮 <b>Free Fire bepul olmoslar olmoqchimisiz?</b>\n\n"
        f"Unda ushbu botga kiring, shartlarni bajaring va ball yig'ib olmoslaringizni yutib oling! 🔥\n\n"
        f"✅ <b>Ishtirok etish shartlari:</b>\n"
        f"1. Botga a'zo bo'lish\n"
        f"2. {channel_user} kanaliga a'zo bo'lish\n\n"
        f"💎 Har bir taklif uchun: <b>{ref_points} ball</b>\n\n"
        f"🚀 <b>Boshlash uchun bosing:</b>\n"
        f"{ref_link}"
    )

    await message.answer(
        f"🎯 <b>Ball yig'ish tizimi</b>\n\n"
        f"Quyidagi xabarni nusxalab do'stlaringizga yoki guruhlarga yuboring.\n"
        f"Har bir faol do'stingiz uchun <b>+{ref_points} ball</b> olasiz!\n\n"
        f"⚠️ <b>Muhim:</b> Do'stingiz albatta {channel_user} kanaliga a'zo bo'lishi shart.\n\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"{share_text}\n"
        f"➖➖➖➖➖➖➖➖➖➖",
        parse_mode="HTML",
    )


# ============================================================
# 🛒 BUYURTMA BERISH (BALL ORQALI)
# ============================================================
@router.message(F.text == "🛒 Buyurtma berish (Ball orqali)")
async def start_order(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    min_points = int(await get_setting("min_points", MIN_POINTS_FOR_ORDER))

    is_subscribed = await check_subscription(message.bot, message.from_user.id)
    if not is_subscribed:
        channel_user = await get_setting("channel_username", CHANNEL_USERNAME)
        await message.answer(
            f"⚠️ <b>Kanalga a'zo bo'ling!</b>\n\n"
            f"Davom etish uchun {channel_user} kanaliga a'zo bo'lishingiz shart.",
            parse_mode="HTML",
            reply_markup=channel_check_kb(),
        )
        return

    if user["points"] < min_points:
        await message.answer(
            f"❌ <b>Almaz yetarli emas!</b>\n\n"
            f"💎 Almazingiz: <b>{user['points']}</b>\n"
            f"📌 Minimal yechish miqdori: <b>{min_points}</b>\n\n"
            f"Almaz yig'ish uchun do'stlaringizni taklif qiling! 👥",
            parse_mode="HTML",
        )
        return

    await state.set_state(OrderState.waiting_for_ff_id)
    await message.answer(
        "🎮 <b>Free Fire ID yozing</b>\n\n"
        "Iltimos, o'zingizning to'g'ri ID raqamingizni yuboring:",
        parse_mode="HTML"
    )


@router.message(OrderState.waiting_for_ff_id)
async def process_ff_id(message: Message, state: FSMContext):
    ff_id = message.text.strip()
    if not ff_id.isdigit() or len(ff_id) < 6 or len(ff_id) > 12:
        await message.answer("❌ Noto'g'ri ID! Faqat raqamlardan iborat bo'lishi kerak.")
        return

    min_points = int(await get_setting("min_points", MIN_POINTS_FOR_ORDER))
    await state.update_data(ff_id=ff_id, points=min_points)
    await state.set_state(OrderState.waiting_for_confirm)

    await message.answer(
        f"📋 <b>Tasdiqlash:</b>\n\n"
        f"🎮 FF ID: <code>{ff_id}</code>\n"
        f"💎 Sarf: <b>{min_points} ball</b>\n\n"
        f"Rozimisiz?",
        parse_mode="HTML",
        reply_markup=order_confirm_kb(min_points)
    )


@router.callback_query(F.data.startswith("confirm_order:"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ff_id, points = data.get("ff_id"), data.get("points")
    
    await deduct_points(callback.from_user.id, points)
    order_id = await create_order(callback.from_user.id, ff_id, points)

    await callback.message.edit_text(
        f"✅ <b>Buyurtma #{order_id} qabul qilindi!</b>\n\n"
        f"Tez orada admin ko'rib chiqadi va olmoslarni yuboradi.",
        parse_mode="HTML"
    )
    
    await notify_admins(
        callback.bot,
        f"🆕 <b>Yangi so'rov!</b>\n\n"
        f"ID: #{order_id}\n"
        f"User: {callback.from_user.full_name}\n"
        f"FF ID: <code>{ff_id}</code>\n"
        f"Ball: {points}",
        reply_markup=admin_order_kb(order_id)
    )
    await state.clear()


# ============================================================
# 💎 OLMOS SOTIB OLISH (PULLIK)
# ============================================================
@router.message(F.text == "💎 Olmos sotib olish")
async def buy_diamonds(message: Message):
    card_info = await get_setting("card_info", "Karta kiritilmagan")
    card_phone = await get_setting("card_phone", "Raqam kiritilmagan")
    buy_rules = await get_setting("buy_rules", "Sotib olish shartlari hali kiritilmagan.")

    await message.answer(
        f"💎 <b>Almaz sotib olish</b>\n\n"
        f"Siz Almazlarni arzon narxlarda xarid qilishingiz mumkin!\n\n"
        f"💳 <b>To'lov uchun karta:</b>\n"
        f"<code>{card_info}</code>\n"
        f"📞 <b>Bog'lanish:</b> {card_phone}\n\n"
        f"📜 <b>Sotib olish shartlari:</b>\n"
        f"{buy_rules}\n\n"
        f"⚠️ To'lov qilganingizdan so'ng, chekni va Free Fire ID raqamingizni @admin ga yuboring.",
        parse_mode="HTML"
    )


# ============================================================
# ✅ KANAL TEKSHIRUV VA BOSHQA
# ============================================================
@router.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback: CallbackQuery):
    is_subscribed = await check_subscription(callback.bot, callback.from_user.id)
    if is_subscribed:
        await callback.message.edit_text("✅ Rahmat! Endi botdan foydalanishingiz mumkin.")
    else:
        await callback.answer("❌ Kanalga hali a'zo emassiz!", show_alert=True)


@router.message(F.text == "📦 Buyurtmalarim")
async def my_orders(message: Message):
    orders = await get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("Sizda hali buyurtmalar yo'q.")
        return

    text = "📦 <b>Sizning buyurtmalaringiz:</b>\n\n"
    for o in orders:
        status = "⏳" if o["status"] == "pending" else "✅" if o["status"] == "approved" else "❌"
        text += f"{status} #{o['id']} | FF ID: {o['ff_id']} | {o['status']}\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🆘 Yordam")
async def cmd_help(message: Message):
    await message.answer("Bot bo'yicha yordam kerak bo'lsa @admin bilan bog'laning.")
