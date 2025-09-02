import sqlite3
import random
import os
from datetime import datetime
# Vocabulary is now defined directly in the database methods

class ContentManager:
    """Manage educational content for the English learning bot."""
    
    def __init__(self, db_path="content_data.db", user_db_path="user_data.db"):
        """Initialize ContentManager with database connection."""
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        # Connect to database
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Connect to user database for tracking studied words
        self.user_conn = sqlite3.connect(user_db_path)
        self.user_cursor = self.user_conn.cursor()
        
        # Initialize database
        self.init_database()
        self.run_content_deduplication_report()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            # Create vocabulary words table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT,
                definition TEXT,
                example TEXT,
                level TEXT
            )
            ''')
            
            # Create grammar lessons table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS grammar_lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                level TEXT
            )
            ''')
            
            # Create assessment questions table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessment_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                options TEXT,
                answer TEXT,
                level TEXT,
                type TEXT
            )
            ''')
            
            # Create conversation topics table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                starter TEXT,
                level TEXT,
                topic_id INTEGER
            )
            ''')
            
            self.conn.commit()
            
            # Check if vocabulary table has data
            self.cursor.execute("SELECT COUNT(*) FROM vocabulary_words")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # Populate with initial data
                self.populate_vocabulary_table()
                self.populate_grammar_lessons()
                self.populate_assessment_questions()
                self.populate_conversation_topics()
        
        except Exception as e:
            print(f"Error initializing content database: {e}")
    
    def get_vocabulary_for_level(self, level, count=5):
        """Get vocabulary words for a specific level."""
        try:
            # First try from database
            self.cursor.execute(
                "SELECT word, definition, example FROM vocabulary_words WHERE level = ? ORDER BY RANDOM() LIMIT ?",
                (level, count)
            )
            words = []
            for row in self.cursor.fetchall():
                words.append({
                    'word': row[0],
                    'definition': row[1],
                    'example': row[2]
                })
            
            # If not enough words in database, use fallback
            if len(words) < count:
                fallback_words = self.get_fallback_vocabulary(level, count - len(words))
                words.extend(fallback_words)
                
                # Try to save fallback words to database for future use
                for word in fallback_words:
                    try:
                        self.cursor.execute(
                            "INSERT INTO vocabulary_words (word, definition, example, level) VALUES (?, ?, ?, ?)",
                            (word['word'], word['definition'], word['example'], level)
                        )
                    except Exception:
                        # Word might already exist, ignore
                        pass
                
                self.conn.commit()
                
            return words
        except Exception as e:
            print(f"Error getting vocabulary for level {level}: {e}")
            # Fallback to static lists
            return self.get_fallback_vocabulary(level, count)
            
    def get_grammar_lesson_for_level(self, user_id, level):
        """Get the next uncompleted grammar lesson for a user at a specific level."""
        try:
            # Check which lessons the user has already completed
            completed_lessons = self.get_completed_grammar_lessons(user_id, level)
            
            # First try to get lessons from database
            self.cursor.execute(
                "SELECT title, content, level FROM grammar_lessons WHERE level = ? ORDER BY id",
                (level,)
            )
            db_lessons = []
            for row in self.cursor.fetchall():
                db_lessons.append({
                    'title': row[0],
                    'content': row[1],
                    'level': row[2],
                    'topic_id': len(db_lessons) + 1  # Assign topic_id based on order
                })
            
            # If database has lessons, use them
            if db_lessons:
                all_lessons = db_lessons
            else:
                # Fallback to static lessons
                all_lessons = self.get_fallback_grammar_lesson(level, all_lessons=True)
            
            # Find the first uncompleted lesson
            for lesson in all_lessons:
                if lesson['topic_id'] not in completed_lessons:
                    return lesson
            
            # If all lessons are completed, return the first one (cycle back)
            return all_lessons[0] if all_lessons else None
            
        except Exception as e:
            print(f"Error getting grammar lesson for level: {e}")
            return self.get_fallback_grammar_lesson(level)
    
    def get_completed_grammar_lessons(self, user_id, level):
        """Get list of completed grammar lesson topic IDs for a user."""
        try:
            self.user_cursor.execute(
                "SELECT topic_id FROM user_grammar WHERE user_id = ? AND level = ?",
                (user_id, level)
            )
            completed = [row[0] for row in self.user_cursor.fetchall()]
            return completed
        except Exception as e:
            print(f"Error getting completed grammar lessons: {e}")
            return []
    
    def mark_grammar_lesson_completed(self, user_id, level, topic_id, score):
        """Mark a grammar lesson as completed for a user with their score."""
        try:
            # Check if already exists
            self.user_cursor.execute(
                "SELECT id FROM user_grammar WHERE user_id = ? AND level = ? AND topic_id = ?",
                (user_id, level, topic_id)
            )
            
            if self.user_cursor.fetchone():
                # Update existing record
                self.user_cursor.execute(
                    "UPDATE user_grammar SET score = ?, completed_at = ? WHERE user_id = ? AND level = ? AND topic_id = ?",
                    (score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, level, topic_id)
                )
            else:
                # Insert new record
                self.user_cursor.execute(
                    "INSERT INTO user_grammar (user_id, level, topic_id, score, completed_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, level, topic_id, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
            
            self.user_conn.commit()
            return True
        except Exception as e:
            print(f"Error marking grammar lesson completed: {e}")
            return False
    
    def get_grammar_progress(self, user_id, level):
        """Get grammar learning progress for a user at a specific level."""
        try:
            completed_lessons = self.get_completed_grammar_lessons(user_id, level)
            total_lessons = 5  # 5 topics per level
            
            if total_lessons == 0:
                return 0
            
            progress_percentage = (len(completed_lessons) / total_lessons) * 100
            return min(progress_percentage, 100)
        except Exception as e:
            print(f"Error getting grammar progress: {e}")
            return 0
    
    def get_seen_grammar_titles(self, user_id, level):
        """Get grammar lesson titles that a user has already seen for a specific level."""
        try:
            self.user_cursor.execute(
                "SELECT lesson_title FROM user_grammar WHERE user_id = ? AND level = ?",
                (user_id, level)
            )
            return set(row[0] for row in self.user_cursor.fetchall())
        except Exception as e:
            print(f"Error getting seen grammar titles for user {user_id}: {e}")
            return set()
    
    def add_grammar_seen(self, user_id, lesson_title, level):
        """Mark a grammar lesson as seen by a user."""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.user_cursor.execute(
                "INSERT INTO user_grammar (user_id, lesson_title, level, date) VALUES (?, ?, ?, ?)",
                (user_id, lesson_title, level, now)
            )
            self.user_conn.commit()
        except Exception as e:
            print(f"Error adding grammar seen for user {user_id}: {e}")
    
    def reset_grammar_seen(self, user_id, level):
        """Reset seen grammar lessons for a user at a specific level."""
        try:
            self.user_cursor.execute(
                "DELETE FROM user_grammar WHERE user_id = ? AND level = ?",
                (user_id, level)
            )
            self.user_conn.commit()
        except Exception as e:
            print(f"Error resetting grammar seen for user {user_id}: {e}")

    def get_mixed_assessment_questions(self, total_count=20):
        """Get a mix of assessment questions across different levels and types."""
        try:
            questions = []
            levels = ['beginner', 'amateur', 'intermediate', 'advanced']
            
            # Fetch all questions from the database first
            self.cursor.execute(
                "SELECT question, options, answer, level FROM assessment_questions ORDER BY id"
            )
            all_db_questions = []
            for row in self.cursor.fetchall():
                all_db_questions.append({
                    'question': row[0],
                    'options': row[1].split('|'),
                    'answer': row[2],
                    'level': row[3]
                })

            # If no questions in DB, use only fallback
            if not all_db_questions:
                all_db_questions = self.get_fallback_assessment_questions(200) # Get a large set from fallback

            # Shuffle all available questions (from DB or fallback) and pick unique ones
            random.shuffle(all_db_questions)
            
            selected_questions = []
            seen_question_texts = set()
            
            # Distribute questions by level if possible, else just pick unique ones
            per_level = total_count // len(levels)
            level_counts = {lvl: 0 for lvl in levels}
            
            for q_data in all_db_questions:
                if len(selected_questions) >= total_count:
                    break
                
                q_text = q_data['question'].lower().strip()
                q_level = q_data['level']
                
                if q_text not in seen_question_texts and level_counts[q_level] < per_level + (total_count % len(levels) if q_level == levels[-1] else 0): # Distribute remaining
                    selected_questions.append(q_data)
                    seen_question_texts.add(q_text)
                    level_counts[q_level] += 1
            
            # If still not enough, add more unique questions regardless of level distribution
            if len(selected_questions) < total_count:
                for q_data in all_db_questions:
                    if len(selected_questions) >= total_count:
                        break
                    q_text = q_data['question'].lower().strip()
                    if q_text not in seen_question_texts:
                        selected_questions.append(q_data)
                        seen_question_texts.add(q_text)

            # Ensure the final list is exactly total_count and randomly shuffled
            random.shuffle(selected_questions)
            return selected_questions[:total_count]
            
        except Exception as e:
            print(f"Error getting mixed assessment questions: {e}")
            # Fallback to general static questions if everything else fails
            fallback_q = self.get_fallback_assessment_questions(total_count)
            random.shuffle(fallback_q)
            return fallback_q[:total_count]

    def get_studied_words(self, user_id):
        """Get a set of words a user has already studied."""
        try:
            self.user_cursor.execute(
                "SELECT word FROM vocabulary WHERE user_id = ?",
                (user_id,)
            )
            return set(row[0] for row in self.user_cursor.fetchall())
        except Exception as e:
            print(f"Error getting studied words for user {user_id}: {e}")
            return set()
            
    def get_fallback_vocabulary(self, level, count=5):
        """Fallback vocabulary when database fails or is empty."""
        vocabulary = {
            'beginner': [
                {'word': 'apple', 'definition': 'A fruit', 'example': 'I like apples.'},
                {'word': 'book', 'definition': 'A written work', 'example': 'I read a book.'},
                {'word': 'cat', 'definition': 'A small domesticated carnivorous mammal', 'example': 'I have a cat.'},
                {'word': 'dog', 'definition': 'A domesticated carnivorous mammal', 'example': 'I have a dog.'},
                {'word': 'house', 'definition': 'A building for human habitation', 'example': 'I live in a house.'}
            ],
            'amateur': [
                {'word': 'car', 'definition': 'A road vehicle', 'example': 'I drive a car.'},
                {'word': 'tree', 'definition': 'A large plant with a trunk and branches', 'example': 'I see a tree.'},
                {'word': 'water', 'definition': 'A liquid', 'example': 'I drink water.'},
                {'word': 'fire', 'definition': 'A chemical reaction that produces light and heat', 'example': 'I saw a fire.'},
                {'word': 'sky', 'definition': 'The expanse of the atmosphere', 'example': 'I look at the sky.'}
            ],
            'intermediate': [
                {'word': 'computer', 'definition': 'An electronic device for storing and processing data', 'example': 'I use a computer.'},
                {'word': 'internet', 'definition': 'A global network connecting millions of computers', 'example': 'I use the internet.'},
                {'word': 'phone', 'definition': 'A device for communication', 'example': 'I use a phone.'},
                {'word': 'mail', 'definition': 'A letter or message sent by post', 'example': 'I send a mail.'},
                {'word': 'money', 'definition': 'A medium of exchange', 'example': 'I have money.'}
            ],
            'advanced': [
                {'word': 'algorithm', 'definition': 'A set of instructions for a computer to follow', 'example': 'I use an algorithm.'},
                {'word': 'data', 'definition': 'Information in a raw or unorganized form', 'example': 'I collect data.'},
                {'word': 'logic', 'definition': 'The principles of reasoning', 'example': 'I use logic.'},
                {'word': 'theory', 'definition': 'A well-substantiated explanation of some aspect of the natural or social world', 'example': 'I have a theory.'},
                {'word': 'research', 'definition': 'The systematic investigation of a subject', 'example': 'I do research.'}
            ]
        }
        level_vocab = vocabulary.get(level, vocabulary['beginner'])
        return random.sample(level_vocab, min(count, len(level_vocab)))
    
    def get_fallback_grammar_lesson(self, level, all_lessons=False):
        """Fallback grammar lessons when database fails or is empty."""
        lessons = {
            'beginner': [
                {
                    'title': 'Simple Present Tense',
                    'content': 'The Simple Present Tense is used to describe:\n\n1. Habits and routines: "I go to school every day."\n2. General truths: "The sun rises in the east."\n3. Fixed arrangements: "The train leaves at 9 AM."\n\nForm:\n- I/You/We/They + base form: "I work", "They study"\n- He/She/It + base form + s: "He works", "She studies"\n\nExamples:\n- I speak English.\n- She works in a hospital.\n- They live in Tehran.\n- The earth moves around the sun.',
                    'level': 'beginner',
                    'topic_id': 1
                },
                {
                    'title': 'Simple Past Tense',
                    'content': 'The Simple Past Tense is used to describe:\n\n1. Completed actions in the past: "I finished my homework yesterday."\n2. Past habits: "I played football when I was young."\n3. Past states: "She was happy last week."\n\nForm:\n- Regular verbs: base form + ed: "work → worked", "play → played"\n- Irregular verbs: special forms: "go → went", "see → saw"\n\nExamples:\n- I studied English last year.\n- She went to Paris in 2020.\n- They played football yesterday.\n- He was a student in 2019.',
                    'level': 'beginner',
                    'topic_id': 2
                },
                {
                    'title': 'There is/There are',
                    'content': '"There is" and "There are" are used to:\n\n1. Say that something exists: "There is a book on the table."\n2. Describe what exists in a place: "There are many students in the class."\n\nForm:\n- Singular: "There is + singular noun"\n- Plural: "There are + plural noun"\n- Negative: "There isn\'t/There aren\'t"\n- Questions: "Is there/Are there"\n\nExamples:\n- There is a cat in the garden.\n- There are three cars in the parking lot.\n- There isn\'t any milk in the fridge.\n- Are there any students in the library?',
                    'level': 'beginner',
                    'topic_id': 3
                },
                {
                    'title': 'Countable and Uncountable Nouns',
                    'content': 'Nouns can be countable or uncountable:\n\nCountable Nouns:\n- Can be counted: "one book, two books"\n- Use "a/an" and numbers\n- Examples: book, car, student, house\n\nUncountable Nouns:\n- Cannot be counted: "water, information"\n- Use "some", "much", "a lot of"\n- Examples: water, milk, money, information\n\nExamples:\n- I have three books. (countable)\n- I need some water. (uncountable)\n- There are many students. (countable)\n- There is much information. (uncountable)',
                    'level': 'beginner',
                    'topic_id': 4
                },
                {
                    'title': 'Articles (a/an/the)',
                    'content': 'Articles are words used before nouns:\n\nIndefinite Articles (a/an):\n- "a" before consonant sounds: "a book", "a car"\n- "an" before vowel sounds: "an apple", "an hour"\n- Used for general things: "I need a pen."\n\nDefinite Article (the):\n- Used for specific things: "The book on the table is mine."\n- Used for unique things: "The sun", "The moon"\n- Used for things mentioned before: "I saw a cat. The cat was black."\n\nExamples:\n- I have a car. (any car)\n- The car is red. (specific car)\n- She is an engineer. (profession)\n- The earth is round. (unique)',
                    'level': 'beginner',
                    'topic_id': 5
                }
            ],
            'amateur': [
                {
                    'title': 'Present Perfect Tense',
                    'content': 'The Present Perfect Tense is used to:\n\n1. Connect past and present: "I have lived here for 5 years."\n2. Talk about experiences: "I have been to Paris."\n3. Recent actions: "I have just finished my homework."\n\nForm:\n- Subject + have/has + past participle\n- I/You/We/They + have + past participle\n- He/She/It + has + past participle\n\nExamples:\n- I have studied English for 3 years.\n- She has visited many countries.\n- They have just arrived.\n- He has never been to Japan.',
                    'level': 'amateur',
                    'topic_id': 1
                },
                {
                    'title': 'Past Continuous Tense',
                    'content': 'The Past Continuous Tense is used to:\n\n1. Describe actions in progress in the past: "I was reading when you called."\n2. Two actions happening at the same time: "While I was cooking, she was cleaning."\n3. Background actions: "It was raining when I left home."\n\nForm:\n- Subject + was/were + verb + ing\n- I/He/She/It + was + verb + ing\n- You/We/They + were + verb + ing\n\nExamples:\n- I was studying when the phone rang.\n- She was cooking dinner at 8 PM.\n- They were playing football in the rain.\n- He was working late last night.',
                    'level': 'amateur',
                    'topic_id': 2
                },
                {
                    'title': 'Modal Verbs (can, must, should)',
                    'content': 'Modal verbs express different meanings:\n\nCan:\n- Ability: "I can speak English."\n- Permission: "You can use my pen."\n- Possibility: "It can rain tomorrow."\n\nMust:\n- Necessity: "You must study hard."\n- Strong recommendation: "You must see this movie."\n- Certainty: "He must be at home."\n\nShould:\n- Advice: "You should exercise regularly."\n- Expectation: "He should arrive soon."\n- Recommendation: "You should try this restaurant."\n\nExamples:\n- I can help you with your homework.\n- You must finish this project today.\n- She should visit the doctor.\n- They can come to the party.',
                    'level': 'amateur',
                    'topic_id': 3
                },
                {
                    'title': 'Comparatives and Superlatives',
                    'content': 'Comparatives and Superlatives are used to compare things:\n\nComparatives:\n- Short adjectives: add -er: "big → bigger"\n- Long adjectives: use "more": "beautiful → more beautiful"\n- Use "than" to compare: "This car is bigger than that one."\n\nSuperlatives:\n- Short adjectives: add -est: "big → biggest"\n- Long adjectives: use "most": "beautiful → most beautiful"\n- Use "the" before superlatives: "This is the biggest car."\n\nExamples:\n- My house is bigger than yours.\n- She is more intelligent than her brother.\n- This is the most expensive car.\n- He is the tallest student in the class.',
                    'level': 'amateur',
                    'topic_id': 4
                },
                {
                    'title': 'Future with Going To',
                    'content': '"Going to" is used to express:\n\n1. Plans and intentions: "I am going to study medicine."\n2. Predictions based on evidence: "It is going to rain."\n3. Future arrangements: "We are going to have a party."\n\nForm:\n- Subject + be + going to + base form\n- I am going to + verb\n- He/She/It is going to + verb\n- You/We/They are going to + verb\n\nExamples:\n- I am going to visit my family next week.\n- She is going to start a new job.\n- They are going to buy a new house.\n- It is going to rain tomorrow.',
                    'level': 'amateur',
                    'topic_id': 5
                }
            ],
            'intermediate': [
                {
                    'title': 'Conditionals (Zero, First, Second)',
                    'content': 'Conditionals express different types of situations:\n\nZero Conditional:\n- General truths: "If you heat water, it boils."\n- Form: "If + present simple, present simple"\n\nFirst Conditional:\n- Real future possibilities: "If it rains, I will stay home."\n- Form: "If + present simple, will + base form"\n\nSecond Conditional:\n- Unreal or unlikely situations: "If I had money, I would travel."\n- Form: "If + past simple, would + base form"\n\nExamples:\n- If you don\'t study, you won\'t pass the exam.\n- If I were rich, I would help poor people.\n- If it rains tomorrow, we will cancel the picnic.',
                    'level': 'intermediate',
                    'topic_id': 1
                },
                {
                    'title': 'Present Perfect Continuous',
                    'content': 'The Present Perfect Continuous is used to:\n\n1. Emphasize duration: "I have been studying for 3 hours."\n2. Recent actions with visible results: "I have been working hard."\n3. Temporary situations: "I have been living here for 2 months."\n\nForm:\n- Subject + have/has + been + verb + ing\n- I/You/We/They + have + been + verb + ing\n- He/She/It + has + been + verb + ing\n\nExamples:\n- I have been studying English since morning.\n- She has been working on this project for weeks.\n- They have been waiting for the bus for 30 minutes.\n- He has been living in Tehran for 5 years.',
                    'level': 'intermediate',
                    'topic_id': 2
                },
                {
                    'title': 'Passive Voice',
                    'content': 'Passive voice is used when:\n\n1. The doer is unknown: "The letter was sent yesterday."\n2. The doer is not important: "Coffee is grown in Brazil."\n3. We want to emphasize the action: "The house was built in 1990."\n\nForm:\n- Present: "am/is/are + past participle"\n- Past: "was/were + past participle"\n- Future: "will be + past participle"\n\nExamples:\n- The book was written by Shakespeare.\n- English is spoken in many countries.\n- The house will be built next year.\n- The car was repaired yesterday.',
                    'level': 'intermediate',
                    'topic_id': 3
                },
                {
                    'title': 'Relative Clauses',
                    'content': 'Relative clauses give more information about nouns:\n\nDefining Clauses:\n- Essential information: "The man who lives next door is a doctor."\n- No commas\n\nNon-defining Clauses:\n- Extra information: "My brother, who lives in Paris, is a teacher."\n- Use commas\n\nRelative Pronouns:\n- Who: for people\n- Which: for things\n- That: for people and things\n- Where: for places\n- When: for time\n\nExamples:\n- The book that I bought is very interesting.\n- My sister, who is a doctor, lives in London.\n- The city where I was born is beautiful.',
                    'level': 'intermediate',
                    'topic_id': 4
                },
                {
                    'title': 'Reported Speech',
                    'content': 'Reported speech is used to report what someone said:\n\nChanges in Tenses:\n- Present Simple → Past Simple: "I like coffee" → "He said he liked coffee."\n- Present Continuous → Past Continuous: "I am working" → "He said he was working."\n- Will → Would: "I will help you" → "He said he would help me."\n\nChanges in Words:\n- Now → Then\n- Today → That day\n- Tomorrow → The next day\n- Here → There\n\nExamples:\n- "I am tired" → He said he was tired.\n- "I will come tomorrow" → She said she would come the next day.\n- "I live here" → He said he lived there.',
                    'level': 'intermediate',
                    'topic_id': 5
                }
            ],
            'advanced': [
                {
                    'title': 'Mixed Conditionals',
                    'content': 'Mixed conditionals combine different time references:\n\nPast → Present:\n- "If I had studied medicine, I would be a doctor now."\n- Past action affects present situation\n\nPast → Future:\n- "If I had saved money, I would buy a house next year."\n- Past action affects future possibility\n\nPresent → Past:\n- "If I were rich, I would have helped you yesterday."\n- Present condition affects past action\n\nExamples:\n- If I had learned to drive, I would be independent now.\n- If you had told me earlier, I would have helped you.\n- If I were you, I would have accepted the job offer.',
                    'level': 'advanced',
                    'topic_id': 1
                },
                {
                    'title': 'Inversion',
                    'content': 'Inversion is used for emphasis and formal style:\n\nNegative Inversion:\n- "Never have I seen such beauty."\n- "Rarely does he visit us."\n- "Seldom do we get such opportunities."\n\nConditional Inversion:\n- "Had I known, I would have helped."\n- "Were I rich, I would travel."\n- "Should you need help, call me."\n\nExamples:\n- Not only did he pass the exam, but he also got the highest score.\n- Hardly had I arrived when the phone rang.\n- Only then did I understand the truth.\n- No sooner had I left than it started raining.',
                    'level': 'advanced',
                    'topic_id': 2
                },
                {
                    'title': 'Cleft Sentences',
                    'content': 'Cleft sentences emphasize specific parts:\n\nIt-cleft:\n- "It was John who broke the window."\n- Emphasizes the subject\n\nWh-cleft:\n- "What I need is more time."\n- Emphasizes the object\n\nExamples:\n- It was in 1990 that I graduated.\n- What I want is a new car.\n- It was the weather that ruined our picnic.\n- What happened was that I lost my keys.\n- It was my mother who taught me to cook.',
                    'level': 'advanced',
                    'topic_id': 3
                },
                {
                    'title': 'Ellipsis and Substitution',
                    'content': 'Ellipsis and substitution avoid repetition:\n\nEllipsis:\n- Omitting words: "I can speak French, but she can\'t (speak French)."\n- "I like coffee, but he doesn\'t (like coffee)."\n\nSubstitution:\n- Using words to replace others: "I like this book. I like that one too."\n- "My car is red. What color is yours?"\n\nExamples:\n- I can swim, but she can\'t.\n- I have two cars. How many do you have?\n- I like this movie. Do you like it?\n- She is taller than I am.\n- I will help you if you want me to.',
                    'level': 'advanced',
                    'topic_id': 4
                },
                {
                    'title': 'Discourse Markers',
                    'content': 'Discourse markers connect ideas and show relationships:\n\nAddition:\n- Furthermore, Moreover, In addition\n- "Furthermore, the study shows..."\n\nContrast:\n- However, Nevertheless, On the other hand\n- "However, there are some problems..."\n\nCause and Effect:\n- Therefore, Consequently, As a result\n- "Therefore, we must act quickly."\n\nExamples:\n- The weather was bad. Nevertheless, we went hiking.\n- He studied hard. Therefore, he passed the exam.\n- On the one hand, it\'s expensive. On the other hand, it\'s high quality.\n- Furthermore, the research indicates...',
                    'level': 'advanced',
                    'topic_id': 5
                }
            ]
        }
        
        if all_lessons:
            return lessons.get(level, lessons['beginner'])
        return random.choice(lessons.get(level, lessons['beginner']))
    
    def populate_assessment_questions(self):
        """Populate assessment_questions table with initial data."""
        try:
            # Get assessment questions from fallback
            questions = self.get_fallback_assessment_questions(200) # Get more to ensure variety
            
            # Insert questions into database, avoiding duplicates
            for q in questions:
                options_str = '|'.join(q['options'])
                
                # Check if a similar question already exists
                self.cursor.execute(
                    "SELECT COUNT(*) FROM assessment_questions WHERE question = ? AND level = ?",
                    (q['question'], q['level'])
                )
                if self.cursor.fetchone()[0] == 0: # Only insert if not exists
                    self.cursor.execute(
                        "INSERT INTO assessment_questions (question, options, answer, level, type) VALUES (?, ?, ?, ?, ?)",
                        (q['question'], options_str, q['answer'], q['level'], 'multiple_choice')
                    )
            
            self.conn.commit()
            print(f"Populated assessment questions table with unique questions.")
        except Exception as e:
            print(f"Error populating assessment questions table: {e}")
    
    
    def get_mixed_assessment_questions(self, total_count=20):
        """Get a mix of assessment questions across different levels and types."""
        try:
            questions = []
            levels = ['beginner', 'amateur', 'intermediate', 'advanced']
            
            # Fetch all questions from the database first
            self.cursor.execute(
                "SELECT question, options, answer, level FROM assessment_questions ORDER BY id"
            )
            all_db_questions = []
            for row in self.cursor.fetchall():
                all_db_questions.append({
                    'question': row[0],
                    'options': row[1].split('|'),
                    'answer': row[2],
                    'level': row[3]
                })

            # If no questions in DB, use only fallback
            if not all_db_questions:
                all_db_questions = self.get_fallback_assessment_questions(200) # Get a large set from fallback

            # Shuffle all available questions (from DB or fallback) and pick unique ones
            random.shuffle(all_db_questions)
            
            selected_questions = []
            seen_question_texts = set()
            
            # Distribute questions by level if possible, else just pick unique ones
            per_level = total_count // len(levels)
            level_counts = {lvl: 0 for lvl in levels}
            
            for q_data in all_db_questions:
                if len(selected_questions) >= total_count:
                    break
                
                q_text = q_data['question'].lower().strip()
                q_level = q_data['level']
                
                if q_text not in seen_question_texts and level_counts[q_level] < per_level + (total_count % len(levels) if q_level == levels[-1] else 0): # Distribute remaining
                    selected_questions.append(q_data)
                    seen_question_texts.add(q_text)
                    level_counts[q_level] += 1
            
            # If still not enough, add more unique questions regardless of level distribution
            if len(selected_questions) < total_count:
                for q_data in all_db_questions:
                    if len(selected_questions) >= total_count:
                        break
                    q_text = q_data['question'].lower().strip()
                    if q_text not in seen_question_texts:
                        selected_questions.append(q_data)
                        seen_question_texts.add(q_text)

            # Ensure the final list is exactly total_count and randomly shuffled
            random.shuffle(selected_questions)
            return selected_questions[:total_count]
            
        except Exception as e:
            print(f"Error getting mixed assessment questions: {e}")
            # Fallback to general static questions if everything else fails
            fallback_q = self.get_fallback_assessment_questions(total_count)
            random.shuffle(fallback_q)
            return fallback_q[:total_count]
            
    def get_fallback_assessment_questions(self, count=20):
        """Fallback assessment questions when database fails or is empty."""
        questions = [
            # Beginner questions (5)
            { 'question': 'What is the correct word for "آب"?', 'options': ['Water', 'Air', 'Fire', 'Earth'], 'answer': 'Water', 'level': 'beginner' },
            { 'question': 'Which is the correct sentence?', 'options': ['She don\'t like coffee.', 'She doesn\'t like coffee.', 'She not like coffee.', 'She no like coffee.'], 'answer': 'She doesn\'t like coffee.', 'level': 'beginner' },
            { 'question': 'Complete the sentence: "I ___ to school every day."', 'options': ['going', 'goes', 'go', 'gone'], 'answer': 'go', 'level': 'beginner' },
            { 'question': 'What is the plural form of "child"?', 'options': ['Childs', 'Children', 'Childrens', 'Child'], 'answer': 'Children', 'level': 'beginner' },
            { 'question': 'Which word means "سلام"?', 'options': ['Goodbye', 'Hello', 'Thank you', 'Please'], 'answer': 'Hello', 'level': 'beginner' },
            
            # Amateur questions (5) - Ensured 'amateur' is used consistently
            { 'question': 'She _____ in that company for five years before she resigned.', 'options': ['worked', 'has worked', 'had worked', 'was working'], 'answer': 'had worked', 'level': 'amateur' },
            { 'question': 'If I _____ rich, I would buy a big house.', 'options': ['am', 'was', 'were', 'had been'], 'answer': 'were', 'level': 'amateur' },
            { 'question': 'Which sentence is grammatically correct?', 'options': ['I have been to Paris three times.', 'I have gone to Paris since three times.', 'I went to Paris for three times.', 'I am going to Paris three times.'], 'answer': 'I have been to Paris three times.', 'level': 'amateur' },
            { 'question': 'The movie was _____ boring that we left the theater.', 'options': ['such', 'so', 'too', 'very'], 'answer': 'so', 'level': 'amateur' },
            { 'question': 'She asked me _____ I could help her with the project.', 'options': ['what', 'that', 'if', 'when'], 'answer': 'if', 'level': 'amateur' },
            
            # Intermediate questions (5)
            { 'question': 'By next year, I _____ English for ten years.', 'options': ['will study', 'will have studied', 'will be studying', 'study'], 'answer': 'will have studied', 'level': 'intermediate' },
            { 'question': 'The book _____ I bought yesterday is very interesting.', 'options': ['which', 'what', 'who', 'whom'], 'answer': 'which', 'level': 'intermediate' },
            { 'question': 'He insisted _____ going to the party.', 'options': ['on', 'in', 'at', 'for'], 'answer': 'on', 'level': 'intermediate' },
            { 'question': 'The weather _____ getting worse.', 'options': ['is', 'are', 'was', 'were'], 'answer': 'is', 'level': 'intermediate' },
            { 'question': 'She _____ her homework before dinner.', 'options': ['finish', 'finishes', 'finished', 'has finished'], 'answer': 'finished', 'level': 'intermediate' },
            
            # Advanced questions (5)
            { 'question': 'Had I known about the problem earlier, I _____ able to solve it.', 'options': ['would be', 'would have been', 'will be', 'had been'], 'answer': 'would have been', 'level': 'advanced' },
            { 'question': 'The report, _____ was submitted last week, contains several errors.', 'options': ['who', 'whom', 'whose', 'which'], 'answer': 'which', 'level': 'advanced' },
            { 'question': 'Not only _____ the exam, but he also got the highest score.', 'options': ['he passed', 'passed he', 'did he pass', 'he did pass'], 'answer': 'did he pass', 'level': 'advanced' },
            { 'question': 'The professor with whom I studied linguistics _____ a new book next year.', 'options': ['publishes', 'is publishing', 'publish', 'published'], 'answer': 'is publishing', 'level': 'advanced' },
            { 'question': 'Which word is a synonym for "ambiguous"?', 'options': ['Clear', 'Vague', 'Precise', 'Definite'], 'answer': 'Vague', 'level': 'advanced' }
        ]
        # Return all questions from the fallback list for more options to pick from
        # No random.sample here to allow the calling function to handle uniqueness and count
        return questions
    
    def populate_vocabulary_table(self):
        """Populate vocabulary_words table with complete vocabulary data."""
        try:
            levels = ['beginner', 'amateur', 'intermediate', 'advanced']
            all_vocabulary = []

            for level in levels:
                words = self.get_fallback_vocabulary(level, 100)  # Get words for the current level
                for word_data in words:
                    # Add the level to each word dictionary
                    word_data['level'] = level
                    all_vocabulary.append(word_data)
            
            # Insert words into database
            for word_data in all_vocabulary:
                    try:
                        self.cursor.execute(
                            "INSERT INTO vocabulary_words (word, definition, example, level) VALUES (?, ?, ?, ?)",
                        (word_data['word'], word_data['definition'], word_data['example'], word_data['level'])
                        )
                    except sqlite3.IntegrityError:
                        # Word might already exist, skip it
                        continue
            
            self.conn.commit()
            print(f"Populated vocabulary table with {len(all_vocabulary)} words for all levels")
        except Exception as e:
            print(f"Error populating vocabulary table: {e}")    
    
    def populate_grammar_lessons(self):
        """Populate grammar_lessons table with complete grammar data."""
        try:
            # Get all grammar lessons for each level
            levels = ['beginner', 'amateur', 'intermediate', 'advanced']
            
            for level in levels:
                lessons = self.get_fallback_grammar_lesson(level, all_lessons=True)
                
                for lesson in lessons:
                    try:
                        self.cursor.execute(
                "INSERT INTO grammar_lessons (title, content, level) VALUES (?, ?, ?)",
                            (lesson['title'], lesson['content'], level)
                        )
                    except Exception:
                        # Lesson might already exist, skip it
                        continue
            
            self.conn.commit()
            print(f"Populated grammar lessons table with lessons for all levels")
        except Exception as e:
            print(f"Error populating grammar lessons table: {e}")
    
    
    def populate_assessment_questions(self):
        """Populate assessment_questions table with initial data."""
        try:
            # Get assessment questions from fallback
            questions = self.get_fallback_assessment_questions(200) # Get more to ensure variety
            
            # Insert questions into database, avoiding duplicates
            for q in questions:
                options_str = '|'.join(q['options'])
                
                # Check if a similar question already exists
                self.cursor.execute(
                    "SELECT COUNT(*) FROM assessment_questions WHERE question = ? AND level = ?",
                    (q['question'], q['level'])
                )
                if self.cursor.fetchone()[0] == 0: # Only insert if not exists
                    self.cursor.execute(
                        "INSERT INTO assessment_questions (question, options, answer, level, type) VALUES (?, ?, ?, ?, ?)",
                        (q['question'], options_str, q['answer'], q['level'], 'multiple_choice')
                    )
            
            self.conn.commit()
            print(f"Populated assessment questions table with unique questions.")
        except Exception as e:
            print(f"Error populating assessment questions table: {e}")
    
    
    def populate_conversation_topics(self):
        """Populate conversation_topics table with complete conversation data."""
        try:
            levels = ['beginner', 'amateur', 'intermediate', 'advanced']
            
            for level in levels:
                # Use the internal method to get all static topics for the level
                level_topics = self._get_static_conversation_topics(level)
                
                for topic in level_topics:
                    if isinstance(topic, dict):
                        try:
                            self.cursor.execute(
                                "INSERT INTO conversation_topics (title, description, starter, level, topic_id) VALUES (?, ?, ?, ?, ?)",
                                (topic['title'], topic['description'], topic['starter'], topic['level'], topic['topic_id'])
                            )
                        except sqlite3.IntegrityError:
                            # Topic might already exist, skip it
                            continue
            
            self.conn.commit()
            print(f"Populated conversation topics table with topics for all levels")
        except Exception as e:
            print(f"Error populating conversation topics table: {e}")
    

    def get_fallback_conversation_topics(self, user_id, level):
        """Get conversation topics for a specific level, first from database then fallback."""
        try:
            # First try to get topics from database
            self.cursor.execute(
                "SELECT title, description, starter, level, topic_id FROM conversation_topics WHERE level = ? ORDER BY topic_id",
                (level,)
            )
            db_topics = []
            for row in self.cursor.fetchall():
                db_topics.append({
                    'title': row[0],
                    'description': row[1],
                    'starter': row[2],
                    'level': row[3],
                    'topic_id': row[4]
                })
            
            # If database has topics, use them
            if db_topics:
                all_topics = db_topics
                print(f"Found {len(db_topics)} topics in database for level {level}")
            else:
                # Fallback to static topics
                all_topics = self._get_static_conversation_topics(level)
                print(f"Using {len(all_topics)} static topics for level {level}")
            
            # If no user_id provided, just return a random topic
            if user_id is None:
                selected_topic = random.choice(all_topics)
                print(f"Random topic selected for level {level}: {selected_topic['title']}")
                return selected_topic
                
            # Get seen topics for this user
            seen = self.get_seen_conversation_topics(user_id, level)
            available = [t for t in all_topics if t['topic_id'] not in seen]
            
            print(f"User {user_id} has seen {len(seen)} topics, {len(available)} available at level {level}")
            
            if not available:
                print(f"All topics seen for user {user_id} at level {level}, resetting...")
                self.reset_conversation_seen(user_id, level)
                available = all_topics
            
            selected_topic = random.choice(available)
            self.add_conversation_seen(user_id, selected_topic['topic_id'], level)
            print(f"Selected topic for user {user_id}: {selected_topic['title']}")
            return selected_topic
            
        except Exception as e:
            print(f"Error getting conversation topics for level {level}: {e}")
            # Fallback to static topics
            return self._get_static_conversation_topics(level)
    
    def _get_static_conversation_topics(self, level):
        """Get static conversation topics as fallback."""
        topics = {
            'beginner': [
                {
                    'title': 'Introduce yourself',
                    'description': 'Tell me about yourself - your name, age, where you live, and what you do.',
                    'starter': 'Hello! My name is...',
                    'level': 'beginner',
                    'topic_id': 1
                },
                {
                    'title': 'Talk about your family',
                    'description': 'Describe your family members - who they are, what they do, and how many people are in your family.',
                    'starter': 'I have a family with...',
                    'level': 'beginner',
                    'topic_id': 2
                },
                {
                    'title': 'Describe your house',
                    'description': 'Tell me about where you live - the rooms, furniture, and what you like about your home.',
                    'starter': 'I live in a house that has...',
                    'level': 'beginner',
                    'topic_id': 3
                },
                {
                    'title': 'Talk about your favorite food',
                    'description': 'What foods do you like? Describe your favorite meals and why you enjoy them.',
                    'starter': 'My favorite food is...',
                    'level': 'beginner',
                    'topic_id': 4
                },
                {
                    'title': 'Describe your daily routine',
                    'description': 'What do you do every day? Talk about your morning, afternoon, and evening activities.',
                    'starter': 'Every day I usually...',
                    'level': 'beginner',
                    'topic_id': 5
                }
            ],
            'amateur': [
                {
                    'title': 'Talk about your hobbies',
                    'description': 'What do you like to do in your free time? Describe your hobbies and why you enjoy them.',
                    'starter': 'In my free time, I like to...',
                    'level': 'amateur',
                    'topic_id': 1
                },
                {
                    'title': 'Describe a memorable trip',
                    'description': 'Tell me about a trip you remember well - where you went, what you did, and why it was special.',
                    'starter': 'I remember a trip when I...',
                    'level': 'amateur',
                    'topic_id': 2
                },
                {
                    'title': 'Talk about your school or job',
                    'description': 'Describe your school or workplace - what you study or do, and how you feel about it.',
                    'starter': 'I study/work at...',
                    'level': 'amateur',
                    'topic_id': 3
                },
                {
                    'title': 'Describe your best friend',
                    'description': 'Tell me about your best friend - how you met, what they are like, and why you are friends.',
                    'starter': 'My best friend is...',
                    'level': 'amateur',
                    'topic_id': 4
                },
                {
                    'title': 'Talk about your weekend plans',
                    'description': 'What are you planning to do this weekend? Describe your plans and why you chose these activities.',
                    'starter': 'This weekend I plan to...',
                    'level': 'amateur',
                    'topic_id': 5
                }
            ],
            'intermediate': [
                {
                    'title': 'Discuss a book or movie you like',
                    'description': 'Tell me about a book or movie that impressed you - what it was about and why you recommend it.',
                    'starter': 'I recently read/watched...',
                    'level': 'intermediate',
                    'topic_id': 1
                },
                {
                    'title': 'Talk about technology in your life',
                    'description': 'How does technology affect your daily life? Discuss the devices you use and their impact.',
                    'starter': 'Technology plays an important role in my life because...',
                    'level': 'intermediate',
                    'topic_id': 2
                },
                {
                    'title': 'Describe a problem you solved',
                    'description': 'Tell me about a challenging situation you faced and how you managed to solve it.',
                    'starter': 'I once faced a problem when...',
                    'level': 'intermediate',
                    'topic_id': 3
                },
                {
                    'title': 'Talk about your goals for the future',
                    'description': 'What are your plans and dreams for the future? Discuss your career and personal goals.',
                    'starter': 'In the future, I hope to...',
                    'level': 'intermediate',
                    'topic_id': 4
                },
                {
                    'title': 'Discuss a cultural tradition',
                    'description': 'Tell me about an important tradition or custom in your culture and why it matters to you.',
                    'starter': 'In my culture, we have a tradition of...',
                    'level': 'intermediate',
                    'topic_id': 5
                }
            ],
            'advanced': [
                {
                    'title': 'Debate a current event',
                    'description': 'Choose a current news topic and discuss different perspectives on the issue.',
                    'starter': 'I think the current situation with...',
                    'level': 'advanced',
                    'topic_id': 1
                },
                {
                    'title': 'Discuss environmental issues',
                    'description': 'What environmental challenges do you think are most important? Discuss solutions and personal responsibility.',
                    'starter': 'Environmental protection is crucial because...',
                    'level': 'advanced',
                    'topic_id': 2
                },
                {
                    'title': 'Talk about the impact of social media',
                    'description': 'How has social media changed society? Discuss both positive and negative effects.',
                    'starter': 'Social media has transformed the way we...',
                    'level': 'advanced',
                    'topic_id': 3
                },
                {
                    'title': 'Discuss education systems',
                    'description': 'What do you think about modern education? Discuss different approaches and what could be improved.',
                    'starter': 'I believe education should focus on...',
                    'level': 'advanced',
                    'topic_id': 4
                },
                {
                    'title': 'Debate the pros and cons of globalization',
                    'description': 'What are the benefits and drawbacks of globalization? Discuss economic and cultural impacts.',
                    'starter': 'Globalization has both advantages and disadvantages...',
                    'level': 'advanced',
                    'topic_id': 5
                }
            ]
        }
        
        return topics.get(level, topics['beginner'])
    
    def get_seen_conversation_topics(self, user_id, level):
        """Get conversation topics that a user has already seen for a specific level."""
        try:
            self.user_cursor.execute(
                "SELECT topic_id FROM user_conversation WHERE user_id = ? AND level = ?",
                (user_id, level)
            )
            seen_topics = set(row[0] for row in self.user_cursor.fetchall())
            print(f"User {user_id} has seen {len(seen_topics)} topics at level {level}")
            return seen_topics
        except Exception as e:
            print(f"Error getting seen conversation topics for user {user_id}: {e}")
            return set()
    
    def add_conversation_seen(self, user_id, topic_id, level):
        """Mark a conversation topic as seen by a user."""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.user_cursor.execute(
                "INSERT INTO user_conversation (user_id, topic_id, level, seen_at) VALUES (?, ?, ?, ?)",
                (user_id, topic_id, level, now)
            )
            self.user_conn.commit()
        except Exception as e:
            print(f"Error adding conversation seen for user {user_id}: {e}")
    
    def reset_conversation_seen(self, user_id, level):
        """Reset seen conversation topics for a user at a specific level."""
        try:
            self.user_cursor.execute(
                "DELETE FROM user_conversation WHERE user_id = ? AND level = ?",
                (user_id, level)
            )
            self.user_conn.commit()
            print(f"Reset conversation seen for user {user_id} at level {level}")
        except Exception as e:
            print(f"Error resetting conversation seen for user {user_id}: {e}")

    def get_total_vocabulary_count(self, level):
        """Get total number of vocabulary words for a level."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM vocabulary_words WHERE level = ?", (level,))
            count = self.cursor.fetchone()[0]
            if count == 0:
                # Fallback
                return len(self.get_fallback_vocabulary(level, 200))
            return count
        except Exception as e:
            print(f"Error getting vocabulary count for level {level}: {e}")
            # Fallback
            return len(self.get_fallback_vocabulary(level, 200))

    
    def get_total_grammar_count(self, level):
        """Get total number of grammar lessons for a level."""
        try:
            # First, try to get the count from the database
            self.cursor.execute("SELECT COUNT(*) FROM grammar_lessons WHERE level = ?", (level,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                return count
            
            # If the database is empty, fall back to the static list
            all_lessons = self.get_fallback_grammar_lesson(level, all_lessons=True)
            return len(all_lessons) if all_lessons else 0
        except Exception as e:
            print(f"Error getting total grammar count: {e}")
            return 5 # Fallback to a default of 5 if everything fails

    
    
    def get_total_conversation_count(self, level):
        """Get total number of conversation topics for a level."""
        try:
            # First, try to get the count from the database
            self.cursor.execute("SELECT COUNT(*) FROM conversation_topics WHERE level = ?", (level,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                return count
            
            # If the database is empty, fall back to the static list
            all_topics = self._get_static_conversation_topics(level)
            return len(all_topics) if all_topics else 0
        except Exception as e:
            print(f"Error getting conversation count for level {level}: {e}")
            return 5 # Fallback to a default of 5 if everything fails
    
    def check_duplicate_vocabulary(self):
        """Check for duplicate vocabulary words across all levels in the database."""
        self.cursor.execute("SELECT word, level FROM vocabulary_words")
        all_db_words = self.cursor.fetchall()

        all_words_map = {}
        for word_text, level in all_db_words:
            normalized_word = word_text.lower()
            if normalized_word not in all_words_map:
                all_words_map[normalized_word] = []
            all_words_map[normalized_word].append(level)
        
        return {w: lvls for w, lvls in all_words_map.items() if len(lvls) > 1}

    def check_duplicate_grammar(self):
        """Check for duplicate grammar lesson titles across all levels in the database."""
        self.cursor.execute("SELECT title, level FROM grammar_lessons")
        all_db_lessons = self.cursor.fetchall()

        all_titles_map = {}
        for title_text, level in all_db_lessons:
            normalized_title = title_text.strip().lower()
            if normalized_title not in all_titles_map:
                all_titles_map[normalized_title] = []
            all_titles_map[normalized_title].append(level)
        
        return {t: lvls for t, lvls in all_titles_map.items() if len(lvls) > 1}

    def check_duplicate_conversation(self):
        """Check for duplicate conversation topics across all levels in the database."""
        self.cursor.execute("SELECT title, level FROM conversation_topics")
        all_db_topics = self.cursor.fetchall()

        all_titles_map = {}
        for title_text, level in all_db_topics:
            normalized_title = title_text.strip().lower()
            if normalized_title not in all_titles_map:
                all_titles_map[normalized_title] = []
            all_titles_map[normalized_title].append(level)
        
        return {t: lvls for t, lvls in all_titles_map.items() if len(lvls) > 1}


    def remove_duplicate_vocabulary(self):
        """Remove duplicate vocabulary words, keeping the word in the lowest level from the database."""
        try:
            # Get all words from the database, ordered by level priority (beginner, amateur, intermediate, advanced)
            # and then by ID to keep the earliest entry in case of same level duplicates
            self.cursor.execute("""
                SELECT word, level, id FROM vocabulary_words 
                ORDER BY 
                    CASE level
                        WHEN 'beginner' THEN 1
                        WHEN 'amateur' THEN 2
                        WHEN 'intermediate' THEN 3
                        WHEN 'advanced' THEN 4
                        ELSE 5
                    END,
                    id ASC
            """)
            all_db_words = self.cursor.fetchall()

            seen_words = set()
            words_to_delete_ids = []

            for word_text, level, word_id in all_db_words:
                normalized_word = word_text.lower()
                if normalized_word in seen_words:
                    words_to_delete_ids.append(word_id)
                else:
                    seen_words.add(normalized_word)
            
            if words_to_delete_ids:
                # Delete duplicate words from the database
                placeholders = ','.join('?' * len(words_to_delete_ids))
                self.cursor.execute(f"DELETE FROM vocabulary_words WHERE id IN ({placeholders})", words_to_delete_ids)
                self.conn.commit()
                print(f"Removed {len(words_to_delete_ids)} duplicate vocabulary words from the database.")
            else:
                print("No duplicate vocabulary words found in the database to remove.")

        except Exception as e:
            print(f"Error removing duplicate vocabulary from DB: {e}")
    
    def remove_duplicate_grammar(self):
        """Remove duplicate grammar lessons, keeping the lesson in the lowest level from the database."""
        try:
            # Get all lessons from the database, ordered by level priority
            self.cursor.execute("""
                SELECT title, level, id FROM grammar_lessons 
                ORDER BY 
                    CASE level
                        WHEN 'beginner' THEN 1
                        WHEN 'amateur' THEN 2
                        WHEN 'intermediate' THEN 3
                        WHEN 'advanced' THEN 4
                        ELSE 5
                    END,
                    id ASC
            """)
            all_db_lessons = self.cursor.fetchall()

            seen_titles = set()
            lessons_to_delete_ids = []

            for title_text, level, lesson_id in all_db_lessons:
                normalized_title = title_text.strip().lower()
                if normalized_title in seen_titles:
                    lessons_to_delete_ids.append(lesson_id)
                else:
                    seen_titles.add(normalized_title)
            
            if lessons_to_delete_ids:
                # Delete duplicate lessons from the database
                placeholders = ','.join('?' * len(lessons_to_delete_ids))
                self.cursor.execute(f"DELETE FROM grammar_lessons WHERE id IN ({placeholders})", lessons_to_delete_ids)
                self.conn.commit()
                print(f"Removed {len(lessons_to_delete_ids)} duplicate grammar lessons from the database.")
            else:
                print("No duplicate grammar lessons found in the database to remove.")

        except Exception as e:
            print(f"Error removing duplicate grammar from DB: {e}")
    
    def remove_duplicate_conversation(self):
        """Remove duplicate conversation topics, keeping the topic in the lowest level from the database."""
        try:
            # Get all topics from the database, ordered by level priority
            self.cursor.execute("""
                SELECT title, level, id FROM conversation_topics 
                ORDER BY 
                    CASE level
                        WHEN 'beginner' THEN 1
                        WHEN 'amateur' THEN 2
                        WHEN 'intermediate' THEN 3
                        WHEN 'advanced' THEN 4
                        ELSE 5
                    END,
                    id ASC
            """)
            all_db_topics = self.cursor.fetchall()

            seen_titles = set()
            topics_to_delete_ids = []

            for title_text, level, topic_id in all_db_topics:
                normalized_title = title_text.strip().lower()
                if normalized_title in seen_titles:
                    topics_to_delete_ids.append(topic_id)
                else:
                    seen_titles.add(normalized_title)
            
            if topics_to_delete_ids:
                # Delete duplicate topics from the database
                placeholders = ','.join('?' * len(topics_to_delete_ids))
                self.cursor.execute(f"DELETE FROM conversation_topics WHERE id IN ({placeholders})", topics_to_delete_ids)
                self.conn.commit()
                print(f"Removed {len(topics_to_delete_ids)} duplicate conversation topics from the database.")
            else:
                print("No duplicate conversation topics found in the database to remove.")

        except Exception as e:
            print(f"Error removing duplicate conversation from DB: {e}")
    
    def run_content_deduplication_report(self):
        """Check and remove duplicates, print a report."""
        vocab_dupes = self.check_duplicate_vocabulary()
        grammar_dupes = self.check_duplicate_grammar()
        conv_dupes = self.check_duplicate_conversation()
        if vocab_dupes:
            print("[DEDUP] Duplicate vocabulary words found:")
            for w, lvls in vocab_dupes.items():
                print(f"  {w}: {lvls}")
            self.remove_duplicate_vocabulary()
        else:
            print("[DEDUP] No duplicate vocabulary words.")
        if grammar_dupes:
            print("[DEDUP] Duplicate grammar lesson titles found:")
            for t, lvls in grammar_dupes.items():
                print(f"  {t}: {lvls}")
            self.remove_duplicate_grammar()
        else:
            print("[DEDUP] No duplicate grammar lessons.")
        if conv_dupes:
            print("[DEDUP] Duplicate conversation topics found:")
            for t, lvls in conv_dupes.items():
                print(f"  {t}: {lvls}")
            self.remove_duplicate_conversation()
        else:
            print("[DEDUP] No duplicate conversation topics.")