# 🚀 Telegram Bot Deployment Checklist

## 📋 Deploymentdan Oldin

### Environment Variables
- [ ] `BOT_TOKEN` - to'g'ri token
- [ ] `ADMIN_IDS` - admin ID'lari (vergul bilan ajratilgan)
- [ ] `CHANNEL_ID` - kanal ID (manfiy bilan boshlanadi)
- [ ] `CHANNEL_USERNAME` - kanal username (@ bilan boshlanadi)
- [ ] `DB_PATH` - `/data/bot_database.db`
- [ ] `OTZIV_GROUP_ID` - guruh ID (agar kerak bo'lsa)
- [ ] `POINTS_PER_REFERRAL` - default: 50
- [ ] `MIN_POINTS_FOR_ORDER` - default: 100

### Railway Volume
- [ ] Volume yaratilgan
- [ ] Mount Path: `/data`
- [ ] Service ga ulangan

### Kod Tekshirish
- [ ] Barcha importlar fayl boshida
- [ ] Inline importlar yo'q
- [ ] Logger to'g'ri sozlangan
- [ ] Handlerlar tartibi to'g'ri (user birinchi, admin keyin)
- [ ] Button textlar mos
- [ ] Constants faylda textlar saqlangan

### Local Test
- [ ] Localda bot ishlayapti
- [ ] `/start` command ishlayapti
- [ ] Database ishlayapti
- [ ] Barcha handlerlar ishlayapti
- [ ] Xatoliklar yo'q

### Local Cleanup
- [ ] Barcha Python jarayonlari o'ldirilgan
- [ ] Webhook tozalgan
- [ ] Git commit qilingan
- [ ] Git push qilingan

---

## 📋 Deploymentdan Keyin

### Log Tekshirish
- [ ] `🤖 Bot ishga tushdi` xabari bor
- [ ] `📥 /start qabul qilindi` xabari bor
- [ ] `ModuleNotFoundError` yo'q
- [ ] `ImportError` yo'q
- [ ] `Permission denied` yo'q
- [ ] `ConflictError` yo'q

### Functional Test
- [ ] `/start` command test qilingan
- [ ] Bot javob beradi
- [ ] Menyu tugmalari ishlayapti
- [ ] Database ma'lumotlar saqlanadi
- [ ] Admin handlerlar ishlayapti

### Railway Status
- [ ] Deploy status: `Succeeded`
- [ ] Service status: `Running`
- [ ] CPU/Memory normal
- [ ] No errors in logs

---

## 🚨 Xatoliklar va Yechimlar

### ConflictError
**Sabab:** Ko'p bot instance ishlayapti
**Yechim:** Local jarayonlarni o'ldirish, webhook tozalash

### ModuleNotFoundError
**Sabab:** Import qilinmagan modul
**Yechim:** Importlarni tekshirish, fayllar borligini tekshirish

### Database Error
**Sabab:** Volume o'rnatilmagan
**Yechim:** Volume qo'shish, DB_PATH o'rnatish

### Bot Javob Bermaydi
**Sabab:** Handler ishga tushmayapti
**Yechim:** Handlerlar tartibini tekshirish, loglarni ko'rish

---

## 📝 Tezkor Scriptlar

### Localda:
```bash
# Webhook tozalash
python scripts/clear_webhook.py

# Database tekshirish
python scripts/check_database.py

# Connection test
python scripts/check_webhook.py
```

### Railway'da:
- Redeploy tugmasi
- Loglarni kuzatish
- Variables tekshirish

---

## 🎯 Muvaffaqiyatli Deployment

Agar barcha punktlar to'liq bo'lsa:
- ✅ Bot ishlayapti
- ✅ Xatoliklar yo'q
- ✅ Foydalanuvchilar foydalanishi mumkin

**Deployment muvaffaqiyatli!** 🎊
