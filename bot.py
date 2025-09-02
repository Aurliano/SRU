import logging
# Configure logging FIRST
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO # Use INFO or DEBUG
)
# Define the logger instance
logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from openai import OpenAI
import pytz
from datetime import time, datetime
import json

# Import our custom modules
from user_db import UserDatabase
from content_manager import ContentManager

# Load environment variables
load_dotenv()

# Get the tokens from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Configure the OpenAI API client
if not OPENAI_API_KEY:
    # Use logger now that it's defined
    logger.error("Error: OPENAI_API_KEY not found in .env file.")
    exit()
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    # Use logger now that it's defined
    logger.info("OpenAI API configured successfully")
except Exception as e:
    # Use logger now that it's defined
    logger.error(f"Error configuring OpenAI API: {e}", exc_info=True)
    exit()

# Initialize database and content manager
db = UserDatabase()
content_manager = ContentManager()

# Define conversation states
MAIN_MENU, LEVEL_ASSESSMENT, VOCABULARY_PRACTICE, GRAMMAR_LESSON, CONVERSATION_PRACTICE, VOCABULARY_TEST = range(6)
user_states = {}

# Persian names for levels (update everywhere used)
levels_persian = {
    "beginner": "مبتدی",
    "amateur": "آماتور",
    "intermediate": "متوسط",
    "advanced": "پیشرفته"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    user_id = update.effective_chat.id
    username = update.effective_user.username or str(user_id)
    
    # Register user in database
    is_new = db.register_user(user_id, username)
    db.update_last_active(user_id)
    
    # Set user state
    user_states[user_id] = MAIN_MENU
    
    # Check if user has completed assessment (store in context or db)
    assessment_done = db.is_assessment_done(user_id)
    if not assessment_done:
        keyboard = [[KeyboardButton("🧪 شروع سنجش سطح")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        welcome_message = """
سلام! به ربات یادگیری زبان انگلیسی خوش آمدید! 👋\n\nبرای شروع فرآیند یادگیری، ابتدا باید آزمون تعیین سطح را انجام دهید.\n\nلطفاً روی دکمه زیر کلیک کنید تا آزمون آغاز شود.
"""
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        return
    
    # If assessment already done, show main menu
    keyboard = [
        [KeyboardButton("📚 تمرین لغات"), KeyboardButton("📝 درس گرامر")],
        [KeyboardButton("🗣️ تمرین مکالمه"), KeyboardButton("📊 پیشرفت من")],
        [KeyboardButton("🧪 سنجش سطح"), KeyboardButton("❓ راهنما")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    welcome_message = """
سلام! به ربات یادگیری زبان انگلیسی خوش آمدید! 👋\n\nبا استفاده از این ربات می‌توانید:\n• لغات جدید یاد بگیرید\n• گرامر انگلیسی را تمرین کنید\n• مکالمه انگلیسی را تمرین کنید\n• پیشرفت خود را مشاهده کنید\n\nبرای شروع، از دکمه‌های زیر استفاده کنید.
"""
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    user_id = update.effective_chat.id
    db.update_last_active(user_id)
    
    help_text = """
راهنمای ربات یادگیری زبان انگلیسی:

📚 تمرین لغات - یادگیری و تمرین لغات جدید
📝 درس گرامر - یادگیری قواعد گرامری
🗣️ تمرین مکالمه - مکالمه با ربات برای تقویت مهارت گفتگو
📊 پیشرفت من - مشاهده پیشرفت یادگیری
🧪 سنجش سطح - تعیین سطح زبان انگلیسی شما
❓ راهنما - نمایش این راهنما

دستورات اضافی:
/level - نمایش یا تغییر سطح فعلی شما (مثال: /level intermediate)
/fix_level - به‌روزرسانی خودکار سطح شما بر اساس آخرین نتیجه آزمون سنجش سطح
/debug_db - بررسی و آزمایش اتصال به پایگاه داده و مشکلات احتمالی
/deep_debug - عیب‌یابی پیشرفته برای مشکلات پایگاه داده و آزمون سنجش سطح
/create_test - ایجاد یک رکورد آزمون آزمایشی برای آزمایش /fix_level (مثال: /create_test 75)

برای استفاده از ربات، کافیست روی دکمه‌های زیر کلیک کنید.
"""
    await update.message.reply_text(help_text)

async def assess_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start level assessment process."""
    user_id = update.effective_chat.id
    username = update.effective_user.username or str(user_id)
    
    # Ensure user exists in database before assessment
    was_new = db.register_user(user_id, username)
    if was_new:
        logger.info(f"New user {user_id} registered during assessment start")
    
    db.update_last_active(user_id)
    logger.info(f"Starting level assessment for user {user_id}")

    user_states[user_id] = LEVEL_ASSESSMENT
    # Use the new function to get 20 mixed questions
    assessment_questions = content_manager.get_mixed_assessment_questions(total_count=20)
    if not assessment_questions:
        logger.warning("No assessment questions found in content manager.")
        await update.message.reply_text("متاسفانه در حال حاضر امکان سنجش سطح وجود ندارد.")
        user_states[user_id] = MAIN_MENU
        return
    
    context.user_data['assessment_questions'] = assessment_questions
    context.user_data['current_question'] = 0
    context.user_data['correct_answers'] = 0
    context.user_data['correct_by_level'] = {"beginner": 0, "amateur": 0, "intermediate": 0, "advanced": 0}
    context.user_data['total_by_level'] = {"beginner": 0, "amateur": 0, "intermediate": 0, "advanced": 0}


    await update.message.reply_text(f"شروع آزمون تعیین سطح ({len(assessment_questions)} سوال)...")
    # Pass the message object to send the first question
    await send_assessment_question(update.message, context)

async def send_assessment_question(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """Sends the next assessment question as a NEW message."""
    # Changed 'update: Update' to 'message: Message' for clarity
    user_id = message.from_user.id # Get user_id if needed, but chat_id is primary
    chat_id = message.chat_id # Get chat_id directly

    questions = context.user_data.get('assessment_questions', [])
    current_q = context.user_data.get('current_question', 0)

    if current_q < len(questions):
        question_data = questions[current_q]
        question_text = question_data['question']
        options = question_data['options']
        question_level = question_data['level'] # Get the level for tracking

        # Track total questions per level
        context.user_data['total_by_level'][question_level] += 1

        keyboard = []
        for option in options:
            # Ensure callback data doesn't exceed Telegram limits (64 bytes)
            callback_data = f"assess_{current_q}_{option[:30]}" # Add question index for safety
            keyboard.append([InlineKeyboardButton(option, callback_data=callback_data)])

        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            # Send the question as a new message
            question_prefix = f"سوال {current_q + 1} از {len(questions)}"
            if current_q == len(questions) - 1:
                question_prefix += " (آخرین سوال)"
                
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{question_prefix}:\n\n{question_text}",
                reply_markup=reply_markup
            )
            logger.info(f"Sent question {current_q + 1} to chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send question {current_q + 1} to chat {chat_id}: {e}", exc_info=True)
            # Attempt to notify user in case of send failure
            try:
                 await context.bot.send_message(chat_id=chat_id, text="مشکلی در ارسال سوال بعدی پیش آمد. لطفاً دوباره امتحان کنید یا با ادمین تماس بگیرید.")
            except Exception:
                 logger.error(f"Failed even to send error message to chat {chat_id}")
            user_states[user_id] = MAIN_MENU # Reset state on error

    else:
        # Assessment completed
        correct = context.user_data.get('correct_answers', 0)
        total = len(questions)
        percentage = (correct / total) * 100 if total > 0 else 0

        # Determine level
        level = "beginner"
        if percentage >= 80:
             level = "advanced"
        elif percentage >= 60:
             level = "intermediate"
        elif percentage >= 40:
            level = "amateur"

        # --- Add Logging Here ---
        logger.info(f"Assessment complete for user {user_id}. Calculated score: {percentage:.1f}%. Determined level: {level}.")
        logger.info(f"Attempting to update level in DB for user {user_id} to {level}...")
        # --- End Add Logging ---

        try: # Add try-except around DB operations
             # Get current level before update
             current_level = db.get_user_level(user_id)
             logger.info(f"User {user_id} current level before update: '{current_level}'")
             
             # Update user level in database - now returns boolean success indicator
             success = db.update_user_level(user_id, level)
             
             if not success:
                 logger.warning(f"DB update_user_level returned failure for user {user_id}. Trying direct SQL update...")
                 
                 # First try the force_update_level method
                 force_success = db.force_update_level(user_id, level)
                 
                 if not force_success:
                     logger.error(f"Even force_update_level failed for user {user_id}. Trying raw SQL as final resort...")
                     
                     # Try direct update as a absolute last resort
                     try:
                         import sqlite3
                         conn = sqlite3.connect("user_data.db")
                         cursor = conn.cursor()
                         
                         # First check if user exists
                         cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
                         exists = cursor.fetchone()[0] > 0
                         
                         if not exists:
                             # Create user if doesn't exist
                             now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                             cursor.execute(
                                 "INSERT INTO users (user_id, username, level, join_date, last_active) VALUES (?, ?, ?, ?, ?)",
                                 (user_id, f"user_{user_id}", level, now, now)
                             )
                             logger.info(f"Direct SQL: Created new user {user_id} with level '{level}'")
                         else:
                             # Update existing user
                             cursor.execute("UPDATE users SET level = ? WHERE user_id = ?", (level, user_id))
                             logger.info(f"Direct SQL: Updated existing user {user_id} to level '{level}'")
                         
                         conn.commit()
                         
                         # Verify direct update
                         cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
                         direct_result = cursor.fetchone()
                         logger.info(f"Direct SQL: After update, level for user {user_id} is: '{direct_result[0] if direct_result else 'unknown'}'")
                         conn.close()
                     except Exception as direct_e:
                         logger.error(f"ALL UPDATE METHODS FAILED! Final error: {direct_e}")
             
             # Double-check that level was updated by reading it back
             updated_level = db.get_user_level(user_id)
             logger.info(f"Final check: User {user_id} level after all update attempts: '{updated_level}'")
             
             # Save overall progress - make extra sure this succeeds
             progress_success = False
             try:
                 # Use the specialized save method for assessment results
                 logger.info(f"Saving assessment progress for user {user_id}, score: {percentage}%")
                 progress_success, error = db.save_assessment_result(user_id, percentage)
                 
                 if not progress_success:
                     logger.error(f"Failed to save assessment result: {error}")
                     # The save_assessment_result method already tries all possible methods
             except Exception as progress_e:
                 logger.error(f"Error saving assessment progress: {progress_e}", exc_info=True)
             
             # Log the final result of progress saving
             if progress_success:
                 logger.info(f"Assessment progress successfully saved for user {user_id}")
             else:
                 logger.error(f"FAILED to save assessment progress for user {user_id}")
                 # Notify the user about the issue
                 try:
                     await context.bot.send_message(
                         chat_id=chat_id,
                         text="⚠️ توجه: مشکلی در ذخیره‌سازی نتیجه آزمون شما پیش آمد. برای رفع مشکل، لطفاً دستور /deep_debug را ارسال کنید."
                     )
                 except Exception:
                     pass
             
             # Check if progress table exists and has correct structure
             try:
                 debug_info = db.debug_database(user_id)
                 if 'progress' in debug_info['tables']:
                     logger.info("Progress table exists in database")
                 else:
                     logger.error("Progress table does not exist in database!")
             except Exception as debug_e:
                 logger.error(f"Error checking database structure: {debug_e}")

             # Reset state
             user_states[user_id] = MAIN_MENU

             await context.bot.send_message(
                 chat_id=chat_id,
                 text=(
                     f"✅ ارزیابی سطح شما به پایان رسید!\n\n"
                     f"نتیجه شما: {correct} از {total} ({percentage:.1f}%)\n"
                     f"سطح تخمینی شما: {levels_persian.get(level, 'نامشخص')}\n\n"
                     f"محتوای آموزشی از این پس متناسب با سطح شما ({levels_persian.get(updated_level, 'نامشخص')}) ارائه خواهد شد.\n\n"
                     f"اگر سطح شما به‌درستی به‌روزرسانی نشده، دستور /fix_level را ارسال کنید تا به‌طور خودکار سطح شما بر اساس نتیجه این آزمون تنظیم شود.\n\n"
                     f"اگر با مشکلی مواجه شدید، می‌توانید از دستور /deep_debug برای عیب‌یابی استفاده کنید."
                 )
             )

        except Exception as db_e: # Catch potential DB errors
             logger.error(f"Database error during level update/progress add for user {user_id}: {db_e}", exc_info=True)
             try: # Try to inform the user
                 await context.bot.send_message(chat_id=chat_id, text="مشکلی در ذخیره سازی نتیجه آزمون شما پیش آمد. لطفا دوباره تلاش کنید.")
             except Exception:
                 pass
             # Optionally reset state even on DB error? Or leave in assessment state?
             # For now, reset state:
             user_states[user_id] = MAIN_MENU

    db.set_assessment_done(user_id, True)

async def handle_assessment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle assessment answer selection"""
    query = update.callback_query
    if not query or not query.data or not query.message: # Add checks
        logger.warning("Received invalid callback query update.")
        return

    await query.answer() # Answer callback quickly

    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if user_states.get(user_id) != LEVEL_ASSESSMENT:
        logger.warning(f"Received assessment callback from user {user_id} not in LEVEL_ASSESSMENT state.")
        try: # This try needs an except block
            await query.edit_message_text(
                 f"{query.message.text}\n\n-- آزمون در حال حاضر برای شما فعال نیست --",
                 reply_markup=None
            )
        except Exception as e: # Add the corresponding except block
            logger.error(f"Error editing message on stale callback: {e}")
        # The return should be outside the except block, but associated with the initial if
        return

    # Main logic for processing the callback
    try:
        # Extract question index and selected option from callback data
        parts = query.data.split("_")
        if len(parts) < 3 or parts[0] != "assess":
             raise ValueError("Invalid callback data format")
        current_q_from_callback = int(parts[1])
        selected_option = "_".join(parts[2:])

        questions = context.user_data.get('assessment_questions', [])
        current_q_in_state = context.user_data.get('current_question', -1)

        if current_q_from_callback != current_q_in_state:
             logger.warning(f"Received callback for question {current_q_from_callback} but user {user_id} is on {current_q_in_state}. Ignoring.")
             # Edit the message to show it's old, needs its own try/except
             try:
                 await query.edit_message_text(
                     f"{query.message.text}\n\n-- این سوال قبلا پاسخ داده شده --",
                     reply_markup=None
                 )
             except Exception as edit_e:
                 logger.error(f"Error editing message on old callback: {edit_e}")
             return # Stop processing this old callback

        if current_q_in_state < len(questions):
            question_data = questions[current_q_in_state]
            correct_answer = question_data['answer']
            question_level = question_data['level']

            feedback_text = ""
            if selected_option == correct_answer:
                context.user_data['correct_answers'] = context.user_data.get('correct_answers', 0) + 1
                context.user_data['correct_by_level'][question_level] += 1
                feedback_text = f"{query.message.text}\n\n✅ پاسخ صحیح!"
            else:
                feedback_text = f"{query.message.text}\n\n❌ پاسخ اشتباه بود. پاسخ صحیح: {correct_answer}"

            # Edit the original message - needs its own try/except
            try:
                await query.edit_message_text(feedback_text, reply_markup=None)
            except Exception as edit_e:
                 logger.error(f"Error editing message feedback text: {edit_e}")

            context.user_data['current_question'] = current_q_in_state + 1
            await send_assessment_question(query.message, context)

        else:
             logger.warning(f"Received callback for question {current_q_from_callback} but assessment should be complete for user {user_id}.")
             # Edit the message - needs its own try/except
             try:
                 await query.edit_message_text(
                     f"{query.message.text}\n\n-- آزمون قبلا تمام شده است --",
                     reply_markup=None
                 )
             except Exception as edit_e:
                 logger.error(f"Error editing message on already completed assessment: {edit_e}")

    # Catch errors during the main callback processing
    except Exception as e:
        logger.error(f"Error processing assessment callback data '{query.data}': {e}", exc_info=True)
        try:
            await context.bot.send_message(chat_id=chat_id, text="مشکلی در پردازش پاسخ شما پیش آمد.")
        except Exception:
            pass
        user_states[user_id] = MAIN_MENU

async def vocabulary_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start vocabulary practice."""
    user_id = update.effective_chat.id
    db.update_last_active(user_id)
    
    # Explicitly log and get the current level
    level = db.get_user_level(user_id)
    logger.info(f"Starting vocabulary practice for user {user_id} with level '{level}'")
    
    # Double verify by directly checking the database
    try:
        import sqlite3
        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        direct_level = result[0] if result else "not found"
        conn.close()
        logger.info(f"Direct DB check for user {user_id} level: '{direct_level}'")
        
        if direct_level != level:
            logger.warning(f"Level mismatch for user {user_id}: db.get_user_level='{level}', direct check='{direct_level}'")
    except Exception as e:
        logger.error(f"Error in direct DB check: {e}")
    
    # Get user's vocabulary stats
    words_studied = db.get_words_studied_count(user_id)
    
    # Check if a test is due (after every 20 words)
    if words_studied > 0 and words_studied % 20 == 0 and not context.user_data.get('test_completed'):
        # Redirect to vocabulary test
        return await vocabulary_test(update, context)
    
    # Get words for the user's level - now storing them in context for later reference
    words = content_manager.get_vocabulary_for_level(level, 5)
    context.user_data['current_vocab_words'] = words
    context.user_data['current_vocab_index'] = 0
    
    user_states[user_id] = VOCABULARY_PRACTICE
    
    # Show the first word from the set
    await send_vocabulary_word(update.message, context)

async def send_vocabulary_word(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """Send a vocabulary word to practice."""
    user_id = message.chat_id
    words = context.user_data.get('current_vocab_words', [])
    current_index = context.user_data.get('current_vocab_index', 0)
    
    if not words or current_index >= len(words):
        # No words left in current set
        keyboard = [
            [KeyboardButton("📚 ادامه تمرین با لغات جدید"), KeyboardButton("🔄 بازگشت به منوی اصلی")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await message.reply_text(
            "شما تمام لغات این مجموعه را تمرین کردید. آیا می‌خواهید لغات جدید تمرین کنید؟",
            reply_markup=reply_markup
        )
        return
    
    # Get the current word
    word_data = words[current_index]
    
    # Store the example sentence for plagiarism check later
    context.user_data['current_example'] = word_data['example']
    
    message_text = f"📚 لغت {current_index + 1} از {len(words)}:\n\n"
    message_text += f"🔤 {word_data['word']}\n"
    message_text += f"📝 معنی: {word_data['definition']}\n"
    message_text += f"💡 مثال: {word_data['example']}\n\n"
    message_text += "لطفاً یک جمله جدید و متفاوت با استفاده از این لغت بنویسید (جمله شما نباید مشابه مثال بالا باشد)."
    
    # Add skip button for current word
    keyboard = [[InlineKeyboardButton("⏭️ رد کردن این لغت", callback_data=f"skip_vocab_{current_index}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(message_text, reply_markup=reply_markup)

async def handle_vocabulary_practice(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    """Handle user response to vocabulary practice."""
    user_id = update.effective_chat.id
    
    # Get the current example for plagiarism detection
    current_example = context.user_data.get('current_example', '')
    
    # Check if the user's response is too similar to the example
    from difflib import SequenceMatcher
    similarity = SequenceMatcher(None, message.lower(), current_example.lower()).ratio()
    
    if similarity > 0.7:  # If more than 70% similar
        await update.message.reply_text(
            "⚠️ جمله شما بسیار شبیه به مثال داده شده است. لطفاً جمله متفاوتی با استفاده از این لغت بنویسید."
        )
        return
    
    # Get current word
    words = context.user_data.get('current_vocab_words', [])
    current_index = context.user_data.get('current_vocab_index', 0)
    
    if not words or current_index >= len(words):
        await update.message.reply_text("لطفاً ابتدا تمرین لغات را شروع کنید.")
        return
    
    current_word = words[current_index]['word']
    
    try:
        logger.info(f"Calling Gemini for VOCABULARY_PRACTICE...")
        # Construct prompt for Gemini - updated to be more lenient with scoring
        prompt = f"""You are an English teacher. A student has been given a vocabulary word and asked to use it in a sentence.
Vocabulary word: "{current_word}"
Student's sentence: "{message}"

Evaluate the student's sentence based on these criteria:
1. Did they use the vocabulary word correctly? (50 points)
2. Is the sentence grammatically correct? (30 points)
3. Is the sentence original and creative? (20 points)

Be generous with scoring - if the student made a good attempt, they can get full points in that category.
Provide feedback in Persian, being encouraging and constructive.
Format the score clearly at the end, e.g., Score: 85/100."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        logger.info("Gemini call successful for VOCABULARY_PRACTICE")
        feedback = response.choices[0].message.content

        # Extract score using simple heuristic
        score = 70  # Default score
        try:
            score_part = feedback.split("Score:")[1].split("/")[0].strip()
            score = int(score_part)
        except Exception:
            logger.warning("Could not parse score from Gemini feedback.")
            pass

        # Mark this word as studied
        db.add_word_studied(user_id, current_word, score)
        
        # Move to the next word
        context.user_data['current_vocab_index'] = current_index + 1
        
        # Create buttons for next actions
        keyboard = [
            [InlineKeyboardButton("➡️ لغت بعدی", callback_data="vocab_next")],
            [InlineKeyboardButton("🔄 بازگشت به منوی اصلی", callback_data="vocab_exit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(feedback, reply_markup=reply_markup)
        
        # --- Weighted progress calculation ---
        # Number of unique words studied for this level
        words_studied = db.get_words_studied_count(user_id)
        total_vocab = content_manager.get_total_vocabulary_count(level)
        studied_ratio = min(words_studied / total_vocab, 1.0) if total_vocab else 0
        avg_score = db.get_avg_vocab_score(user_id, level)
        # Weighted: 60% for coverage, 40% for avg score
        weighted_progress = (studied_ratio * 60) + (avg_score * 0.4)
        db.add_section_progress(user_id, 'vocabulary', level, weighted_progress)
        if db.check_and_upgrade_level(user_id):
            await update.message.reply_text("🎉 تبریک! شما به سطح بعدی ارتقاء یافتید.")
    except Exception as e:
        logger.error(f"Error in VOCABULARY_PRACTICE: {str(e)}", exc_info=True)
        level = db.get_user_level(user_id)
        total_vocab = content_manager.get_total_vocabulary_count(level)
        studied_ratio = min(words_studied / total_vocab, 1.0) if total_vocab else 0
        avg_score = db.get_avg_vocab_score(user_id, level)
        weighted_progress = (studied_ratio * 60) + (avg_score * 0.4)
        db.add_section_progress(user_id, 'vocabulary', level, weighted_progress)
        await update.message.reply_text("متأسفانه در بررسی پیام شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")

async def vocabulary_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start or resume a vocabulary test after every 20 words studied."""
    user_id = update.effective_chat.id
    level = db.get_user_level(user_id)

    # Check if a test is already in progress for this user
    vocab_test = context.user_data.get('vocab_test')
    if vocab_test and vocab_test.get('words') and vocab_test.get('current_question', 0) < len(vocab_test['words']):
        # Resume the test
        user_states[user_id] = VOCABULARY_TEST
        await update.message.reply_text(
            "🧪 آزمون لغت شما هنوز به پایان نرسیده است. ادامه می‌دهیم..."
        )
        return await send_vocab_test_question(update.message, context)

    # Get the next batch of 20 untested words for this user and level
    test_words = db.get_next_untested_words(user_id, level, 20)
    if not test_words or len(test_words) < 20:
        await update.message.reply_text(
            "برای شرکت در آزمون لغت باید حداقل ۲۰ لغت جدید تمرین کرده باشید که قبلاً در آزمون شرکت داده نشده‌اند."
            " لطفاً ابتدا لغات بیشتری تمرین کنید تا آزمون فعال شود."
        )
        # Redirect back to vocabulary practice
        return await vocabulary_practice(update, context)

    # Create a multiple choice test
    context.user_data['vocab_test'] = {
        'words': test_words,
        'current_question': 0,
        'correct_answers': 0
    }

    user_states[user_id] = VOCABULARY_TEST

    await update.message.reply_text(
        "🧪 آزمون لغت\n\nبه آزمون لغت خوش آمدید!\nدر این آزمون ۲۰ سوال از لغاتی که اخیراً تمرین کرده‌اید از شما پرسیده می‌شود. برای هر لغت، معنی صحیح را از بین گزینه‌ها انتخاب کنید.\n\nنکته: نتیجه آزمون در پیشرفت شما ثبت خواهد شد. موفق باشید!"
    )

    # Send the first question
    await send_vocab_test_question(update.message, context)

async def send_vocab_test_question(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """Send a vocabulary test question."""
    user_id = message.chat_id
    test_data = context.user_data.get('vocab_test', {})
    test_words = test_data.get('words', [])
    current_q = test_data.get('current_question', 0)

    if current_q >= len(test_words):
        # Test is complete
        correct = test_data.get('correct_answers', 0)
        total = len(test_words)
        score = (correct / total) * 100 if total > 0 else 0
        level = db.get_user_level(user_id)
        # Update progress
        db.add_section_progress(user_id, 'assessment', level, score)
        # Mark these words as tested
        db.mark_words_tested(user_id, [w['word'] for w in test_words])
        # Update vocabulary progress after test
        words_studied = db.get_words_studied_count(user_id)
        total_vocab = content_manager.get_total_vocabulary_count(level)
        studied_ratio = min(words_studied / total_vocab, 1.0) if total_vocab else 0
        avg_score = db.get_avg_vocab_score(user_id, level)
        weighted_progress = (studied_ratio * 60) + (avg_score * 0.4)
        db.add_section_progress(user_id, 'vocabulary', level, weighted_progress)
        context.user_data['test_completed'] = False  # Reset so next 20 triggers test again
        # Reset state
        user_states[user_id] = MAIN_MENU
        result_text = (
            f"✅ آزمون لغت به پایان رسید!\n\n"
            f"نتیجه شما: {correct} از {total} ({score:.1f}%)\n\n"
            f"می‌توانید به تمرین لغت ادامه دهید یا به منوی اصلی بازگردید."
        )
        # Show buttons for next actions
        keyboard = [
            [InlineKeyboardButton("📚 بازگشت به تمرین لغت", callback_data="vocab_practice")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="vocab_exit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(result_text, reply_markup=reply_markup)
        # Check for level up
        if db.check_and_upgrade_level(user_id):
            await message.reply_text("🎉 تبریک! شما به سطح بعدی ارتقاء یافتید.")
        return

    # Get current word
    word = test_words[current_q]

    # Generate incorrect options
    all_definitions = db.get_random_definitions(user_id, 3)
    options = [word['definition']] + all_definitions
    import random
    random.shuffle(options)

    # Create keyboard with options
    keyboard = []
    for idx, option in enumerate(options):
        callback_data = f"vocab_test_{current_q}_{idx}"
        keyboard.append([InlineKeyboardButton(option, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send question
    await message.reply_text(
        f"سوال {current_q + 1} از {len(test_words)}:\n\n"
        f"معنی لغت '{word['word']}' را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def handle_vocab_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle vocabulary callbacks (next word, skip, test answers, test navigation)"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    callback_data = query.data

    if callback_data == "vocab_next":
        # Show next vocabulary word
        await send_vocabulary_word(query.message, context)

    elif callback_data == "vocab_exit":
        # Return to main menu
        user_states[user_id] = MAIN_MENU
        keyboard = [
            [KeyboardButton("📚 تمرین لغات"), KeyboardButton("📝 درس گرامر")],
            [KeyboardButton("🗣️ تمرین مکالمه"), KeyboardButton("📊 پیشرفت من")],
            [KeyboardButton("🧪 سنجش سطح"), KeyboardButton("❓ راهنما")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text("بازگشت به منوی اصلی:", reply_markup=reply_markup)

    elif callback_data == "vocab_practice":
        # Go back to vocabulary practice
        await vocabulary_practice(update, context)

    elif callback_data.startswith("skip_vocab_"):
        # Skip current word
        try:
            # Extract index
            index = int(callback_data.split("_")[2])
            context.user_data['current_vocab_index'] = index + 1
            # Send next word
            await send_vocabulary_word(query.message, context)
        except Exception as e:
            logger.error(f"Error skipping vocabulary word: {e}")
            await query.message.reply_text("مشکلی در رد کردن لغت پیش آمد. لطفاً دوباره تلاش کنید.")

    elif callback_data.startswith("vocab_test_"):
        # Handle test answer
        parts = callback_data.split("_")
        question_index = int(parts[2])
        selected_option_index = int(parts[3])

        test_data = context.user_data.get('vocab_test', {})
        test_words = test_data.get('words', [])
        current_q = test_data.get('current_question', 0)

        if question_index != current_q:
            # Outdated callback
            await query.edit_message_text(
                f"{query.message.text}\n\n-- این سوال قبلاً پاسخ داده شده است --",
                reply_markup=None
            )
            return

        # Get correct answer
        correct_definition = test_words[current_q]['definition']
        options = [button[0].text for button in query.message.reply_markup.inline_keyboard]
        correct_option_index = options.index(correct_definition) if correct_definition in options else -1

        # Check if answer is correct
        is_correct = selected_option_index == correct_option_index

        if is_correct:
            test_data['correct_answers'] = test_data.get('correct_answers', 0) + 1
            feedback = f"{query.message.text}\n\n✅ پاسخ صحیح!"
        else:
            selected_text = options[selected_option_index] if 0 <= selected_option_index < len(options) else "نامشخص"
            feedback = f"{query.message.text}\n\n❌ پاسخ اشتباه.\nپاسخ شما: {selected_text}\nپاسخ صحیح: {correct_definition}"

        # Update message with feedback
        await query.edit_message_text(feedback, reply_markup=None)

        # Move to next question
        test_data['current_question'] = current_q + 1
        context.user_data['vocab_test'] = test_data

        # Send next question after a short delay
        import asyncio
        await asyncio.sleep(2)
        await send_vocab_test_question(query.message, context)

async def grammar_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send grammar lesson with exercises."""
    user_id = update.effective_chat.id
    db.update_last_active(user_id)
    
    # Get and verify level
    level = db.get_user_level(user_id)
    logger.info(f"Starting grammar lesson for user {user_id} with level '{level}'")
    
    # Get the next uncompleted grammar lesson
    lesson = content_manager.get_grammar_lesson_for_level(user_id, level)
    
    if not lesson:
        await update.message.reply_text("متأسفانه در حال حاضر درس گرامر در دسترس نیست.")
        return
    
    # Store lesson info in context for exercises
    context.user_data['current_grammar_lesson'] = {
        'title': lesson['title'],
        'content': lesson['content'],
        'level': lesson['level'],
        'topic_id': lesson['topic_id'],
        'exercises_completed': 0,
        'total_score': 0
    }
    
    user_states[user_id] = GRAMMAR_LESSON
    
    message = f"📝 درس گرامر: {lesson['title']} (سطح {level})\n\n"
    message += f"{lesson['content']}\n\n"
    message += "حالا ۵ تمرین برای شما آماده می‌کنم. لطفاً برای هر تمرین، جمله‌ای با استفاده از این قاعده گرامری بنویسید.\n\n"
    message += "تمرین ۱ از ۵:\n"
    message += "جمله‌ای با استفاده از قاعده گرامری که یاد گرفتید بنویسید:"
    
    await update.message.reply_text(message)

async def conversation_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start or continue advanced conversation practice using OpenAI."""
    user_id = update.effective_chat.id
    db.update_last_active(user_id)
    logger.info(f"Starting/continuing conversation practice for user {user_id}")

    level = db.get_user_level(user_id)
    topic_data = content_manager.get_fallback_conversation_topics(user_id, level)
    user_states[user_id] = CONVERSATION_PRACTICE

    # Initialize conversation history and topic if not present
    if 'conversation_history' not in context.user_data:
        context.user_data['conversation_history'] = []
    if 'conversation_topic' not in context.user_data:
        context.user_data['conversation_topic'] = topic_data

    # If this is the first message, send the topic and ask for a reply
    if not context.user_data['conversation_history']:
        message = f"🗣️ موضوع مکالمه (سطح {level}):\n\n"
        message += f"📝 {topic_data['title']}\n"
        message += f"💡 {topic_data['description']}\n\n"
        message += f"💬 شروع کنید: {topic_data['starter']}"
        await update.message.reply_text(message)
        return
    
    # Otherwise, handle the user's reply (see handle_message below)

async def show_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user progress."""
    user_id = update.effective_chat.id
    db.update_last_active(user_id)
    
    # Get user level
    level = db.get_user_level(user_id)
    
    # Get progress data
    progress = db.get_user_progress(user_id)
    
    # Create progress bars
    categories = {
        "vocabulary": "لغات",
        "grammar": "گرامر",
        "conversation": "مکالمه",
        "assessment": "ارزیابی"
    }
    
    message = "📊 گزارش پیشرفت شما\n\n"
    message += f"سطح فعلی: {level}\n\n"
    
    for category, persian_name in categories.items():
        score = progress[category][level]
        bar_length = 10
        filled_length = int(score / 100 * bar_length)
        bar = "🟩" * filled_length + "⬜" * (bar_length - filled_length)
        
        message += f"{persian_name}: {bar} {score:.1f}%\n"
    
    message += "\nبه تمرین ادامه دهید تا پیشرفت کنید! 💪"
    
    await update.message.reply_text(message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general messages and continue conversations."""
    user_id = update.effective_chat.id
    db.update_last_active(user_id)
    logger.info(f"Received message from user {user_id}")

    message = update.message.text
    state = user_states.get(user_id, MAIN_MENU)
    logger.info(f"User {user_id} state: {state}")

    # Check if assessment is done
    assessment_done = db.is_assessment_done(user_id)
    if not assessment_done:
        if message == "🧪 شروع سنجش سطح" or message == "🧪 سنجش سطح":
            await assess_level(update, context)
            return
        else:
            await update.message.reply_text("برای شروع یادگیری، ابتدا باید آزمون تعیین سطح را انجام دهید. لطفاً روی دکمه \"🧪 شروع سنجش سطح\" کلیک کنید.")
            return

    # Handle button presses
    if message == "📚 تمرین لغات":
        await vocabulary_practice(update, context)
        return
    elif message == "📝 درس گرامر":
        await grammar_lesson(update, context)
        return
    elif message == "🗣️ تمرین مکالمه":
        await conversation_practice(update, context)
        return
    elif message == "📊 پیشرفت من":
        await show_progress(update, context)
        return
    elif message == "🧪 سنجش سطح":
        await assess_level(update, context)
        return
    elif message == "❓ راهنما":
        await help_command(update, context)
        return
    elif message == "📚 ادامه تمرین با لغات جدید":
        await vocabulary_practice(update, context)
        return
    elif message == "🔄 بازگشت به منوی اصلی":
        user_states[user_id] = MAIN_MENU
        keyboard = [
            [KeyboardButton("📚 تمرین لغات"), KeyboardButton("📝 درس گرامر")],
            [KeyboardButton("🗣️ تمرین مکالمه"), KeyboardButton("📊 پیشرفت من")],
            [KeyboardButton("🧪 سنجش سطح"), KeyboardButton("❓ راهنما")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text("بازگشت به منوی اصلی:", reply_markup=reply_markup)
        return
    
    # Handle state-specific messages
    if state == VOCABULARY_PRACTICE:
        await handle_vocabulary_practice(update, context, message)
    elif state == VOCABULARY_TEST:
        await update.message.reply_text("لطفاً از گزینه‌های موجود یکی را انتخاب کنید.")
    elif state == GRAMMAR_LESSON:
        try:
            # Get current grammar lesson info
            lesson_info = context.user_data.get('current_grammar_lesson', {})
            if not lesson_info:
                await update.message.reply_text("لطفاً ابتدا درس گرامر را شروع کنید.")
                return
            
            exercises_completed = lesson_info.get('exercises_completed', 0)
            total_score = lesson_info.get('total_score', 0)
            topic_id = lesson_info.get('topic_id')
            level = lesson_info.get('level')
            
            
            # Check if all 5 exercises are completed
            if exercises_completed >= 5:
                # Calculate average score and mark lesson as completed
                avg_score = total_score / 5
                content_manager.mark_grammar_lesson_completed(user_id, level, topic_id, avg_score)
                
                # --- New Progress Calculation Logic ---
                # Get total number of grammar lessons for the level
                total_lessons = content_manager.get_total_grammar_count(level)
                
                if total_lessons > 0:
                    # Calculate the progress increment for completing one lesson
                    progress_increment = (1 / total_lessons) * 100
                    
                    # Add the calculated increment to the user's grammar progress
                    db.add_section_progress(user_id, 'grammar', level, progress_increment)
                # --- End of New Logic ---
                
                # Check for level up
                if db.check_and_upgrade_level(user_id):
                    await update.message.reply_text("🎉 تبریک! شما به سطح بعدی ارتقاء یافتید.")
                
                # Show completion message
                await update.message.reply_text(
                    f"✅ درس گرامر '{lesson_info['title']}' به پایان رسید!\n\n"
                    f"میانگین امتیاز شما: {avg_score:.1f}/100\n\n"
                    f"برای شروع درس بعدی، دوباره دکمه درس گرامر را بزنید."
                )
                
                # Reset state
                user_states[user_id] = MAIN_MENU
                context.user_data['current_grammar_lesson'] = {}
                return
            
            # Process the current exercise
            logger.info(f"Calling OpenAI for GRAMMAR_LESSON exercise {exercises_completed + 1}...")
            
            # Construct prompt for AI evaluation
            prompt = f"""You are an English grammar teacher. A student has learned this grammar rule:

{lesson_info['content']}

The student wrote this sentence: "{message}"

Evaluate the student's sentence based on:
1. Correct use of the grammar rule (60 points)
2. Grammatical accuracy (30 points)
3. Natural English expression (10 points)

Provide feedback in Persian, being encouraging and constructive.
Format the score clearly at the end, e.g., Score: 85/100.

Focus on the specific grammar rule they just learned."""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            logger.info("OpenAI call successful for GRAMMAR_LESSON")
            feedback = response.choices[0].message.content

            # Extract score
            score = 70  # Default score
            try:
                score_part = feedback.split("Score:")[1].split("/")[0].strip()
                score = int(score_part)
            except Exception:
                logger.warning("Could not parse score from OpenAI feedback.")
                pass

            # Update lesson progress
            exercises_completed += 1
            total_score += score
            
            context.user_data['current_grammar_lesson']['exercises_completed'] = exercises_completed
            context.user_data['current_grammar_lesson']['total_score'] = total_score

            # Show feedback and next exercise
            if exercises_completed < 5:
                next_message = f"{feedback}\n\n"
                next_message += f"تمرین {exercises_completed + 1} از ۵:\n"
                next_message += "جمله‌ای دیگر با استفاده از همین قاعده گرامری بنویسید:"
                await update.message.reply_text(next_message)
            else:
                # This was the last exercise, show completion
                await update.message.reply_text(
                    f"{feedback}\n\n"
                    f"🎉 تمام تمرین‌های این درس به پایان رسید!\n\n"
                    f"میانگین امتیاز شما: {total_score / 5:.1f}/100\n\n"
                    f"درس گرامر '{lesson_info['title']}' با موفقیت تکمیل شد!"
                )
                
        except Exception as e:
            logger.error(f"Error in GRAMMAR_LESSON: {str(e)}", exc_info=True)
            await update.message.reply_text("متأسفانه در بررسی پیام شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")
    
    elif state == CONVERSATION_PRACTICE:
        try:
            user_reply = message.strip()
            import re
            if not re.search(r'[a-zA-Z]', user_reply) or re.search(r'[آ-یءضصثقفغعهخحجچشسیبلاتنمکگظطزرذدپو.,!?؛،]', user_reply):
                await update.message.reply_text("⚠️ لطفاً فقط به انگلیسی پاسخ دهید و به موضوع مکالمه توجه کنید.")
                return
            topic = context.user_data.get('conversation_topic', '')
            level = db.get_user_level(user_id)
            # Initialize conversation state if not present
            if 'conversation_history' not in context.user_data:
                context.user_data['conversation_history'] = []
            if 'conversation_scores' not in context.user_data:
                context.user_data['conversation_scores'] = []
            if 'conversation_ai_replies' not in context.user_data:
                context.user_data['conversation_ai_replies'] = 0
            
            # Limit to 4 user replies
            if len(context.user_data['conversation_history']) >= 4:
                # End session, calculate average score
                scores = context.user_data['conversation_scores']
                avg_score = int(sum(scores) / len(scores)) if scores else 0
                
                # --- New Progress Calculation Logic ---
                total_topics = content_manager.get_total_conversation_count(level)
                if total_topics > 0:
                    # Calculate the progress increment for completing one conversation topic
                    progress_increment = (1 / total_topics) * 100
                    db.add_section_progress(user_id, 'conversation', level, progress_increment)
                # --- End of New Logic ---
                
                if db.check_and_upgrade_level(user_id):
                    await update.message.reply_text("🎉 تبریک! شما به سطح بعدی ارتقاء یافتید.")
                await update.message.reply_text(f"✅ مکالمه به پایان رسید!\nمیانگین امتیاز شما: {avg_score}/100\nبرای شروع مکالمه جدید، دوباره دکمه تمرین مکالمه را بزنید.")
                # Reset state
                context.user_data['conversation_history'] = []
                context.user_data['conversation_scores'] = []
                context.user_data['conversation_ai_replies'] = 0
                context.user_data['conversation_topic'] = None
                user_states[user_id] = MAIN_MENU
                return
            # Score the user's reply
            score_prompt = f"You are an English teacher. A student at the {level} level replied to the topic '{topic['title']}':\n\n'{user_reply}'\n\nGive a score out of 100 for the reply, considering grammar, fluency, and relevance to the topic. Reply only with: Score: XX/100 and a short feedback in Persian."
            score_response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": score_prompt}]
            )
            score_feedback = score_response.choices[0].message.content
            score = 70
            try:
                score_part = score_feedback.split("Score:")[1].split("/")[0].strip()
                score = int(score_part)
            except Exception:
                pass
            context.user_data['conversation_scores'].append(score)
            context.user_data['conversation_history'].append(user_reply)
            await update.message.reply_text(score_feedback)
            # AI short reply (max 3 per session)
            if context.user_data['conversation_ai_replies'] < 3:
                ai_reply_prompt = f"You are an English teacher. The topic is '{topic['title']}'. The student said: '{user_reply}'. Reply with a short, relevant English sentence to continue the conversation."
                ai_reply_response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": ai_reply_prompt}]
                )
                ai_reply = ai_reply_response.choices[0].message.content
                await update.message.reply_text(ai_reply)
                context.user_data['conversation_ai_replies'] += 1
        except Exception as e:
            logger.error(f"Error in CONVERSATION_PRACTICE: {str(e)}", exc_info=True)
            await update.message.reply_text("متأسفانه در پردازش پیام شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")
    
    else:  # MAIN_MENU or any other state
        try: # This try needs its own except
            logger.info(f"Calling Gemini for MAIN_MENU...")
            # Construct prompt for Gemini
            prompt = f"""You are an English teacher bot helping an Iranian student learn English.
The student sent this message outside of a specific task: "{message}"
Respond briefly and politely in Persian. Gently suggest they use the menu buttons (تمرین لغات, درس گرامر, تمرین مکالمه, سنجش سطح) to practice specific skills."""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            logger.info("Gemini call successful for MAIN_MENU")
            reply = response.choices[0].message.content
            # The await needs to be inside the try block if it depends on 'reply'
            await update.message.reply_text(reply)
        # This except corresponds to the try block above
        except Exception as e:
            logger.error(f"Error in MAIN_MENU handler: {str(e)}", exc_info=True)
            await update.message.reply_text("متأسفانه در پردازش پیام شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")

async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send daily reminder to all active users."""
    user_ids = db.get_users_with_notifications()
    
    reminder_message = """
یادآوری روزانه یادگیری زبان انگلیسی 📚✨

امروز را با یادگیری زبان انگلیسی شروع کنید:
- لغات جدید یاد بگیرید 📝
- گرامر انگلیسی را تمرین کنید 📖
- مکالمه انگلیسی را تمرین کنید 🗣️

موفق باشید! 💪
"""
    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text=reminder_message)
        except Exception as e:
            print(f"Failed to send reminder to {user_id}: {e}")

async def set_level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to check or set user level (debug)"""
    user_id = update.effective_chat.id
    db.update_last_active(user_id)
    
    # If no arguments, show current level
    if not context.args:
        level = db.get_user_level(user_id)
        await update.message.reply_text(f"Your current level is: {level}")
        return
    
    # If argument provided, set level
    new_level = context.args[0].lower()
    if new_level not in ["beginner", "amateur", "intermediate", "advanced"]:
        await update.message.reply_text("Invalid level. Use 'beginner', 'amateur', 'intermediate', or 'advanced'.")
        return
    
    # Update level
    try:
        db.update_user_level(user_id, new_level)
        await update.message.reply_text(f"Level successfully set to: {new_level}")
        
        # Verify the update
        updated_level = db.get_user_level(user_id)
        await update.message.reply_text(f"Verification - your level is now: {updated_level}")
    except Exception as e:
        logger.error(f"Error setting level: {e}")
        await update.message.reply_text(f"Error setting level: {str(e)}")

async def debug_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug command to test database functionality"""
    user_id = update.effective_chat.id
    
    # Only respond to messages from authorized users (optional)
    # if user_id not in [authorized_id_1, authorized_id_2]:
    #     await update.message.reply_text("Unauthorized")
    #     return
    
    await update.message.reply_text("Starting database diagnostics...")
    
    # Check if user exists in the database
    try:
        import sqlite3
        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()
        
        # Get database tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        await update.message.reply_text(f"Database tables: {[t[0] for t in tables]}")
        
        # Check user record
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()
        
        if user_row:
            await update.message.reply_text(f"User record found: id={user_row[0]}, username={user_row[1]}, level={user_row[2]}")
        else:
            await update.message.reply_text("User not found in database.")
        
        # Store original level before tests
        original_level = db.get_user_level(user_id)
        await update.message.reply_text(f"Original level before tests: {original_level}")
            
        # Test all levels
        for test_level in ["beginner", "amateur", "intermediate", "advanced"]:
            # Try regular update
            await update.message.reply_text(f"Testing regular update to {test_level}...")
            success = db.update_user_level(user_id, test_level)
            
            if success:
                await update.message.reply_text(f"✅ Regular update to {test_level} succeeded")
            else:
                await update.message.reply_text(f"❌ Regular update to {test_level} failed")
                
                # Try force update
                await update.message.reply_text(f"Testing force update to {test_level}...")
                force_success = db.force_update_level(user_id, test_level)
                
                if force_success:
                    await update.message.reply_text(f"✅ Force update to {test_level} succeeded")
                else:
                    await update.message.reply_text(f"❌ Force update to {test_level} failed")
                    
            # Verify current level
            current = db.get_user_level(user_id)
            await update.message.reply_text(f"Current level after test: {current}")
        
        # Restore original level
        restore_success = db.update_user_level(user_id, original_level)
        if not restore_success:
            db.force_update_level(user_id, original_level)
        
        # Verify restoration
        final_level = db.get_user_level(user_id)
        await update.message.reply_text(f"✅ Level restored to original: {final_level}")
        
        conn.close()
    except Exception as e:
        await update.message.reply_text(f"Error during diagnostics: {str(e)}")
    
    await update.message.reply_text("Database diagnostics complete. Your level has been restored to its original value.")

async def deep_debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Advanced diagnostics for database troubleshooting"""
    user_id = update.effective_chat.id
    
    await update.message.reply_text("Starting advanced database diagnostics. This may take a moment...")
    
    try:
        # Get comprehensive database information
        debug_info = db.debug_database(user_id)
        
        # Send the database structure information
        tables_info = f"Database file exists: {debug_info['db_exists']}\n"
        tables_info += f"Database size: {debug_info['db_size']} bytes\n"
        tables_info += f"Tables found: {', '.join(debug_info['tables'])}\n"
        tables_info += f"Database integrity: {debug_info['integrity_check']}\n"
        
        if debug_info['foreign_key_violations']:
            tables_info += f"⚠️ Foreign key violations found: {len(debug_info['foreign_key_violations'])}\n"
        else:
            tables_info += "✅ No foreign key violations found\n"
            
        if debug_info['errors']:
            tables_info += f"⚠️ Diagnostic errors: {len(debug_info['errors'])}\n"
        
        await update.message.reply_text(tables_info)
        
        # Send info about progress table
        progress_info = f"Total progress records: {debug_info['progress_count']}\n"
        progress_info += f"Assessment progress records: {debug_info['assessment_progress_count']}\n"
        
        if "progress" in debug_info["table_structures"]:
            cols = debug_info["table_structures"]["progress"]
            progress_info += f"Progress table structure: {len(cols)} columns\n"
            for col in cols:
                progress_info += f"  - {col['name']} ({col['type']})\n"
        else:
            progress_info += "⚠️ Could not retrieve progress table structure\n"
            
        await update.message.reply_text(progress_info)
        
        # Send user-specific info
        user_info = f"User record exists: {debug_info['user_exists']}\n"
        if debug_info['user_exists']:
            user_info += f"User level: {debug_info['user_level']}\n"
            user_info += f"Join date: {debug_info['user_record']['join_date']}\n"
            user_info += f"Last active: {debug_info['user_record']['last_active']}\n"
        
        if debug_info['last_assessment']:
            user_info += "Last assessment:\n"
            user_info += f"  - Score: {debug_info['last_assessment']['score']}\n"
            user_info += f"  - Date: {debug_info['last_assessment']['date']}\n"
            
            # Calculate what level this should be
            score = debug_info['last_assessment']['score']
            calculated_level = "beginner"
            if score >= 80:
                calculated_level = "advanced"
            elif score >= 60:
                calculated_level = "intermediate"
            
            user_info += f"  - Calculated level: {calculated_level}\n"
            
            if debug_info['user_exists'] and calculated_level != debug_info['user_level']:
                user_info += f"⚠️ MISMATCH: User level ({debug_info['user_level']}) doesn't match assessment level ({calculated_level})\n"
                user_info += "Send /fix_level to correct this issue\n"
        else:
            user_info += "⚠️ No assessment records found for this user\n"
            
        await update.message.reply_text(user_info)
        
        # Attempt to fix database issues
        if not debug_info['user_exists']:
            await update.message.reply_text("Creating missing user record...")
            username = update.effective_user.username or str(user_id)
            db.register_user(user_id, username)
        
        # Verify fix_level would have a valid result
        if debug_info['last_assessment']:
            score = debug_info['last_assessment']['score']
            calculated_level = "beginner"
            if score >= 80:
                calculated_level = "advanced"
            elif score >= 60:
                calculated_level = "intermediate"
                
            await update.message.reply_text(f"If you run /fix_level, your level will be set to: {calculated_level}")
        else:
            await update.message.reply_text("No assessment data found. Please complete an assessment with /level_assessment first.")
        
    except Exception as e:
        await update.message.reply_text(f"Error during deep diagnostics: {str(e)}")
    
    await update.message.reply_text("Advanced diagnostics complete.")

async def fix_level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to automatically fix user level based on latest assessment results"""
    user_id = update.effective_chat.id
    
    # Get the current level
    current_level = db.get_user_level(user_id)
    
    # Show current level
    await update.message.reply_text(f"سطح فعلی شما: {levels_persian.get(current_level, current_level)}")
    
    # Get the latest assessment result
    latest_level, latest_score = db.get_latest_assessment_result(user_id)
    
    if not latest_level:
        await update.message.reply_text(
            "هیچ نتیجه ارزیابی قبلی برای شما یافت نشد.\n"
            "لطفاً ابتدا آزمون سنجش سطح را انجام دهید و سپس از این دستور استفاده کنید.\n\n"
            "برای آزمایش این دستور، می‌توانید از دستور /create_test برای ایجاد یک رکورد ارزیابی آزمایشی استفاده کنید."
        )
        return
    
    if current_level == latest_level:
        await update.message.reply_text(
            f"سطح فعلی شما ({levels_persian.get(current_level)}) با نتیجه آخرین ارزیابی شما مطابقت دارد.\n"
            f"نیازی به تغییر نیست."
        )
        return
    
    # Found a different level from assessment, ask user to confirm
    await update.message.reply_text(
        f"آخرین نتیجه ارزیابی شما (با امتیاز {latest_score:.1f}%)، سطح {levels_persian.get(latest_level)} را نشان می‌دهد.\n\n"
        f"در حال به‌روزرسانی سطح شما از '{levels_persian.get(current_level)}' به '{levels_persian.get(latest_level)}'..."
    )
    
    # First try using our normal method
    success = db.update_user_level(user_id, latest_level)
    
    if not success:
        # If failed, try force method
        await update.message.reply_text("روش استاندارد با مشکل مواجه شد. در حال استفاده از روش جایگزین...")
        force_success = db.force_update_level(user_id, latest_level)
        
        if not force_success:
            await update.message.reply_text("⚠️ متأسفانه تغییر سطح با مشکل مواجه شد. لطفاً با پشتیبانی تماس بگیرید.")
            return
    
    # Verify the update worked
    updated_level = db.get_user_level(user_id)
    
    if updated_level == latest_level:
        await update.message.reply_text(
            f"✅ سطح شما با موفقیت به '{levels_persian.get(latest_level)}' تغییر یافت.\n\n"
            f"محتوای آموزشی از این پس متناسب با سطح جدید شما ارائه خواهد شد."
        )
    else:
        await update.message.reply_text(
            f"⚠️ مشکلی در تغییر سطح پیش آمد. سطح فعلی شما: '{levels_persian.get(updated_level, updated_level)}'\n"
            f"لطفاً دوباره تلاش کنید یا از دستور /debug_db برای بررسی بیشتر استفاده کنید."
        )

async def create_test_assessment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a test assessment record for debugging purposes"""
    user_id = update.effective_chat.id
    
    # Extract score from command arguments if provided, otherwise use default
    score = 60  # Default score (intermediate level)
    if context.args and len(context.args) > 0:
        try:
            score = float(context.args[0])
            # Ensure score is between 0 and 100
            score = max(0, min(100, score))
        except ValueError:
            await update.message.reply_text("خطا: نمره باید یک عدد بین 0 تا 100 باشد.")
            return
    
    # Determine level based on score
    level = "beginner"
    if score >= 80:
        level = "advanced"
    elif score >= 60:
        level = "intermediate"
    elif score >= 40:
        level = "amateur"
    
    await update.message.reply_text(f"در حال ایجاد یک نتیجه آزمون آزمایشی با نمره {score}% (سطح {level})...")
    
    # Save the test assessment record
    success, error = db.save_assessment_result(user_id, score)
    
    if success:
        await update.message.reply_text(
            f"✅ نتیجه آزمون آزمایشی با موفقیت ذخیره شد.\n"
            f"نمره: {score}%\n"
            f"سطح محاسبه شده: {level}\n\n"
            f"اکنون می‌توانید از دستور /fix_level برای به‌روزرسانی سطح خود استفاده کنید."
        )
    else:
        await update.message.reply_text(
            f"❌ خطا در ذخیره‌سازی نتیجه آزمون آزمایشی:\n{error}\n\n"
            f"لطفاً از دستور /deep_debug برای عیب‌یابی بیشتر استفاده کنید."
        )
    
    # Run a verification check
    debug_info = db.debug_database(user_id)
    if debug_info['last_assessment']:
        verify_info = (
            f"تأیید نتیجه آزمون:\n"
            f"آخرین نمره: {debug_info['last_assessment']['score']}%\n"
            f"تاریخ: {debug_info['last_assessment']['date']}"
        )
        await update.message.reply_text(verify_info)
    else:
        await update.message.reply_text("⚠️ هشدار: حتی پس از ذخیره‌سازی، هیچ سابقه آزمونی در پایگاه داده یافت نشد.")

def main():
    """Start the bot."""
    # Configure logging basic setup
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    # Create application with timeout settings to handle network issues
    # If you're in Iran and need proxy, uncomment and configure the proxy settings below:
    # proxy_url = "http://your_proxy:port"
    # application = Application.builder().token(TOKEN).proxy_url(proxy_url).read_timeout(30).write_timeout(30).connect_timeout(30).build()
    
    application = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("level", set_level_command))
    application.add_handler(CommandHandler("debug_db", debug_db_command))
    application.add_handler(CommandHandler("fix_level", fix_level_command))
    application.add_handler(CommandHandler("deep_debug", deep_debug_command))
    application.add_handler(CommandHandler("create_test", create_test_assessment_command))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(handle_assessment_callback, pattern="^assess_"))
    application.add_handler(CallbackQueryHandler(handle_vocab_callback, pattern="^vocab_"))  # New callback handler
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set up the daily job at 12 AM
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(send_daily_reminder, time=time(0, 0))
        logger.info("Daily reminder job scheduled.")
    else:
        logger.warning("JobQueue not available, daily reminders will not be sent")

    # Start the Bot
    logger.info("Starting bot polling...")
    application.run_polling()
    logger.info("Bot polling has ended.")

if __name__ == '__main__':
    main() 