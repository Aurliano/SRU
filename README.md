# 🤖 ربات آموزش زبان انگلیسی

یک ربات تلگرام هوشمند برای آموزش زبان انگلیسی با استفاده از هوش مصنوعی

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-green.svg)](https://openai.com)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://sqlite.org)

---

## 🎯 ویژگی‌های کلیدی

✅ **آزمون تعیین سطح هوشمند** - تشخیص دقیق سطح زبان کاربر  
✅ **تمرین واژگان تعاملی** - یادگیری لغات با جمله‌سازی  
✅ **دروس گرامر عملی** - 20 درس کامل در 4 سطح  
✅ **تمرین مکالمه با AI** - گفتگو طبیعی با ربات هوشمند  
✅ **پیگیری پیشرفت** - ردیابی دقیق پیشرفت یادگیری  
✅ **سیستم امتیازدهی** - ارزیابی هوشمند توسط OpenAI  

---

## 🏗️ معماری سیستم

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │────│   Main Bot Logic │────│   OpenAI API    │
│   (Interface)   │    │   (bot.py)       │    │   (AI Engine)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │
         │                        │
┌─────────────────┐    ┌──────────────────┐
│   User Data     │────│  Content Manager │
│   (user_db.py)  │    │ (content_mgr.py) │
└─────────────────┘    └──────────────────┘
         │                        │
         │                        │
┌─────────────────┐    ┌──────────────────┐
│   user_data.db  │    │  content_data.db │
│   (SQLite)      │    │   (SQLite)       │
└─────────────────┘    └──────────────────┘
```

---

## 🚀 راه‌اندازی سریع

### پیش‌نیازها

- Python 3.9+
- Telegram Bot Token ([از BotFather](https://t.me/botfather))
- OpenAI API Key ([از OpenAI Platform](https://platform.openai.com))

### نصب

```bash
# 1. کلون کردن پروژه
git clone https://github.com/your-repo/english-learning-bot.git
cd english-learning-bot

# 2. نصب وابستگی‌ها
pip install -r requirements.txt

# 3. تنظیم متغیرهای محیطی
cp .env.example .env
# ویرایش .env و افزودن Token ها

# 4. اجرای ربات
python bot.py
```

### تنظیم .env

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📚 مستندات

| مستند | توضیحات |
|--------|----------|
| [📖 راهنمای کامل پروژه](PROJECT_DOCUMENTATION.md) | مستندات کامل سیستم و اهداف |
| [🔧 راهنمای فنی](TECHNICAL_GUIDE.md) | جزئیات فنی و معماری |
| [📡 مرجع API](API_REFERENCE.md) | مستندات کامل API ها |
| [🚀 راهنمای استقرار](DEPLOYMENT_GUIDE.md) | نحوه نصب و استقرار در محیط‌های مختلف |
| [📱 راهنمای کاربری](USER_MANUAL.md) | راهنمای استفاده برای کاربران نهایی |

---

## 🎮 نحوه استفاده

### برای کاربران

1. **شروع:** پیام `/start` به ربات ارسال کنید
2. **آزمون سطح:** آزمون 20 سوالی تعیین سطح انجام دهید
3. **انتخاب تمرین:** از میان واژگان، گرامر یا مکالمه انتخاب کنید
4. **پیگیری پیشرفت:** از منوی "پیشرفت من" استفاده کنید

### برای توسعه‌دهندگان

```python
from user_db import UserDatabase
from content_manager import ContentManager

# مدیریت کاربران
db = UserDatabase()
user_level = db.get_user_level(user_id)

# مدیریت محتوا
content = ContentManager()
words = content.get_vocabulary_for_level("beginner", 5)
```

---

## 📊 آمار پروژه

- **📝 خطوط کد:** 2000+ خط Python
- **📚 واژگان:** 40+ واژه در 4 سطح
- **📖 دروس گرامر:** 20 درس کامل
- **🗣️ موضوعات مکالمه:** 20 موضوع متنوع
- **🧪 سوالات آزمون:** 20+ سوال چندگزینه‌ای

---

## 🔧 اجزای اصلی

### ماژول‌های کلیدی

| فایل | مسئولیت |
|------|---------|
| `bot.py` | منطق اصلی ربات و مدیریت تعاملات |
| `user_db.py` | مدیریت پایگاه داده کاربران |
| `content_manager.py` | مدیریت محتوای آموزشی |

### پایگاه داده

| جدول | هدف |
|------|------|
| `users` | اطلاعات کاربران |
| `progress` | پیشرفت یادگیری |
| `vocabulary` | واژگان تمرین شده |
| `user_grammar` | دروس گرامر تکمیل شده |

---

## 🎯 ویژگی‌های آموزشی

### سطوح پشتیبانی شده

🔰 **مبتدی (Beginner)**
- واژگان پایه
- گرامر ابتدایی (Simple Present, Past)
- مکالمات ساده

⭐ **آماتور (Amateur)**  
- واژگان متوسط
- گرامر میانی (Present Perfect, Modals)
- مکالمات شخصی

🌟 **متوسط (Intermediate)**
- واژگان پیشرفته
- گرامر پیچیده (Conditionals, Passive)
- مکالمات موضوعی

🏆 **پیشرفته (Advanced)**
- واژگان تخصصی
- گرامر پیشرفته (Inversion, Cleft)
- مکالمات تحلیلی

### سیستم امتیازدهی

- **واژگان:** کاربرد صحیح (50%) + گرامر (30%) + خلاقیت (20%)
- **گرامر:** کاربرد قاعده (60%) + صحت گرامری (30%) + طبیعی بودن (10%)
- **مکالمه:** گرامر (40%) + واژگان (30%) + ارتباط (20%) + روانی (10%)

---

## 🧪 تست و کیفیت

### تست عملکرد

```bash
# تست اتصال OpenAI
python -c "from openai import OpenAI; print('OpenAI OK')"

# تست پایگاه داده
python -c "from user_db import UserDatabase; print('Database OK')"

# تولید داده‌های تست
python simple_dataset.py
```

### Quality Assurance

- ✅ **تست واحد:** تست تمام توابع کلیدی
- ✅ **تست یکپارچگی:** تست ارتباط بین ماژول‌ها
- ✅ **تست کاربری:** تست flow کامل آموزش
- ✅ **تست عملکرد:** بررسی سرعت و کارایی

---

## 🔧 ویژگی‌های فنی

### بهینه‌سازی

- **Database Connection Pooling** برای عملکرد بهتر
- **LRU Cache** برای محتوای ثابت
- **Async Operations** برای API calls
- **Error Handling** جامع

### امنیت

- **Environment Variables** برای Token ها
- **Input Sanitization** برای ورودی کاربران
- **Rate Limiting** برای جلوگیری از سوء استفاده
- **SQL Injection Prevention** با Prepared Statements

### Monitoring

- **Comprehensive Logging** با rotation
- **Health Checks** خودکار
- **Performance Metrics** 
- **Error Tracking** و alerting

---

## 🌟 ویژگی‌های اضافی

> **نکته:** بخش‌های زیر به عنوان ویژگی‌های اضافی پیاده‌سازی شده‌اند و در اهداف اصلی پروژه قرار نداشتند.

### Admin Panel (اختیاری)
- 🖥️ رابط وب برای مدیریت
- 📊 داشبورد آماری
- 📈 نمودارهای پیشرفت

```bash
# راه‌اندازی Admin Panel
pip install -r admin_requirements.txt
python admin_panel.py
# دسترسی: http://localhost:5000
```

### Analytics Engine (اختیاری)
- 📊 تحلیل رفتار کاربران
- 📈 گزارش‌های عملکرد
- 🔍 آمار استفاده

```bash
# اجرای Analytics
python analytics_engine.py
```

---

## 🤝 مشارکت

### نحوه مشارکت

1. **Fork** کردن پروژه
2. **Clone** کردن fork شما
3. ایجاد **branch** جدید
4. انجام تغییرات
5. **Commit** و **Push**
6. ارسال **Pull Request**

### استانداردهای کد

- **PEP 8** برای Python
- **Type Hints** برای توابع مهم
- **Docstrings** برای کلاس‌ها و توابع
- **Error Handling** مناسب

### گزارش باگ

برای گزارش باگ، لطفاً اطلاعات زیر را ارائه دهید:

- **نسخه Python**
- **سیستم‌عامل** 
- **مراحل بازتولید** باگ
- **پیام‌های خطا**
- **لاگ‌های مربوطه**

---

## 📄 مجوز

این پروژه تحت مجوز **Academic Use** منتشر شده است.

### شرایط استفاده

- ✅ **استفاده آموزشی:** برای یادگیری و تحقیق
- ✅ **تغییر و توسعه:** اصلاح و بهبود کد
- ❌ **استفاده تجاری:** بدون مجوز صاحب پروژه

---

## 🙏 تشکر و قدردانی

### کتابخانه‌های استفاده شده

- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/) - فریم‌ورک ربات تلگرام
- [OpenAI Python](https://github.com/openai/openai-python) - کتابخانه OpenAI
- [SQLite](https://sqlite.org/) - پایگاه داده embedded

### منابع الهام

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [English Learning Resources](https://www.cambridge.org/elt/)

---

## 📞 ارتباط و پشتیبانی

### اطلاعات پروژه

- **نسخه:** 1.0.0
- **وضعیت:** Production Ready
- **نگهدارنده:** توسعه‌دهنده پروژه
- **زبان:** Python 3.9+

### راه‌های ارتباط

- **GitHub Issues:** برای باگ‌ها و درخواست‌های ویژگی
- **Email:** برای سؤالات عمومی
- **Documentation:** برای راهنمای تفصیلی

---

## 🗺️ نقشه راه توسعه

### نسخه‌های آینده

#### v1.1 (پیشنهادی)
- 🎯 گیمیفیکیشن (Badge ها و Achievement ها)
- 🔊 پشتیبانی از Voice Messages
- 📱 Progressive Web App

#### v1.2 (پیشنهادی)  
- 🤖 بهبود AI با Fine-tuning
- 🌍 پشتیبانی چندزبانه
- 👥 ویژگی‌های اجتماعی (Group Classes)

#### v2.0 (آینده)
- 📊 Machine Learning برای شخصی‌سازی
- 🎬 یکپارچگی با محتوای multimedia
- 🏆 سیستم رقابت و مسابقه

---

**🚀 آماده برای شروع یادگیری زبان انگلیسی با هوش مصنوعی!**

---
*ساخته شده با ❤️ برای یادگیرندگان زبان انگلیسی*