# TeleBot Wizard 🧙

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![PyPI Version](https://img.shields.io/badge/pypi-v1.0.0-orange.svg) ![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

**Zero-Code Telegram Bot Builder** - pyTelegramBotAPI uchun professional kutubxona

## 📖 Tavsif

TeleBot Wizard - bu foydalanuvchilarga hech qanday kod yozmasdan professional Telegram botlar yaratish imkonini beruvchi qulay kutubxona. pyTelegramBotAPI asosida qurilgan bu vosita bot yaratish jarayonini soddalashtiradi va tezlashtiradi.

### ✨ Asosiy imkoniyatlar

- 🎯 **Zero-Code**: Hech qanday kod yozish shart emas
- 🔄 **Multi-Menu**: Ko'plab menular bilan ishlash
- ⚡ **Dual Mode**: Reply va Run rejimlari
- 🛡️ **Xavfsizlik**: To'liq xatolik tekshirish
- 📝 **Auto-Documentation**: Avtomatik hujjatlashtirish
- 🔧 **Extensible**: Oson kengaytirish imkoniyati

## 🚀 Tez boshlash

### O'rnatish

```bash
# PyPI dan o'rnatish
pip install telebot-wizard
```

### Ishga tushirish

```python
from telebot_wizard import BotWizard
# Bot yaratish
w = BotWizard("SIZNING_BOT_TOKEN")
# Menu yaratish
w.menu("Asosiy")
w.button("Salom", reply="Xush kelibsiz!")
w.button("Hisob", run="2 + 2")
# Kod generatsiya qilish
w.generate("mening_bot.py")
```

## 📚 Batafsil qo'llanma

### 1. Asosiy foydalanish

```python
from telebot_wizard import BotWizard
# Bot obyektini yaratish
w = BotWizard("1234567890:ABCdefGHIjklMNOpqrSTUVWxyz")
# Asosiy menu
w.menu("Asosiy")
w.button("Start", reply="Botga xush kelibsiz!")
w.button("Info", reply="Bu bot TeleBot Wizard yordamida qurilgan!")
# Matematik menu
w.menu("Matematik")
w.button("Qo'shish", run="15 + 25")
w.button("Ko'paytirish", run="7 * 8")
w.button("Vaqt", run="import datetime; datetime.datetime.now().strftime('%H:%M')")
# Kod generatsiya
w.generate("mybot.py")
```

### 2. Reply va Run rejimlari

**Reply Rejimi** - Oddiy matn qaytaradi:
```python
w.button("Salomlashish", reply="Salom! Bugun qalaysiz?")
```

**Run Rejimi** - Python kodini bajaradi:
```python
w.button("Hisoblash", run="2 + 2 * 3")  # 8 qaytaradi
w.button("Tarix", run="import datetime; return datetime.date.today()")
w.button("Random", run="import random; random.randint(1, 10)")
```

### 3. Multi-Menu tizimi

```python
# Asosiy menu
w.menu("Asosiy")
w.button("Boshqa Menu", reply="Boshqa menu ochildi!")
# Admin menu
w.menu("Admin")
w.button("Panel", reply="Admin paneliga xush kelibsiz!")
w.button("Foydalanuvchilar", run="f'Jami foydalanuvchilar: {12345}'")
# Matematik menu
w.menu("Matematik")
w.button("Algebra", run="x = 5; x * 2 + 3")
```

## 🛠️ Imkoniyatlar

### BotConnection Test qilish
```python
w = BotWizard("YOUR_TOKEN")
if w.test_connection():
    print("✅ Bot tokeni to'g'ri!")
else:
    print("❌ Bot tokeni noto'g'ri!")
```

### Konfiguratsiya ko'rsatish
```python
print(w.get_menus_summary())
# Natija:
# BotWizard konfiguratsiyasi:
# Token: 1234567890...
# Menus: 3
#   - Asosiy: 2 tugma
#   - Admin: 2 tugma
#   - Matematik: 3 tugma
```

### Konfiguratsiyani eksport qilish
```python
w.export_config("bot_config.json")  # JSON fayliga saqlash
```

### Tekshirish
```python
validation = w.validate_configuration()
print(validation)
# {'token_valid': True, 'menus_exist': True, ...}
```

## 📦 Paket ma'lumotlari

### Requirements
- Python 3.8+
- pyTelegramBotAPI >= 4.0.0

## 🔧 CLI Tool

```bash
# CLI orqali foydalanish
telebot-wizard --help
```

## 📄 Foydalanish misollari

### Oddiy Salamlashish Bot
```python
from telebot_wizard import BotWizard
w = BotWizard("YOUR_TOKEN")
w.menu("Asosiy")
w.button("Salom", reply="Assalomu alaykum!")
w.button("Xayr", reply="Xayr! Botni yana ishlatish uchun /start bosing.")
w.generate("salom_bot.py")
```

### Matematik Hisoblash Bot
```python
from telebot_wizard import BotWizard
w = BotWizard("YOUR_TOKEN")
w.menu("Hisoblash")
w.button("2+2", run="2 + 2")
w.button("5*7", run="5 * 7")
w.button("10^2", run="10 ** 2")
w.button("sqrt(16)", run="import math; math.sqrt(16)")
w.generate("math_bot.py")
```

### Info Bot
```python
from telebot_wizard import BotWizard

w = BotWizard("YOUR_TOKEN")
w.menu("Ma'lumot")
w.button("Vaqt", run="import datetime; datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')")
w.button("Sana", run="import datetime; datetime.date.today()")
w.button("Python Version", run="import sys; sys.version.split()[0]")
w.button("Bot Haqida", reply="Bu bot TeleBot Wizard yordamida yaratilgan!")
w.generate("info_bot.py")
```

## 🐛 Xatoliklarni hal qilish

### Keng tarqalgan muammolar

**1. Token xatoligi**
```python
# ❌ Noto'g'ri
w = BotWizard("wrong_token")
# ✅ To'g'ri
w = BotWizard("1234567890:ABCdefGHIjklMNOpqrSTUVWxyz")
```

**2. Menu ochilmagan tugma**
```python
# ❌ Xatolik
w.button("Test", reply="Hello")  # menu() chaqirilmagan

# ✅ To'g'ri
w.menu("Test Menu")
w.button("Test", reply="Hello")
```

**3. Tugma nomlari takrorlanishi**
```python
# ❌ Xatolik
w.menu("Main")
w.button("Hello", reply="First")
w.button("Hello", reply="Second")  # Takrorlanuvchi nom

# ✅ To'g'ri
w.menu("Main")
w.button("Hello", reply="First")
w.button("Goodbye", reply="Second")
```

## 📈 Performance

TeleBot Wizard quyidagi jihatlarda optimallashtirilgan:
- Tez kod generatsiya (1-2 soniya)
- Minimal xotira iste'moli
- Parallel menu ishlab chiqarish
- Optimallashtirilgan handler generatsiya

## 🔒 Xavfsizlik

- **Input Validation**: Barcha inputlarni tekshirish
- **Code Injection**: Safe eval() funksiya
- **Error Handling**: Professional xatolik hal qilish
- **Logging**: To'liq log yaratish

## 📄 LICENSE

Bu loyiha MIT License ostida tarqatiladi. Batafsil ma'lumot uchun [LICENSE](LICENSE) faylini ko'ring.

## 🆘 Yordam va qo'llab-quvvatlash

- **Issues**: [Telegram](https://t.me/UzMaxBoy)
- **Discussions**: [Telegram](https://t.me/UzMaxBoy)
- **Email**: rakuzenuz@gmail.com

## 🙏 Rahmat

- pyTelegramBotAPI jamoasi
- Python community
- Test qilgan barcha foydalanuvchilar

---

**TeleBot Wizard** - Telegram bot yaratishni soddalashtirish uchun! 🧙✨