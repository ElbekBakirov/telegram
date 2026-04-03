# 🚀 Free Fire Botni Railway'ga Joylashtirish Qo'llanmasi

Botning ma'lumotlar bazasi o'chib ketmasligi va doimiy ishlashini ta'minlash uchun quyidagi amallarni bajaring.

## 1. Railway Loyihasini Yaratish
1. [Railway.app](https://railway.app/) saytiga kiring.
2. **New Project** tugmasini bosing va **Deploy from GitHub** ni tanlang.
3. Bot kodi yuklangan GitHub repozitoriyni tanlang.

## 2. Doimiy Xotira Qo'shish (CRITICAL - JUDA MUHIM)
Railway fayl tizimi vaqtinchalik. Foydalanuvchilar ma'lumotlarini saqlab qolish uchun albatta "Volume" qo'shishingiz shart.
1. Railway loyihangizda **+ New** -> **Volume** tugmasini bosing.
2. Unga nom bering (masalan: `bot_data`).
3. **Bot Service** (bot xizmati) -> **Settings** -> **Volumes** bo'limiga kiring.
4. **Mount Volume** tugmasini bosing.
5. **Mount Path** qatoriga `/data` deb yozing.

## 3. Muhit O'zgaruvchilarini (Variables) Sozlash
Bot xizmati ichidagi **Variables** bo'limiga kiring va quyidagilarni qo'shing:
- `BOT_TOKEN`: @BotFather dan olingan bot tokeni.
- `ADMIN_IDS`: Sizning Telegram ID raqamingiz (va boshqalar, vergul bilan).
- `DB_PATH`: `/data/bot_database.db` (Bu bazani doimiy xotiraga yo'naltiradi).
- `CHANNEL_ID`: Majburiy a'zolik kanali ID raqami.
- `CHANNEL_USERNAME`: Kanal username ( @ bilan).
- `OTZIV_GROUP_ID`: Fikr-mulohazalar guruhi ID raqami.

## 4. Ishga Tushirish (Deploy)
Railway botni avtomatik ravishda quradi va ishga tushiradi.
Holat (Status) "Active" bo'lganda, botingiz tayyor bo'ladi!

---

## 🤝 Botni Yangi Egaga Topshirish
Botni boshqa odamga o'tkazmoqchi bo'lsangiz:
1. **GitHub**: Uni GitHub repozitoriyingizga hamkor (collaborator) sifatida qo'shing.
2. **Railway**: U o'zining Railway hisobida sizning kodingizdan yangi loyiha yaratishi mumkin yoki siz uni o'z loyihangizga qo'shishingiz mumkin.
3. **O'zgaruvchilar (Variables)**: Yangi ega Railway panelida `BOT_TOKEN` va `ADMIN_IDS` ga o'z ma'lumotlarini yozishi SHART.
4. **Migratsiya**: Bot ichida `🔑 Adminni ko'chirish` buyrug'ini ishlatib, barcha foydalanuvchilarning yangi egaga va yangi kanalga o'tishini ta'minlang.
