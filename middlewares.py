import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from database import is_user_banned

# ============================================================
# ANTI-SPAM MIDDLEWARE (THROTTLING)
# ============================================================
class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 1.0):
        self.limit = limit
        self.last_requests: Dict[int, float] = {}
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.last_requests:
            elapsed = current_time - self.last_requests[user_id]
            if elapsed < self.limit:
                # Spam aniqlandi - indamaymiz yoki ogohlantiramiz
                # await event.answer("⚠️ Iltimos, xabarlarni tez-tez yubormang!")
                return None

        self.last_requests[user_id] = current_time
        return await handler(event, data)


# ============================================================
# BAN CHECK MIDDLEWARE
# ============================================================
class BanCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id
        
        # Adminlarni bloklamaymiz
        from utils import is_admin
        if await is_admin(user_id):
            return await handler(event, data)

        if await is_user_banned(user_id):
            await event.answer(
                "🚫 <b>Siz bloklandingiz!</b>\n\n"
                "Qoidalarni buzganingiz uchun botdan foydalanish huquqingiz cheklangan.",
                parse_mode="HTML"
            )
            return None

        return await handler(event, data)
