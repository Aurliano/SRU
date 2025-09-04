# 📡 API Reference - سیستم ربات آموزش زبان انگلیسی

## 📋 فهرست مطالب

1. [کلاس UserDatabase](#کلاس-userdatabase)
2. [کلاس ContentManager](#کلاس-contentmanager)
3. [توابع اصلی Bot](#توابع-اصلی-bot)
4. [OpenAI Integration](#openai-integration)
5. [Telegram Bot Handlers](#telegram-bot-handlers)
6. [Database Schema](#database-schema)
7. [Error Codes](#error-codes)
8. [مثال‌های کاربردی](#مثالهای-کاربردی)

---

## 🗄️ کلاس UserDatabase

### مقدمه
کلاس `UserDatabase` مسئول مدیریت تمام عملیات مربوط به داده‌های کاربران است.

### تنظیمات اولیه

```python
from user_db import UserDatabase

# ایجاد نمونه
db = UserDatabase(db_path="user_data.db")
```

### متدهای کاربر

#### `register_user(user_id, username)`
**توضیح:** ثبت کاربر جدید یا به‌روزرسانی username کاربر موجود

**پارامترها:**
- `user_id` (int): شناسه یکتای کاربر تلگرام
- `username` (str): نام کاربری

**برگشتی:**
- `bool`: True اگر کاربر جدید ثبت شد، False اگر کاربر قبلاً وجود داشت

**مثال:**
```python
is_new_user = db.register_user(12345, "john_doe")
if is_new_user:
    print("کاربر جدید ثبت شد")
else:
    print("کاربر قبلاً وجود داشت")
```

#### `get_user_level(user_id)`
**توضیح:** دریافت سطح فعلی کاربر

**پارامترها:**
- `user_id` (int): شناسه کاربر

**برگشتی:**
- `str`: سطح کاربر ('beginner', 'amateur', 'intermediate', 'advanced')

**مثال:**
```python
level = db.get_user_level(12345)
print(f"سطح کاربر: {level}")
```

#### `update_user_level(user_id, level)`
**توضیح:** به‌روزرسانی سطح کاربر

**پارامترها:**
- `user_id` (int): شناسه کاربر
- `level` (str): سطح جدید

**برگشتی:**
- `bool`: موفقیت عملیات

**مثال:**
```python
success = db.update_user_level(12345, "intermediate")
if success:
    print("سطح به‌روزرسانی شد")
```

### متدهای پیشرفت

#### `add_section_progress(user_id, section, level, increment)`
**توضیح:** افزایش تدریجی پیشرفت در یک بخش

**پارامترها:**
- `user_id` (int): شناسه کاربر
- `section` (str): نام بخش ('vocabulary', 'grammar', 'conversation', 'assessment')
- `level` (str): سطح
- `increment` (float): مقدار افزایش پیشرفت

**برگشتی:**
- `float`: پیشرفت جدید (محدود به 100)

**مثال:**
```python
new_progress = db.add_section_progress(12345, "vocabulary", "beginner", 10.5)
print(f"پیشرفت جدید: {new_progress}%")
```

#### `get_section_progress(user_id, section, level)`
**توضیح:** دریافت پیشرفت فعلی در یک بخش

**پارامترها:**
- `user_id` (int): شناسه کاربر
- `section` (str): نام بخش
- `level` (str): سطح

**برگشتی:**
- `float`: درصد پیشرفت

#### `get_user_progress(user_id)`
**توضیح:** دریافت پیشرفت کامل کاربر در تمام بخش‌ها و سطوح

**برگشتی:**
- `dict`: ساختار تو در تو پیشرفت

**مثال:**
```python
progress = db.get_user_progress(12345)
# ساختار:
# {
#   'vocabulary': {
#     'beginner': 85.5,
#     'amateur': 0.0,
#     ...
#   },
#   'grammar': {...},
#   'conversation': {...},
#   'assessment': {...}
# }
```

#### `check_and_upgrade_level(user_id)`
**توضیح:** بررسی و ارتقاء خودکار سطح کاربر

**شرایط ارتقاء:**
- تمام 3 بخش (vocabulary, grammar, conversation) >= 80%
- عدم وجود آزمون اخیر (24 ساعت گذشته)
- عدم قرار داشتن در بالاترین سطح

**برگشتی:**
- `bool`: True اگر ارتقاء انجام شد

### متدهای واژگان

#### `add_word_studied(user_id, word, score)`
**توضیح:** ثبت تمرین یک واژه

**پارامترها:**
- `user_id` (int): شناسه کاربر
- `word` (str): واژه تمرین شده
- `score` (int): نمره دریافتی (0-100)

#### `get_words_studied_count(user_id)`
**توضیح:** تعداد واژگان تمرین شده کاربر

**برگشتی:**
- `int`: تعداد واژگان یکتا

#### `get_recent_studied_words(user_id, limit)`
**توضیح:** دریافت واژگان اخیراً تمرین شده

**پارامترها:**
- `limit` (int): حداکثر تعداد واژگان

**برگشتی:**
- `list`: لیست dictionary های واژه و معنی

### متدهای گرامر

#### `mark_grammar_lesson_completed(user_id, level, topic_id, score)`
**توضیح:** ثبت تکمیل درس گرامر (در ContentManager)

**پارامترها:**
- `user_id` (int): شناسه کاربر
- `level` (str): سطح
- `topic_id` (int): شناسه درس
- `score` (float): نمره میانگین

### متدهای آزمون

#### `save_assessment_result(user_id, percentage)`
**توضیح:** ذخیره نتیجه آزمون تعیین سطح

**پارامترها:**
- `percentage` (float): درصد صحیح آزمون

**برگشتی:**
- `tuple`: (bool موفقیت, str پیام خطا)

#### `get_latest_assessment_result(user_id)`
**توضیح:** دریافت آخرین نتیجه آزمون

**برگشتی:**
- `tuple`: (str سطح محاسبه شده, float نمره) یا (None, None)

#### `is_assessment_done(user_id)`
**توضیح:** بررسی انجام آزمون توسط کاربر

**برگشتی:**
- `bool`: True اگر آزمون انجام شده

---

## 📚 کلاس ContentManager

### مقدمه
کلاس `ContentManager` مسئول مدیریت محتوای آموزشی است.

### تنظیمات اولیه

```python
from content_manager import ContentManager

# ایجاد نمونه
content_manager = ContentManager(
    db_path="content_data.db",
    user_db_path="user_data.db"
)
```

### متدهای واژگان

#### `get_vocabulary_for_level(level, count=5, user_id=None)`
**توضیح:** دریافت واژگان برای یک سطح (با فیلتر تمرین شده)

**پارامترها:**
- `level` (str): سطح مطلوب
- `count` (int): تعداد واژگان درخواستی
- `user_id` (int, optional): شناسه کاربر برای فیلتر

**برگشتی:**
- `list`: لیست dictionary های واژه

**ساختار خروجی:**
```python
[
    {
        'word': 'apple',
        'definition': 'A fruit',
        'example': 'I like apples.'
    },
    ...
]
```

#### `get_total_vocabulary_count(level)`
**توضیح:** تعداد کل واژگان یک سطح

**برگشتی:**
- `int`: تعداد واژگان

### متدهای گرامر

#### `get_grammar_lesson_for_level(user_id, level)`
**توضیح:** دریافت درس گرامر بعدی (تکمیل نشده)

**برگشتی:**
- `dict` یا `None`: اطلاعات درس یا None اگر همه تکمیل شده

**ساختار خروجی:**
```python
{
    'title': 'Simple Present Tense',
    'content': 'قوانین و توضیحات...',
    'level': 'beginner',
    'topic_id': 1
}
```

#### `get_total_grammar_count(level)`
**توضیح:** تعداد کل دروس گرامر یک سطح

#### `mark_grammar_lesson_completed(user_id, level, topic_id, score)`
**توضیح:** ثبت تکمیل درس گرامر

**برگشتی:**
- `bool`: موفقیت عملیات

### متدهای آزمون

#### `get_mixed_assessment_questions(total_count=20)`
**توضیح:** دریافت سوالات مختلط آزمون تعیین سطح

**پارامترها:**
- `total_count` (int): تعداد کل سوالات

**برگشتی:**
- `list`: لیست سوالات با توزیع متعادل

**ساختار خروجی:**
```python
[
    {
        'question': 'What is the correct word for "آب"?',
        'options': ['Water', 'Air', 'Fire', 'Earth'],
        'answer': 'Water',
        'level': 'beginner'
    },
    ...
]
```

### متدهای مکالمه

#### `get_fallback_conversation_topics(user_id, level)`
**توضیح:** دریافت موضوع مکالمه (با مدیریت تکرار)

**برگشتی:**
- `dict`: اطلاعات موضوع مکالمه

**ساختار خروجی:**
```python
{
    'title': 'Introduce yourself',
    'description': 'Tell me about yourself...',
    'starter': 'Hello! My name is...',
    'level': 'beginner',
    'topic_id': 1
}
```

#### `get_total_conversation_count(level)`
**توضیح:** تعداد کل موضوعات مکالمه یک سطح

### متدهای Deduplication

#### `remove_duplicate_vocabulary()`
**توضیح:** حذف واژگان تکراری از پایگاه داده

#### `remove_duplicate_grammar()`
**توضیح:** حذف دروس گرامر تکراری

#### `remove_duplicate_conversation()`
**توضیح:** حذف موضوعات مکالمه تکراری

---

## 🤖 توابع اصلی Bot

### Command Handlers

#### `async def start(update, context)`
**توضیح:** مدیریت دستور /start

**عملکرد:**
- ثبت/به‌روزرسانی کاربر
- بررسی انجام آزمون
- نمایش منوی مناسب

#### `async def help_command(update, context)`
**توضیح:** نمایش راهنمای استفاده

#### `async def assess_level(update, context)`
**توضیح:** شروع آزمون تعیین سطح

**فرایند:**
1. دریافت 20 سوال مختلط
2. مقداردهی اولیه شمارنده‌ها
3. شروع ارسال سوالات

### Learning Functions

#### `async def vocabulary_practice(update, context)`
**توضیح:** شروع تمرین واژگان

**پارامترهای Context:**
- `current_vocab_words`: لیست واژگان فعلی
- `current_vocab_index`: ایندکس واژه فعلی

#### `async def grammar_lesson(update, context)`
**توضیح:** شروع درس گرامر

**پارامترهای Context:**
- `current_grammar_lesson`: اطلاعات درس فعلی
  - `title`: عنوان درس
  - `content`: محتوای درس
  - `exercises_completed`: تعداد تمرین‌های انجام شده
  - `total_score`: مجموع نمرات

#### `async def conversation_practice(update, context)`
**توضیح:** شروع تمرین مکالمه

**پارامترهای Context:**
- `conversation_topic`: موضوع مکالمه
- `conversation_history`: تاریخچه پیام‌ها
- `conversation_scores`: نمرات دریافتی

### Message Handlers

#### `async def handle_message(update, context)`
**توضیح:** مدیریت پیام‌های کاربر بر اساس state

**States مدیریت شده:**
- `MAIN_MENU`: پردازش دکمه‌های منو
- `VOCABULARY_PRACTICE`: پردازش جمله واژگان
- `GRAMMAR_LESSON`: پردازش تمرین گرامر
- `CONVERSATION_PRACTICE`: پردازش پیام مکالمه

#### `async def handle_assessment_callback(update, context)`
**توضیح:** مدیریت callback های آزمون

**فرایند:**
1. اعتبارسنجی callback
2. بررسی صحت پاسخ
3. به‌روزرسانی شمارنده‌ها
4. ارسال سوال بعدی یا نمایش نتیجه

---

## 🔗 OpenAI Integration

### تنظیمات اولیه

```python
from openai import OpenAI

openai_client = OpenAI(api_key=OPENAI_API_KEY)
```

### تابع کلی فراخوانی

```python
async def call_openai_api(prompt, max_tokens=150, temperature=0.7):
    """فراخوانی کلی API OpenAI"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None
```

### Prompt Templates

#### واژگان
```python
def get_vocabulary_prompt(word, user_sentence):
    return f"""You are an English teacher evaluating vocabulary usage.
    
Word: "{word}"
Student's sentence: "{user_sentence}"

Criteria:
1. Correct word usage (50 points)
2. Grammar (30 points) 
3. Creativity (20 points)

Provide Persian feedback and end with: Score: XX/100"""
```

#### گرامر
```python
def get_grammar_prompt(lesson_title, lesson_content, user_sentence):
    return f"""Grammar lesson: "{lesson_title}"

Rule: {lesson_content}
Student's sentence: "{user_sentence}"

Evaluate focusing on the specific grammar rule.
Persian feedback + Score: XX/100"""
```

#### مکالمه
```python
def get_conversation_prompt(topic, user_message, is_scoring=True):
    if is_scoring:
        return f"""Topic: "{topic['title']}"
Student message: "{user_message}"

Score on: Grammar (40%), Vocabulary (30%), Relevance (20%), Fluency (10%)
Persian feedback + Score: XX/100"""
    else:
        return f"""Continue this conversation naturally about: "{topic['title']}"
Student said: "{user_message}"
Respond in English as a teacher."""
```

---

## 📱 Telegram Bot Handlers

### Application Setup

```python
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler

# ایجاد Application
application = Application.builder().token(TOKEN).build()

# اضافه کردن Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CallbackQueryHandler(handle_assessment_callback, pattern="^assess_"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# شروع polling
application.run_polling()
```

### Callback Query Patterns

#### آزمون تعیین سطح
- **Pattern:** `assess_{question_index}_{selected_option}`
- **مثال:** `assess_5_Water`

#### واژگان
- **Patterns:**
  - `vocab_next`: واژه بعدی
  - `vocab_exit`: خروج از تمرین
  - `vocab_test_{question_index}_{option_index}`: آزمون واژگان

### Keyboard Layouts

#### منوی اصلی
```python
main_keyboard = [
    [KeyboardButton("📚 تمرین لغات"), KeyboardButton("📝 درس گرامر")],
    [KeyboardButton("🗣️ تمرین مکالمه"), KeyboardButton("📊 پیشرفت من")],
    [KeyboardButton("🧪 سنجش سطح"), KeyboardButton("❓ راهنما")]
]
```

#### واژگان
```python
vocab_keyboard = [
    [InlineKeyboardButton("➡️ لغت بعدی", callback_data="vocab_next")],
    [InlineKeyboardButton("🔄 بازگشت به منوی اصلی", callback_data="vocab_exit")]
]
```

---

## 🗄️ Database Schema

### جداول اصلی

#### `users`
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

#### `progress`
```sql
CREATE TABLE progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    section TEXT,           -- vocabulary, grammar, conversation, assessment
    level TEXT,
    score REAL DEFAULT 0,
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### `vocabulary`
```sql
CREATE TABLE vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    word TEXT,
    score INTEGER DEFAULT 0,
    last_practiced TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### `user_grammar`
```sql
CREATE TABLE user_grammar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    level TEXT,
    topic_id INTEGER,
    score INTEGER DEFAULT 0,
    completed_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### جداول محتوا

#### `vocabulary_words`
```sql
CREATE TABLE vocabulary_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT,
    definition TEXT,
    example TEXT,
    level TEXT
);
```

#### `grammar_lessons`
```sql
CREATE TABLE grammar_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    level TEXT
);
```

#### `assessment_questions`
```sql
CREATE TABLE assessment_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    options TEXT,           -- separated by |
    answer TEXT,
    level TEXT,
    type TEXT
);
```

---

## ⚠️ Error Codes

### Database Errors
- `DB_001`: اتصال به پایگاه داده ناموفق
- `DB_002`: خطا در اجرای query
- `DB_003`: کاربر یافت نشد
- `DB_004`: داده نامعتبر

### API Errors  
- `API_001`: خطا در اتصال به OpenAI
- `API_002`: محدودیت درخواست OpenAI
- `API_003`: پاسخ نامعتبر از OpenAI
- `API_004`: خطا در اتصال به Telegram

### Business Logic Errors
- `BL_001`: State نامعتبر کاربر
- `BL_002`: سطح نامعتبر
- `BL_003`: محتوا یافت نشد
- `BL_004`: ورودی نامعتبر کاربر

### مدیریت Error ها

```python
class BotError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

def handle_error(error):
    if error.code.startswith('DB_'):
        # مدیریت خطاهای پایگاه داده
        logger.error(f"Database error: {error}")
    elif error.code.startswith('API_'):
        # مدیریت خطاهای API
        logger.error(f"API error: {error}")
    # ...
```

---

## 💡 مثال‌های کاربردی

### مثال 1: اضافه کردن کاربر جدید و شروع آزمون

```python
async def new_user_flow():
    user_id = 12345
    username = "john_doe"
    
    # ثبت کاربر
    is_new = db.register_user(user_id, username)
    
    if is_new:
        # کاربر جدید - شروع آزمون
        questions = content_manager.get_mixed_assessment_questions(20)
        
        # تنظیم context
        context.user_data['assessment_questions'] = questions
        context.user_data['current_question'] = 0
        context.user_data['correct_answers'] = 0
        
        # ارسال اولین سوال
        await send_assessment_question(message, context)
```

### مثال 2: محاسبه و ذخیره پیشرفت واژگان

```python
async def vocabulary_practice_complete(user_id, word, score):
    # ثبت تمرین واژه
    db.add_word_studied(user_id, word, score)
    
    # محاسبه پیشرفت
    level = db.get_user_level(user_id)
    total_vocab = content_manager.get_total_vocabulary_count(level)
    
    if total_vocab > 0:
        # محاسبه افزایش پیشرفت
        progress_increment = (1 / total_vocab) * 100
        score_multiplier = max(0.7, score / 100)
        final_increment = progress_increment * score_multiplier
        
        # اضافه کردن به پیشرفت
        new_progress = db.add_section_progress(user_id, 'vocabulary', level, final_increment)
        
        # بررسی ارتقاء سطح
        if db.check_and_upgrade_level(user_id):
            await send_level_upgrade_message(user_id)
```

### مثال 3: مدیریت درس گرامر کامل

```python
async def complete_grammar_lesson(user_id, lesson_info, total_score):
    # محاسبه نمره میانگین
    avg_score = total_score / 2  # 2 تمرین
    
    # ثبت تکمیل درس
    success = content_manager.mark_grammar_lesson_completed(
        user_id, 
        lesson_info['level'], 
        lesson_info['topic_id'], 
        avg_score
    )
    
    if success:
        # محاسبه پیشرفت
        total_lessons = content_manager.get_total_grammar_count(lesson_info['level'])
        progress_increment = (1 / total_lessons) * 100
        
        # اضافه کردن پیشرفت
        db.add_section_progress(user_id, 'grammar', lesson_info['level'], progress_increment)
        
        # بررسی ارتقاء
        if db.check_and_upgrade_level(user_id):
            await send_level_upgrade_message(user_id)
```

### مثال 4: تست کامل سیستم

```python
async def system_integration_test():
    test_user_id = 99999
    
    # تست ثبت کاربر
    assert db.register_user(test_user_id, "test_user") == True
    
    # تست آزمون
    questions = content_manager.get_mixed_assessment_questions(5)
    assert len(questions) == 5
    
    # شبیه‌سازی پاسخ‌های صحیح
    correct_count = 4
    percentage = (correct_count / 5) * 100  # 80%
    
    # ذخیره نتیجه
    success, error = db.save_assessment_result(test_user_id, percentage)
    assert success == True
    
    # بررسی سطح
    level = db.get_user_level(test_user_id)
    assert level == "intermediate"  # 80% -> intermediate
    
    # تست واژگان
    vocab = content_manager.get_vocabulary_for_level(level, 3, test_user_id)
    assert len(vocab) <= 3
    
    # تمیزکاری
    # حذف کاربر تست...
```

---

**📝 نتیجه‌گیری:** این API Reference تمام توابع و کلاس‌های موجود در سیستم را به تفصیل شرح می‌دهد. برای استفاده از هر تابع، به مثال‌های ارائه شده مراجعه کنید.

---
*آخرین به‌روزرسانی: 2024*
