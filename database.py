import os
import aiosqlite
import uuid
from datetime import datetime
from pathlib import Path
from config import DB_PATH


async def init_db():
    """Ma'lumotlar bazasini yaratish va jadvallarni sozlash."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        # Jadval mavjudligini tekshirish
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_cards'")
        table_exists = await cursor.fetchone()
        print(f"📊 payment_cards jadvali mavjud: {bool(table_exists)}")

        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                points INTEGER DEFAULT 0,
                referral_code TEXT UNIQUE NOT NULL,
                referred_by INTEGER,
                is_banned INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Buyurtmalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ff_id TEXT NOT NULL,
                points_spent INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                reject_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Referallar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL,
                points_awarded INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sozlamalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # To'lov kartalari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payment_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_number TEXT NOT NULL,
                card_holder TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ payment_cards jadvali yaratildi/yangilandi")

        await db.commit()


# ============================================================
# FOYDALANUVCHI FUNKSIYALARI
# ============================================================

async def get_user(user_id: int) -> dict | None:
    """Foydalanuvchini ID bo'yicha topish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def create_user(user_id: int, username: str, full_name: str, referred_by: int = None) -> dict:
    """Yangi foydalanuvchi yaratish."""
    referral_code = str(uuid.uuid4())[:8].upper()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, full_name, referral_code, referred_by)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, full_name, referral_code, referred_by))
        await db.commit()
    return await get_user(user_id)


async def add_points(user_id: int, points: int):
    """Foydalanuvchiga ball qo'shish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET points = points + ? WHERE user_id = ?",
            (points, user_id)
        )
        await db.commit()


async def deduct_points(user_id: int, points: int):
    """Foydalanuvchidan ball ayirish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET points = points - ? WHERE user_id = ?",
            (points, user_id)
        )
        await db.commit()


async def get_user_by_referral(referral_code: str) -> dict | None:
    """Referal kodi bo'yicha foydalanuvchini topish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE referral_code = ?", (referral_code,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def ban_user(user_id: int):
    """Foydalanuvchini bloklash."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()


async def unban_user(user_id: int):
    """Foydalanuvchini blokdan chiqarish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()


async def is_user_banned(user_id: int) -> bool:
    """Foydalanuvchi bloklanganligini tekshirish."""
    user = await get_user(user_id)
    return bool(user["is_banned"]) if user else False


async def get_all_users() -> list:
    """Barcha foydalanuvchilar ro'yxati."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY joined_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def count_referrals(user_id: int) -> int:
    """Foydalanuvchining referal soni."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def save_referral(referrer_id: int, referred_id: int, points: int):
    """Referal yozuvini saqlash."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO referrals (referrer_id, referred_id, points_awarded)
            VALUES (?, ?, ?)
        """, (referrer_id, referred_id, points))
        await db.commit()


async def already_referred(referred_id: int) -> bool:
    """Bu foydalanuvchi orqali avval referal yo'llanganligini tekshirish."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM referrals WHERE referred_id = ?", (referred_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] > 0


# ============================================================
# SOZLAMALAR FUNKSIYALARI
# ============================================================

async def get_setting(key: str, default: str = None) -> str:
    """Sozlamani bazadan olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else default


async def set_setting(key: str, value: str):
    """Sozlamani bazaga yozish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        """, (key, str(value)))
        await db.commit()


# ============================================================
# BUYURTMA FUNKSIYALARI
# ============================================================

async def create_order(user_id: int, ff_id: str, points_spent: int) -> int:
    """Yangi buyurtma yaratish. Qaytadi: order ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO orders (user_id, ff_id, points_spent)
            VALUES (?, ?, ?)
        """, (user_id, ff_id, points_spent))
        await db.commit()
        return cursor.lastrowid


async def get_order(order_id: int) -> dict | None:
    """Buyurtmani ID bo'yicha topish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_user_orders(user_id: int) -> list:
    """Foydalanuvchining barcha buyurtmalari."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_pending_orders() -> list:
    """Kutilayotgan barcha buyurtmalar."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT o.*, u.username, u.full_name
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.status = 'pending'
            ORDER BY o.created_at ASC
        """) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def update_order_status(order_id: int, status: str, reject_reason: str = None):
    """Buyurtma holatini yangilash."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE orders
            SET status = ?, reject_reason = ?, processed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, reject_reason, order_id))
        await db.commit()


# ============================================================
# STATISTIKA FUNKSIYALARI
# ============================================================

async def get_stats() -> dict:
    """Umumiy statistika."""
    async with aiosqlite.connect(DB_PATH) as db:
        # User soni
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total_users = (await c.fetchone())[0]

        # Jami ballar
        async with db.execute("SELECT SUM(points) FROM users") as c:
            total_points = (await c.fetchone())[0] or 0

        # Jami orderlar
        async with db.execute("SELECT COUNT(*) FROM orders") as c:
            total_orders = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM orders WHERE status='pending'") as c:
            pending_orders = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM orders WHERE status='approved'") as c:
            approved_orders = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM orders WHERE status='rejected'") as c:
            rejected_orders = (await c.fetchone())[0]

        # Bugungi statistika
        async with db.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = DATE('now')") as c:
            today_orders = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM users WHERE DATE(joined_at) = DATE('now')") as c:
            today_users = (await c.fetchone())[0]

        # Top 5 referal yig'uvchilar
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT u.full_name, COUNT(r.id) as ref_count 
            FROM users u 
            LEFT JOIN referrals r ON u.user_id = r.referrer_id 
            GROUP BY u.user_id 
            ORDER BY ref_count DESC 
            LIMIT 5
        """) as cursor:
            top_referrals = [dict(r) for r in await cursor.fetchall()]

    return {
        "total_users": total_users,
        "total_points": total_points,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "approved_orders": approved_orders,
        "rejected_orders": rejected_orders,
        "today_orders": today_orders,
        "today_users": today_users,
        "top_referrals": top_referrals
    }


# ============================================================
# KARTA FUNKSIYALARI
# ============================================================

async def add_payment_card(card_number: str, card_holder: str) -> int:
    """Yangi karta qo'shish. Qaytadi: card ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO payment_cards (card_number, card_holder)
            VALUES (?, ?)
        """, (card_number, card_holder))
        await db.commit()
        return cursor.lastrowid


async def get_all_payment_cards() -> list:
    """Barcha faol kartalar ro'yxati."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM payment_cards WHERE is_active = 1 ORDER BY created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            cards = [dict(r) for r in rows]
            print(f"📋 {len(cards)} ta karta topildi")
            return cards


async def get_payment_card(card_id: int) -> dict | None:
    """Kartani ID bo'yicha topish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM payment_cards WHERE id = ?", (card_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def delete_payment_card(card_id: int):
    """Kartani o'chirish (soft delete)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE payment_cards SET is_active = 0 WHERE id = ?", (card_id,)
        )
        await db.commit()


async def get_active_payment_card() -> dict | None:
    """Birinchi faol kartani olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM payment_cards WHERE is_active = 1 LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
