# 🤖 AioTeleBot

Telegram bot yaratish uchun **eng oson** va **o'zbekcha** kutubxona! Aiogram 3 asosida qurilgan.

## ✨ Xususiyatlari

- 🇺🇿 **To'liq o'zbekcha** dokumentatsiya va metodlar
- 🚀 **Juda oson** - kamroq kod, ko'proq natija
- 🎯 **Sodda sintaksis** - 5 daqiqada bot yasang
- 📦 **Barcha imkoniyatlar** - state, tugmalar, media va h.k.
- 🔧 **Aiogram 3** asosida ishlab chiqilgan

## 📥 O'rnatish
```bash
pip install aiotelebot
```

## 🚀 Tezkor Boshlash

### Oddiy bot
```python
from aiotelebot import OsonBot

# Bot yaratish
bot = OsonBot("SIZNING_TOKEN")

# /start komandasi
@bot.xabar("/start")
async def start(xabar):
    await bot.yuborish(xabar, "🎉 Salom! Men oddiy botman.")

# /help komandasi
@bot.xabar("/help")
async def yordam(xabar):
    await bot.yuborish(xabar, "📚 Yordam bo'limi")

# Botni ishga tushirish
bot.ishga_tushirish()
```

### Tugmalar bilan
```python
from aiotelebot import OsonBot, Tugma

bot = OsonBot("TOKEN")

@bot.xabar("/menu")
async def menu(xabar):
    # Oddiy tugmalar
    tugma = Tugma()
    tugma.qator(["📊 Statistika", "⚙️ Sozlamalar"])
    tugma.qator(["❓ Yordam"])
    
    await bot.yuborish(xabar, "Menyuni tanlang:", tugma)

bot.ishga_tushirish()
```

### Inline tugmalar
```python
from aiotelebot import OsonBot, InlineTugma

bot = OsonBot("TOKEN")

@bot.xabar("/taklif")
async def taklif(xabar):
    # Inline tugmalar
    tugma = InlineTugma()
    tugma.qator([
        ("✅ Tasdiq", "tasdiq"),
        ("❌ Rad etish", "rad")
    ])
    tugma.url("🌐 Sayt", "https://example.com")
    
    await bot.yuborish(xabar, "Taklifni qabul qilasizmi?", tugma)

# Inline tugma bosilganda
@bot.callback("tasdiq")
async def tasdiq_handler(callback):
    await bot.javob_berish(callback, "✅ Tasdiqlanddi!")
    await bot.tahrirlash(callback, "Taklif qabul qilindi ✅")

bot.ishga_tushirish()
```

### Holatlar bilan ishlash (State)
```python
from aiotelebot import OsonBot, HolatGuruhi, Holat

bot = OsonBot("TOKEN")

# Holatlarni yaratish
class Royxat(HolatGuruhi):
    ism = Holat()
    yosh = Holat()
    telefon = Holat()

@bot.xabar("/royxat")
async def royxat_boshlash(xabar):
    await bot.holat_ozgartirish(xabar, Royxat.ism)
    await bot.yuborish(xabar, "Ismingizni kiriting:")

@bot.xabar(holat=Royxat.ism)
async def ism_qabul(xabar):
    await bot.malumot_saqlash(xabar, "ism", xabar.text)
    await bot.holat_ozgartirish(xabar, Royxat.yosh)
    await bot.yuborish(xabar, "Yoshingizni kiriting:")

@bot.xabar(holat=Royxat.yosh)
async def yosh_qabul(xabar):
    await bot.malumot_saqlash(xabar, "yosh", xabar.text)
    await bot.holat_ozgartirish(xabar, Royxat.telefon)
    
    tugma = Tugma()
    tugma.kontakt("📱 Telefon raqamni yuborish")
    
    await bot.yuborish(xabar, "Telefon raqamingizni yuboring:", tugma)

@bot.xabar(holat=Royxat.telefon)
async def telefon_qabul(xabar):
    # Barcha ma'lumotlarni olish
    malumot = await bot.malumot_olish(xabar)
    
    await bot.holat_tozalash(xabar)
    await bot.yuborish(
        xabar,
        f"✅ Ro'yxatdan o'tdingiz!\n\n"
        f"👤 Ism: {malumot['ism']}\n"
        f"🎂 Yosh: {malumot['yosh']}\n"
        f"📱 Telefon: {xabar.contact.phone_number}"
    )

bot.ishga_tushirish()
```

### Media yuborish
```python
from aiotelebot import OsonBot, Media

bot = OsonBot("TOKEN")

@bot.xabar("/rasm")
async def rasm_yuborish(xabar):
    # Fayldan
    await bot.rasm_yuborish(
        xabar,
        Media.fayldan("rasm.jpg"),
        izoh="Bu rasm"
    )
    
    # URL dan
    await bot.rasm_yuborish(
        xabar,
        Media.urldan("https://example.com/rasm.jpg"),
        izoh="URL dan rasm"
    )

@bot.xabar("/video")
async def video_yuborish(xabar):
    await bot.video_yuborish(
        xabar,
        Media.fayldan("video.mp4"),
        izoh="Video fayl"
    )

@bot.xabar("/fayl")
async def fayl_yuborish(xabar):
    await bot.fayl_yuborish(
        xabar,
        Media.fayldan("dokument.pdf"),
        izoh="PDF fayl"
    )

bot.ishga_tushirish()
```

## 📖 To'liq Misol
```python
from aiotelebot import OsonBot, Tugma, InlineTugma, HolatGuruhi, Holat, Media

# Bot yaratish
bot = OsonBot("SIZNING_TOKEN", log_darajasi="INFO")

# Holatlar
class Savol(HolatGuruhi):
    javob_kutish = Holat()

# Start komandasi
@bot.xabar("/start")
async def start(xabar):
    tugma = Tugma()
    tugma.qator(["📊 Statistika", "❓ Savol"])
    tugma.qator(["⚙️ Sozlamalar"])
    
    await bot.yuborish(
        xabar,
        f"Salom, {xabar.from_user.first_name}! 👋\n"
        f"Men yordamchi botman.",
        tugma
    )

# Statistika
@bot.xabar(matn="📊 Statistika")
async def statistika(xabar):
    inline = InlineTugma()
    inline.qator([
        ("📈 Bugun", "stat_bugun"),
        ("📅 Hafta", "stat_hafta")
    ])
    inline.qator([("🔙 Orqaga", "orqaga")])
    
    await bot.yuborish(xabar, "📊 Statistika bo'limi:", inline)

# Savol boshlash
@bot.xabar(matn="❓ Savol")
async def savol_boshlash(xabar):
    await bot.holat_ozgartirish(xabar, Savol.javob_kutish)
    await bot.yuborish(xabar, "Savolingizni yozing:")

# Savolga javob
@bot.xabar(holat=Savol.javob_kutish)
async def savol_javob(xabar):
    await bot.holat_tozalash(xabar)
    await bot.yuborish(xabar, f"Sizning savolingiz: {xabar.text}\n\nTez orada javob beramiz!")

# Callback handlerlar
@bot.callback("stat_bugun")
async def stat_bugun(callback):
    await bot.javob_berish(callback, "Bugungi statistika")

@bot.callback("orqaga")
async def orqaga(callback):
    tugma = Tugma()
    tugma.qator(["📊 Statistika", "❓ Savol"])
    
    await bot.tahrirlash(callback, "Bosh menyu", tugma)

# Har qanday xabar
@bot.har_qanday_xabar()
async def boshqa(xabar):
    print(f"Noma'lum xabar: {xabar.text}")

# Botni ishga tushirish
if __name__ == "__main__":
    bot.ishga_tushirish()
```

## 🎯 Asosiy Metodlar

### Bot Metodlari

| Metod | Tavsif |
|-------|--------|
| `yuborish()` | Xabar yuborish |
| `tahrirlash()` | Xabarni tahrirlash |
| `javob_berish()` | Callback ga javob |
| `rasm_yuborish()` | Rasm yuborish |
| `video_yuborish()` | Video yuborish |
| `fayl_yuborish()` | Fayl yuborish |
| `holat_ozgartirish()` | Holatni o'zgartirish |
| `malumot_saqlash()` | Ma'lumot saqlash |
| `malumot_olish()` | Ma'lumot olish |

### Dekoratorlar

| Dekorator | Tavsif |
|-----------|--------|
| `@bot.xabar()` | Xabar handler |
| `@bot.callback()` | Inline tugma handler |
| `@bot.har_qanday_xabar()` | Barcha xabarlar |

## 📝 Litsenziya

MIT License

## 🤝 Hissa qo'shish

Pull requestlar xush kelibsiz!

## 📞 Aloqa

Savollar bo'lsa, issue oching!