import sqlite3
import random
import os
from vocab_data import beginner_words, elementary_words, intermediate_words, advanced_words

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
            
            self.conn.commit()
            
            # Check if vocabulary table has data
            self.cursor.execute("SELECT COUNT(*) FROM vocabulary_words")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # Populate with initial data
                self.populate_vocabulary_table()
                self.populate_grammar_lessons()
                self.populate_assessment_questions()
        
        except Exception as e:
            print(f"Error initializing content database: {e}")
    
    def get_vocabulary_for_level(self, user_id, level, count=5):
        """Get vocabulary words for a specific level, excluding words the user has already studied."""
        try:
            # First try from database, excluding words the user has studied
            self.cursor.execute(
                """
                SELECT vw.word, vw.definition, vw.example 
                FROM vocabulary_words vw
                LEFT JOIN (
                    SELECT word FROM vocabulary WHERE user_id = ?
                ) uv ON vw.word = uv.word
                WHERE vw.level = ? AND uv.word IS NULL
                ORDER BY RANDOM() 
                LIMIT ?
                """,
                (user_id, level, count)
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
                
                # Filter out words user has already studied from fallback
                studied_words = self.get_studied_words(user_id)
                fallback_words = [word for word in fallback_words if word['word'] not in studied_words]
                
                words.extend(fallback_words)
                
                # Try to save fallback words to database for future use
                for word in fallback_words:
                    try:
                        self.cursor.execute(
                            "INSERT INTO vocabulary_words (word, definition, example, level) VALUES (?, ?, ?, ?)",
                            (word['word'], word['definition'], word['example'], level)
                        )
                    except Exception:
                        # Might already exist, ignore
                        pass
                
                self.conn.commit()
                
            return words
        except Exception as e:
            print(f"Error getting vocabulary for level {level} for user {user_id}: {e}")
            # Fallback to static lists and filter out studied words
            fallback_words = self.get_fallback_vocabulary(level, count)
            studied_words = self.get_studied_words(user_id)
            return [word for word in fallback_words if word['word'] not in studied_words]
            
    def get_grammar_lesson_for_level(self, user_id, level):
        """Get a grammar lesson for the specified level, avoiding repeats."""
        lessons = self.get_fallback_grammar_lesson(level, all_lessons=True)
        seen_titles = self.get_seen_grammar_titles(user_id, level)
        available = [l for l in lessons if l['title'] not in seen_titles]
        if not available:
            self.reset_grammar_seen(user_id, level)
            available = lessons
        lesson = random.choice(available)
        self.add_grammar_seen(user_id, lesson['title'], level)
        return lesson
    
    def get_mixed_assessment_questions(self, total_count=15):
        """Get a mix of assessment questions across different levels and types."""
        try:
            questions = []
            # 25% for each level
            per_level = total_count // 4
            levels = ['beginner', 'amatur', 'intermediate', 'advanced']
            for lvl in levels:
                self.cursor.execute(
                    "SELECT question, options, answer, level FROM assessment_questions WHERE level = ? ORDER BY RANDOM() LIMIT ?",
                    (lvl, per_level)
                )
                for row in self.cursor.fetchall():
                    questions.append({
                        'question': row[0],
                        'options': row[1].split('|'),
                        'answer': row[2],
                        'level': row[3]
                    })
            # If not enough, fallback to static
            if len(questions) < total_count:
                fallback = self.get_fallback_assessment_questions(total_count - len(questions))
                questions.extend(fallback)
            random.shuffle(questions)
            return questions
        except Exception as e:
            print(f"Error getting mixed assessment questions: {e}")
            return self.get_fallback_assessment_questions(total_count)
    
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
            'beginner': beginner_words,
            'elementary': [w for w in elementary_words if w['word'].lower() not in [bw['word'].lower() for bw in beginner_words]],
            'intermediate': [w for w in intermediate_words if w['word'].lower() not in [bw['word'].lower() for bw in beginner_words] + [ew['word'].lower() for ew in elementary_words]],
            'advanced': [w for w in advanced_words if w['word'].lower() not in [bw['word'].lower() for bw in beginner_words] + [ew['word'].lower() for ew in elementary_words] + [iw['word'].lower() for iw in intermediate_words]]
        }
        level_vocab = vocabulary.get(level, vocabulary['beginner'])
        return random.sample(level_vocab, min(count, len(level_vocab)))
    
    def get_fallback_grammar_lesson(self, level, all_lessons=False):
        """Fallback grammar lessons when database fails or is empty."""
        lessons = {
            'beginner': [
                {'title': 'Simple Present Tense', 'content': '...'},
                {'title': 'Simple Past Tense', 'content': '...'},
                {'title': 'There is/There are', 'content': '...'},
                {'title': 'Countable and Uncountable Nouns', 'content': '...'},
                {'title': 'Prepositions of Place', 'content': '...'},
                {'title': 'Present Continuous Tense', 'content': '...'},
                {'title': 'Articles (a/an/the)', 'content': '...'},
                {'title': 'Possessive Adjectives', 'content': '...'},
                {'title': 'Imperatives', 'content': '...'},
                {'title': 'Question Words', 'content': '...'}
            ],
            'amatur': [
                {'title': 'Comparatives and Superlatives', 'content': '...'},
                {'title': 'Future with going to', 'content': '...'},
                {'title': 'Modal Verbs (can, must, should)', 'content': '...'},
                {'title': 'Adverbs of Frequency', 'content': '...'},
                {'title': 'Present Perfect Tense', 'content': '...'},
                {'title': 'Past Continuous Tense', 'content': '...'},
                {'title': 'Gerunds and Infinitives', 'content': '...'},
                {'title': 'Relative Clauses', 'content': '...'},
                {'title': 'Passive Voice', 'content': '...'},
                {'title': 'Reported Speech', 'content': '...'}
            ],
            'intermediate': [
                {'title': 'Conditionals (Zero, First, Second)', 'content': '...'},
                {'title': 'Wish and If Only', 'content': '...'},
                {'title': 'Causative Verbs', 'content': '...'},
                {'title': 'Direct and Indirect Speech', 'content': '...'},
                {'title': 'Phrasal Verbs', 'content': '...'},
                {'title': 'Quantifiers', 'content': '...'},
                {'title': 'Inversion', 'content': '...'},
                {'title': 'Cleft Sentences', 'content': '...'},
                {'title': 'Nominalization', 'content': '...'},
                {'title': 'Advanced Modal Verbs', 'content': '...'}
            ],
            'advanced': [
                {'title': 'Mixed Conditionals', 'content': '...'},
                {'title': 'Ellipsis and Substitution', 'content': '...'},
                {'title': 'Discourse Markers', 'content': '...'},
                {'title': 'Emphatic Structures', 'content': '...'},
                {'title': 'Collocations', 'content': '...'},
                {'title': 'Idioms and Fixed Expressions', 'content': '...'},
                {'title': 'Formal and Informal English', 'content': '...'},
                {'title': 'Academic Writing Structures', 'content': '...'},
                {'title': 'Paraphrasing Techniques', 'content': '...'},
                {'title': 'Register and Style', 'content': '...'}
            ]
        }
        if all_lessons:
            return lessons.get(level, lessons['beginner'])
        return random.choice(lessons.get(level, lessons['beginner']))
    
    def get_fallback_assessment_questions(self, count=15):
        """Fallback assessment questions when database fails or is empty."""
        questions = [
            # Beginner questions
            { 'question': 'What is the correct word for "آب"?', 'options': ['Water', 'Air', 'Fire', 'Earth'], 'answer': 'Water', 'level': 'beginner' },
            { 'question': 'Which is the correct sentence?', 'options': ['She don\'t like coffee.', 'She doesn\'t like coffee.', 'She not like coffee.', 'She no like coffee.'], 'answer': 'She doesn\'t like coffee.', 'level': 'beginner' },
            { 'question': 'Complete the sentence: "I ___ to school every day."', 'options': ['going', 'goes', 'go', 'gone'], 'answer': 'go', 'level': 'beginner' },
            { 'question': 'What is the plural form of "child"?', 'options': ['Childs', 'Children', 'Childrens', 'Child'], 'answer': 'Children', 'level': 'beginner' },
            { 'question': 'Which word means "سلام"?', 'options': ['Goodbye', 'Hello', 'Thank you', 'Please'], 'answer': 'Hello', 'level': 'beginner' },
            # Amatur questions (copy of intermediate for now)
            { 'question': 'She _____ in that company for five years before she resigned.', 'options': ['worked', 'has worked', 'had worked', 'was working'], 'answer': 'had worked', 'level': 'amatur' },
            { 'question': 'If I _____ rich, I would buy a big house.', 'options': ['am', 'was', 'were', 'had been'], 'answer': 'were', 'level': 'amatur' },
            { 'question': 'Which sentence is grammatically correct?', 'options': ['I have been to Paris three times.', 'I have gone to Paris since three times.', 'I went to Paris for three times.', 'I am going to Paris three times.'], 'answer': 'I have been to Paris three times.', 'level': 'amatur' },
            { 'question': 'The movie was _____ boring that we left the theater.', 'options': ['such', 'so', 'too', 'very'], 'answer': 'so', 'level': 'amatur' },
            { 'question': 'She asked me _____ I could help her with the project.', 'options': ['what', 'that', 'if', 'when'], 'answer': 'if', 'level': 'amatur' },
            # Intermediate questions
            { 'question': 'She _____ in that company for five years before she resigned.', 'options': ['worked', 'has worked', 'had worked', 'was working'], 'answer': 'had worked', 'level': 'intermediate' },
            { 'question': 'If I _____ rich, I would buy a big house.', 'options': ['am', 'was', 'were', 'had been'], 'answer': 'were', 'level': 'intermediate' },
            { 'question': 'Which sentence is grammatically correct?', 'options': ['I have been to Paris three times.', 'I have gone to Paris since three times.', 'I went to Paris for three times.', 'I am going to Paris three times.'], 'answer': 'I have been to Paris three times.', 'level': 'intermediate' },
            { 'question': 'The movie was _____ boring that we left the theater.', 'options': ['such', 'so', 'too', 'very'], 'answer': 'so', 'level': 'intermediate' },
            { 'question': 'She asked me _____ I could help her with the project.', 'options': ['what', 'that', 'if', 'when'], 'answer': 'if', 'level': 'intermediate' },
            # Advanced questions
            { 'question': 'Had I known about the problem earlier, I _____ able to solve it.', 'options': ['would be', 'would have been', 'will be', 'had been'], 'answer': 'would have been', 'level': 'advanced' },
            { 'question': 'The report, _____ was submitted last week, contains several errors.', 'options': ['who', 'whom', 'whose', 'which'], 'answer': 'which', 'level': 'advanced' },
            { 'question': 'Not only _____ the exam, but he also got the highest score.', 'options': ['he passed', 'passed he', 'did he pass', 'he did pass'], 'answer': 'did he pass', 'level': 'advanced' },
            { 'question': 'The professor with whom I studied linguistics _____ a new book next year.', 'options': ['publishes', 'is publishing', 'publish', 'published'], 'answer': 'is publishing', 'level': 'advanced' },
            { 'question': 'Which word is a synonym for "ambiguous"?', 'options': ['Clear', 'Vague', 'Precise', 'Definite'], 'answer': 'Vague', 'level': 'advanced' }
        ]
        return random.sample(questions, min(count, len(questions)))
    
    def populate_vocabulary_table(self):
        """Populate vocabulary_words table with initial data."""
        try:
            # Get vocabulary words for each level using the deduplicated lists
            vocabulary = {
                'beginner': beginner_words,
                'elementary': [w for w in elementary_words if w['word'].lower() not in [bw['word'].lower() for bw in beginner_words]],
                'intermediate': [w for w in intermediate_words if w['word'].lower() not in [bw['word'].lower() for bw in beginner_words] + [ew['word'].lower() for ew in elementary_words]],
                'advanced': [w for w in advanced_words if w['word'].lower() not in [bw['word'].lower() for bw in beginner_words] + [ew['word'].lower() for ew in elementary_words] + [iw['word'].lower() for iw in intermediate_words]]
            }
            
            # Insert words into database
            for level, words in vocabulary.items():
                for word in words:
                    try:
                        self.cursor.execute(
                            "INSERT INTO vocabulary_words (word, definition, example, level) VALUES (?, ?, ?, ?)",
                            (word['word'], word['definition'], word['example'], level)
                        )
                    except Exception:
                        # Word might already exist, skip it
                        continue
            
            self.conn.commit()
            print(f"Populated vocabulary table with words for all levels")
        except Exception as e:
            print(f"Error populating vocabulary table: {e}")
    
    def populate_grammar_lessons(self):
        """Populate grammar_lessons table with initial data."""
        try:
            # Get grammar lessons for each level
            beginner_lesson = self.get_fallback_grammar_lesson('beginner')
            intermediate_lesson = self.get_fallback_grammar_lesson('intermediate')
            advanced_lesson = self.get_fallback_grammar_lesson('advanced')
            
            # Insert lessons into database
            self.cursor.execute(
                "INSERT INTO grammar_lessons (title, content, level) VALUES (?, ?, ?)",
                (beginner_lesson['title'], beginner_lesson['content'], 'beginner')
            )
            
            self.cursor.execute(
                "INSERT INTO grammar_lessons (title, content, level) VALUES (?, ?, ?)",
                (intermediate_lesson['title'], intermediate_lesson['content'], 'intermediate')
            )
            
            self.cursor.execute(
                "INSERT INTO grammar_lessons (title, content, level) VALUES (?, ?, ?)",
                (advanced_lesson['title'], advanced_lesson['content'], 'advanced')
            )
            
            self.conn.commit()
            print("Populated grammar lessons table with 3 lessons")
        except Exception as e:
            print(f"Error populating grammar lessons table: {e}")
    
    def populate_assessment_questions(self):
        """Populate assessment_questions table with initial data."""
        try:
            # Get assessment questions
            questions = self.get_fallback_assessment_questions(15)
            
            # Insert questions into database
            for q in questions:
                options_str = '|'.join(q['options'])
                self.cursor.execute(
                    "INSERT INTO assessment_questions (question, options, answer, level, type) VALUES (?, ?, ?, ?, ?)",
                    (q['question'], options_str, q['answer'], q['level'], 'multiple_choice')
                )
            
            self.conn.commit()
            print(f"Populated assessment questions table with {len(questions)} questions")
        except Exception as e:
            print(f"Error populating assessment questions table: {e}")

    def get_fallback_conversation_topics(self, user_id, level):
        """Fallback conversation topics for each level, avoiding repeats."""
        topics = {
            'beginner': [
                'Introduce yourself',
                'Talk about your family',
                'Describe your house',
                'Talk about your favorite food',
                'Describe your daily routine',
            ],
            'amatur': [
                'Talk about your hobbies',
                'Describe a memorable trip',
                'Talk about your school or job',
                'Describe your best friend',
                'Talk about your weekend plans',
            ],
            'intermediate': [
                'Discuss a book or movie you like',
                'Talk about technology in your life',
                'Describe a problem you solved',
                'Talk about your goals for the future',
                'Discuss a cultural tradition',
            ],
            'advanced': [
                'Debate a current event',
                'Discuss environmental issues',
                'Talk about the impact of social media',
                'Discuss education systems',
                'Debate the pros and cons of globalization',
            ]
        }
        all_topics = topics.get(level, topics['beginner'])
        seen = self.get_seen_conversation_topics(user_id, level)
        available = [t for t in all_topics if t not in seen]
        if not available:
            self.reset_conversation_seen(user_id, level)
            available = all_topics
        topic = random.choice(available)
        self.add_conversation_seen(user_id, topic, level)
        return topic

    def get_total_vocabulary_count(self, level):
        self.cursor.execute("SELECT COUNT(*) FROM vocabulary_words WHERE level = ?", (level,))
        count = self.cursor.fetchone()[0]
        if count == 0:
            # Fallback
            return len(self.get_fallback_vocabulary(level, 100))
        return count

    def get_total_grammar_count(self, level):
        self.cursor.execute("SELECT COUNT(*) FROM grammar_lessons WHERE level = ?", (level,))
        count = self.cursor.fetchone()[0]
        if count == 0:
            # Fallback
            return len(self.get_fallback_grammar_lesson(level))
        return count

    def get_total_conversation_count(self, level):
        topics = self.get_fallback_conversation_topics(level)
        if isinstance(topics, list):
            return len(topics)
        return 5  # Default

    def check_duplicate_vocabulary(self):
        """Check for duplicate vocabulary words across all levels."""
        all_words = {}
        for level in ['beginner', 'amatur', 'intermediate', 'advanced']:
            words = self.get_fallback_vocabulary(level, 200)
            for w in words:
                word = w['word'].lower()
                if word not in all_words:
                    all_words[word] = []
                all_words[word].append(level)
        return {w: lvls for w, lvls in all_words.items() if len(lvls) > 1}

    def check_duplicate_grammar(self):
        """Check for duplicate grammar lesson titles across all levels."""
        all_titles = {}
        for level in ['beginner', 'amatur', 'intermediate', 'advanced']:
            lessons = self.get_fallback_grammar_lesson(level, all_lessons=True)
            for l in lessons:
                title = l['title'].strip().lower()
                if title not in all_titles:
                    all_titles[title] = []
                all_titles[title].append(level)
        return {t: lvls for t, lvls in all_titles.items() if len(lvls) > 1}

    def check_duplicate_conversation(self):
        """Check for duplicate conversation topics across all levels."""
        all_topics = {}
        # Use the static topics dictionary directly
        topics_dict = {
            'beginner': [
                'Introduce yourself',
                'Talk about your family',
                'Describe your house',
                'Talk about your favorite food',
                'Describe your daily routine',
                # ... (add all beginner topics here) ...
            ],
            'amatur': [
                'Talk about your hobbies',
                'Describe a memorable trip',
                'Talk about your school or job',
                'Describe your best friend',
                'Talk about your weekend plans',
                # ... (add all amatur topics here) ...
            ],
            'intermediate': [
                'Discuss a book or movie you like',
                'Talk about technology in your life',
                'Describe a problem you solved',
                'Talk about your goals for the future',
                'Discuss a cultural tradition',
                # ... (add all intermediate topics here) ...
            ],
            'advanced': [
                'Debate a current event',
                'Discuss environmental issues',
                'Talk about the impact of social media',
                'Discuss education systems',
                'Debate the pros and cons of globalization',
                # ... (add all advanced topics here) ...
            ]
        }
        for level in ['beginner', 'amatur', 'intermediate', 'advanced']:
            topics = topics_dict.get(level, [])
            for t in topics:
                topic = t.strip().lower()
                if topic not in all_topics:
                    all_topics[topic] = []
                all_topics[topic].append(level)
        return {t: lvls for t, lvls in all_topics.items() if len(lvls) > 1}

    def remove_duplicate_vocabulary(self):
        """Remove duplicate vocabulary words, keeping the word in the lowest level."""
        seen = set()
        for level in ['beginner', 'amatur', 'intermediate', 'advanced']:
            vocab = self.get_fallback_vocabulary(level, 200)
            unique = []
            for w in vocab:
                word = w['word'].lower()
                if word not in seen:
                    unique.append(w)
                    seen.add(word)
            # Overwrite the vocabulary for this level (if using in-memory)
            # If using DB, would need to update DB as well
        # Note: This only affects in-memory fallback, not DB

    def remove_duplicate_grammar(self):
        """Remove duplicate grammar lessons, keeping the lesson in the lowest level."""
        seen = set()
        for level in ['beginner', 'amatur', 'intermediate', 'advanced']:
            lessons = self.get_fallback_grammar_lesson(level, all_lessons=True)
            unique = []
            for l in lessons:
                title = l['title'].strip().lower()
                if title not in seen:
                    unique.append(l)
                    seen.add(title)
            # Overwrite the lessons for this level (if using in-memory)
        # Note: This only affects in-memory fallback, not DB

    def remove_duplicate_conversation(self):
        """Remove duplicate conversation topics, keeping the topic in the lowest level."""
        seen = set()
        for level in ['beginner', 'amatur', 'intermediate', 'advanced']:
            topics = self.get_fallback_conversation_topics(None, level) if hasattr(self, 'get_fallback_conversation_topics') else []
            unique = []
            if isinstance(topics, list):
                for t in topics:
                    topic = t.strip().lower()
                    if topic not in seen:
                        unique.append(t)
                        seen.add(topic)
            # Overwrite the topics for this level (if using in-memory)
        # Note: This only affects in-memory fallback, not DB

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