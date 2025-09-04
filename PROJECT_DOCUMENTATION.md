# 📚 مستندات سیستم ربات آموزش زبان انگلیسی

## 📋 فهرست مطالب

1. [مقدمه و اهداف](#مقدمه-و-اهداف)
2. [معماری سیستم](#معماری-سیستم)
3. [ماژول‌های اصلی](#ماژولهای-اصلی)
4. [پایگاه داده](#پایگاه-داده)
5. [API و یکپارچه‌سازی](#api-و-یکپارچهسازی)
6. [راهنمای نصب و راه‌اندازی](#راهنمای-نصب-و-راهاندازی)
7. [راهنمای استفاده](#راهنمای-استفاده)
8. [تست و ارزیابی](#تست-و-ارزیابی)
9. [نکات امنیتی](#نکات-امنیتی)
10. [ضمائم](#ضمائم)

---

## 🎯 مقدمه و اهداف

### هدف پروژه
این پروژه یک ربات تلگرام هوشمند برای آموزش زبان انگلیسی است که با استفاده از هوش مصنوعی، تجربه یادگیری شخصی‌سازی شده ارائه می‌دهد.

### اهداف اصلی
- **آموزش تعاملی:** ارائه محتوای آموزشی تعاملی در سه بخش واژگان، گرامر و مکالمه
- **ارزیابی هوشمند:** استفاده از AI برای ارزیابی پاسخ‌های کاربران
- **تعیین سطح:** آزمون خودکار تعیین سطح زبان کاربران
- **پیگیری پیشرفت:** ردیابی و گزارش پیشرفت یادگیری
- **قابلیت مقیاس‌پذیری:** طراحی برای پشتیبانی از تعداد زیاد کاربر

### ویژگی‌های کلیدی
- ✅ آزمون تعیین سطح خودکار
- ✅ آموزش واژگان با تمرین جمله‌سازی
- ✅ دروس گرامر تعاملی با تمرین‌های عملی
- ✅ تمرین مکالمه با AI
- ✅ ردیابی پیشرفت شخصی
- ✅ سیستم امتیازدهی هوشمند
- ✅ پشتیبانی از چهار سطح: مبتدی، آماتور، متوسط، پیشرفته

---

## 🏗️ معماری سیستم

### نمای کلی معماری

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

### اجزای اصلی سیستم

1. **رابط کاربری (Telegram Interface)**
   - دریافت پیام‌های کاربران
   - ارسال پاسخ‌ها و محتوای آموزشی
   - مدیریت inline keyboard ها

2. **منطق اصلی ربات (Bot Logic)**
   - مدیریت state کاربران
   - پردازش دستورات و پیام‌ها
   - هماهنگی بین ماژول‌های مختلف

3. **موتور هوش مصنوعی (AI Engine)**
   - ارزیابی پاسخ‌های کاربران
   - تولید بازخورد آموزشی
   - امتیازدهی خودکار

4. **مدیریت داده‌های کاربر (User Management)**
   - ثبت و پیگیری کاربران
   - ذخیره پیشرفت یادگیری
   - مدیریت سطح کاربران

5. **مدیریت محتوا (Content Management)**
   - ارائه واژگان و دروس گرامر
   - سوالات آزمون تعیین سطح
   - مباحث تمرین مکالمه

---

## 🔧 ماژول‌های اصلی

### 1. ماژول اصلی ربات (`bot.py`)

```python
# مسئولیت‌های کلیدی:
- مدیریت conversation states
- پردازش command ها و message ها
- یکپارچه‌سازی با OpenAI API
- مدیریت flow آموزشی
```

**عملکردهای اصلی:**
- `start()`: راه‌اندازی ربات و ثبت کاربر
- `assess_level()`: آزمون تعیین سطح
- `vocabulary_practice()`: تمرین واژگان
- `grammar_lesson()`: دروس گرامر
- `conversation_practice()`: تمرین مکالمه
- `show_progress()`: نمایش پیشرفت

### 2. مدیریت کاربران (`user_db.py`)

```python
# کلاس UserDatabase:
- register_user(): ثبت کاربر جدید
- get_user_level(): دریافت سطح کاربر
- update_user_level(): به‌روزرسانی سطح
- add_progress(): ثبت پیشرفت
- get_user_progress(): دریافت پیشرفت کامل
```

**ویژگی‌های کلیدی:**
- ردیابی پیشرفت تدریجی در هر بخش
- سیستم ارتقاء خودکار سطح
- ذخیره تاریخچه تمرین‌ها
- پشتیبانی از چندین کاربر همزمان

### 3. مدیریت محتوا (`content_manager.py`)

```python
# کلاس ContentManager:
- get_vocabulary_for_level(): واژگان بر اساس سطح
- get_grammar_lesson_for_level(): دروس گرامر
- get_mixed_assessment_questions(): سوالات آزمون
- mark_grammar_lesson_completed(): ثبت تکمیل درس
```

**محتوای آموزشی:**
- 🔤 **واژگان:** بیش از 40 واژه در 4 سطح
- 📝 **گرامر:** 20 درس کامل (5 درس در هر سطح)
- 🗣️ **مکالمه:** 20 موضوع تمرین مکالمه
- 🧪 **آزمون:** 20+ سوال تعیین سطح

---

## 🗄️ پایگاه داده

### ساختار پایگاه داده

#### دیتابیس کاربران (`user_data.db`)

**جدول users:**
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level TEXT DEFAULT 'beginner',
    join_date TEXT,
    last_active TEXT,
    assessment_done BOOLEAN DEFAULT FALSE
);
```

**جدول progress:**
```sql
CREATE TABLE progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    section TEXT,      -- vocabulary, grammar, conversation, assessment
    level TEXT,
    score REAL,
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**جدول vocabulary:**
```sql
CREATE TABLE vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    word TEXT,
    score INTEGER,
    last_practiced TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**جدول user_grammar:**
```sql
CREATE TABLE user_grammar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    level TEXT,
    topic_id INTEGER,
    score INTEGER,
    completed_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### دیتابیس محتوا (`content_data.db`)

**جدول vocabulary_words:**
```sql
CREATE TABLE vocabulary_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT,
    definition TEXT,
    example TEXT,
    level TEXT
);
```

**جدول grammar_lessons:**
```sql
CREATE TABLE grammar_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    level TEXT
);
```

**جدول assessment_questions:**
```sql
CREATE TABLE assessment_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    options TEXT,
    answer TEXT,
    level TEXT,
    type TEXT
);
```

### روابط داده‌ای

```
users (1) ←→ (N) progress
users (1) ←→ (N) vocabulary  
users (1) ←→ (N) user_grammar
vocabulary_words (N) ←→ (N) vocabulary
grammar_lessons (N) ←→ (N) user_grammar
```

---

## 🔗 API و یکپارچه‌سازی

### یکپارچه‌سازی با Telegram Bot API

```python
# تنظیمات اصلی
from telegram.ext import Application, CommandHandler, MessageHandler

# ایجاد Application
application = Application.builder().token(TOKEN).build()

# افزودن Handler ها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT, handle_message))
application.add_handler(CallbackQueryHandler(handle_assessment_callback))
```

### یکپارچه‌سازی با OpenAI API

```python
# تنظیمات OpenAI
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# نمونه استفاده برای ارزیابی واژگان
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{
        "role": "user", 
        "content": f"Evaluate student's sentence: {user_sentence}"
    }]
)
```

### متغیرهای محیطی

ایجاد فایل `.env`:
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

---

## ⚙️ راهنمای نصب و راه‌اندازی

### پیش‌نیازها

1. **Python 3.9+**
2. **حساب Telegram Bot**
3. **API Key OpenAI**

### مراحل نصب

#### 1. کلون کردن پروژه
```bash
git clone https://github.com/your-repo/english-learning-bot.git
cd english-learning-bot
```

#### 2. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

#### 3. تنظیم متغیرهای محیطی
```bash
# ایجاد فایل .env
cp .env.example .env

# ویرایش .env و افزودن Token ها
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_api_key_here
```

#### 4. راه‌اندازی پایگاه داده
```bash
# پایگاه داده به صورت خودکار ایجاد می‌شود
python bot.py
```

#### 5. اجرای ربات
```bash
python bot.py
```

### تست نصب

```bash
# تست اتصال به OpenAI
python test_openai.py

# تست پایگاه داده
python test_content_db.py

# تولید داده‌های نمونه برای تست
python simple_dataset.py
```

---

## 📱 راهنمای استفاده

### برای کاربران

#### 1. شروع کار
- ارسال `/start` به ربات
- انجام آزمون تعیین سطح (20 سوال)
- دریافت سطح مناسب

#### 2. تمرین واژگان
- انتخاب "📚 تمرین لغات"
- مطالعه واژه، معنی و مثال
- نوشتن جمله جدید با واژه
- دریافت امتیاز و بازخورد

#### 3. دروس گرامر  
- انتخاب "📝 درس گرامر"
- مطالعه قاعده گرامری
- انجام 2 تمرین عملی
- دریافت امتیاز میانگین

#### 4. تمرین مکالمه
- انتخاب "🗣️ تمرین مکالمه"
- ارسال حداکثر 4 پیام انگلیسی
- دریافت پاسخ و بازخورد AI
- محاسبه امتیاز کلی

#### 5. مشاهده پیشرفت
- انتخاب "📊 پیشرفت من"
- مشاهده درصد پیشرفت در هر بخش
- بررسی آمادگی برای ارتقاء سطح

### برای مدیران

#### دستورات مدیریتی
```bash
/level [new_level]     # تغییر سطح کاربر
/debug_db             # بررسی پایگاه داده
/fix_level            # تصحیح سطح بر اساس آزمون
/create_test [score]  # ایجاد نتیجه آزمون تست
```

#### مانیتورینگ سیستم
- بررسی لاگ‌های سیستم
- پیگیری عملکرد OpenAI API
- کنترل اتصالات پایگاه داده

---

## 🧪 تست و ارزیابی

### انواع تست

#### 1. تست واحد (Unit Testing)
```python
# تست عملکرد توابع اصلی
def test_user_registration():
    db = UserDatabase()
    result = db.register_user(12345, "test_user")
    assert result == True

def test_vocabulary_scoring():
    # تست سیستم امتیازدهی واژگان
    pass
```

#### 2. تست یکپارچگی (Integration Testing)
- تست اتصال به Telegram API
- تست اتصال به OpenAI API  
- تست عملکرد پایگاه داده

#### 3. تست کاربری (User Testing)
- تست flow کامل آموزش
- تست صحت آزمون تعیین سطح
- تست دقت سیستم امتیازدهی

### معیارهای ارزیابی

#### 1. عملکرد فنی
- **زمان پاسخ:** < 3 ثانیه برای هر درخواست
- **دقت AI:** > 85% در امتیازدهی
- **در دسترس بودن:** > 99% uptime

#### 2. تجربه کاربری
- **سادگی استفاده:** رابط کاربری intuitiveطراحی 
- **محتوای آموزشی:** تدریجی و منطقی
- **انگیزه‌بخشی:** سیستم امتیاز و پیشرفت

#### 3. اهداف آموزشی
- **بهبود مهارت:** قابل اندازه‌گیری از طریق نمرات
- **تنوع محتوا:** پوشش واژگان، گرامر، مکالمه
- **شخصی‌سازی:** تطبیق با سطح کاربر

### داده‌های تست

سیستم شامل dataset نمونه با:
- **11 کاربر تست** در سطوح مختلف
- **122+ رکورد پیشرفت** یادگیری
- **49+ تمرین واژگان** با نمرات
- **19+ تکمیل درس گرامر**

---

## 🔒 نکات امنیتی

### حفاظت از اطلاعات

#### 1. مدیریت Token ها
- استفاده از متغیرهای محیطی
- عدم ذخیره Token در کد
- محدودیت دسترسی به فایل `.env`

#### 2. امنیت پایگاه داده
- استفاده از Prepared Statements
- محدودیت دسترسی به فایل‌های DB
- Backup منظم داده‌ها

#### 3. ولیدیشن ورودی
```python
# بررسی صحت ورودی کاربر
def validate_user_input(text):
    if len(text) > 500:
        return False, "Text too long"
    
    # فیلتر محتوای نامناسب
    inappropriate_words = ["spam", "abuse"]
    if any(word in text.lower() for word in inappropriate_words):
        return False, "Inappropriate content"
    
    return True, "Valid"
```

#### 4. Rate Limiting
- محدودیت تعداد درخواست‌ها per user
- جلوگیری از spam
- مدیریت load سیستم

### Logging و Monitoring

```python
import logging

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ثبت رویدادهای مهم
logger.info(f"User {user_id} started assessment")
logger.warning(f"API call failed for user {user_id}")
logger.error(f"Database error: {error}")
```

---

## 📊 ویژگی‌های اضافی (اختیاری)

> **نکته:** بخش‌های زیر به عنوان ویژگی‌های اضافی پیاده‌سازی شده‌اند و در اهداف اصلی پروژه قرار نداشتند.

### 1. پنل مدیریت وب (Admin Panel)
- 🖥️ رابط وب برای مدیریت سیستم
- 📊 داشبورد آماری کاربران
- 📈 نمایش نمودارهای پیشرفت
- ⚙️ مدیریت محتوای آموزشی

### 2. سیستم Analytics پیشرفته
- 📊 تحلیل رفتار کاربران
- 📈 گزارش‌های عملکرد AI
- 🔍 بررسی اثربخشی آموزش
- 📉 آمار استفاده از سیستم

### 3. Performance Monitoring
- ⚡ نظارت بر کارایی سیستم
- 🚨 هشدارهای خودکار
- 📊 متریک‌های real-time
- 🔧 بهینه‌سازی خودکار

استفاده از این بخش‌ها اختیاری بوده و می‌توان آن‌ها را برای توسعه آینده پروژه در نظر گرفت.

---

## 🔮 توسعه‌های آینده

### امکانات پیشنهادی

#### 1. بهبود تجربه کاربری
- 🎯 **گیمیفیکیشن:** سیستم badge و achievement
- 📱 **اپ موبایل:** نسخه standalone
- 🔊 **صدا:** پشتیبانی از voice message
- 🖼️ **تصاویر:** تمرین‌های بصری

#### 2. توسعه محتوا
- 📖 **داستان:** آموزش از طریق story telling
- 🎬 **ویدئو:** یکپارچگی با محتوای ویدئویی
- 🌍 **فرهنگ:** معرفی فرهنگ کشورهای انگلیسی‌زبان
- 💼 **تخصصی:** انگلیسی کسب‌وکار، تکنیکال

#### 3. بهبود AI
- 🧠 **Machine Learning:** یادگیری از رفتار کاربران
- 🎯 **شخصی‌سازی:** محتوای adaptive
- 🗣️ **تشخیص گفتار:** Speech-to-Text
- 🎭 **احساسات:** تحلیل tone و emotion

#### 4. اکوسیستم
- 👥 **کلاس‌های گروهی:** تعامل بین کاربران
- 👨‍🏫 **معلم:** دسترسی به مربی انسانی
- 🏆 **مسابقه:** challenges و competitions
- 🔗 **یکپارچگی:** اتصال به سیستم‌های LMS

---

## 📚 ضمائم

### ضمیمه A: ساختار فایل‌ها

```
english-learning-bot/
├── bot.py                 # ماژول اصلی ربات
├── user_db.py            # مدیریت کاربران
├── content_manager.py    # مدیریت محتوا
├── requirements.txt      # وابستگی‌ها
├── .env.example         # نمونه متغیرهای محیطی
├── README.md            # راهنمای سریع
├── user_data.db         # پایگاه داده کاربران
├── content_data.db      # پایگاه داده محتوا
├── simple_dataset.py    # تولید داده‌های تست
├── test_openai.py       # تست OpenAI API
├── test_content_db.py   # تست پایگاه داده
└── docs/
    ├── API_REFERENCE.md
    ├── DATABASE_SCHEMA.md
    └── DEPLOYMENT_GUIDE.md
```

### ضمیمه B: دستورات مفید

```bash
# اجرای ربات
python bot.py

# تولید داده‌های تست
python simple_dataset.py

# تست اتصالات
python test_openai.py
python test_content_db.py

# مشاهده لاگ‌ها
tail -f error_log.txt

# Backup پایگاه داده
cp user_data.db backup/user_data_$(date +%Y%m%d).db
```

### ضمیمه C: عیب‌یابی مشکلات رایج

#### مشکل: ربات پاسخ نمی‌دهد
```bash
# بررسی Token
echo $TELEGRAM_BOT_TOKEN

# بررسی اتصال به اینترنت
curl -I https://api.telegram.org

# بررسی لاگ‌ها
tail -20 error_log.txt
```

#### مشکل: خطای OpenAI API
```bash
# بررسی API Key
python test_openai.py

# بررسی credit OpenAI
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/usage
```

#### مشکل: خطای پایگاه داده
```bash
# بررسی فایل DB
ls -la *.db

# تست schema
python test_content_db.py

# بازسازی DB
rm user_data.db content_data.db
python bot.py
```

---

## 📞 پشتیبانی و تماس

### اطلاعات پروژه
- **نسخه:** 1.0.0
- **تاریخ ایجاد:** 2024
- **وضعیت:** Production Ready
- **مجوز:** Academic Use

### منابع مفید
- [مستندات Telegram Bot API](https://core.telegram.org/bots/api)
- [مستندات OpenAI API](https://platform.openai.com/docs)
- [راهنمای SQLite](https://www.sqlite.org/docs.html)
- [Python Telegram Bot Library](https://python-telegram-bot.readthedocs.io/)

---

**📝 یادداشت:** این مستند شامل تمام جزئیات فنی و راهنمای کاربری سیستم ربات آموزش زبان انگلیسی است. برای سؤالات بیشتر، لطفاً به بخش‌های مختلف این مستند مراجعه کنید.

---
*آخرین به‌روزرسانی: 2024*
