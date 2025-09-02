import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserDatabase:
    """Database for user management."""
    
    def __init__(self, db_path="user_data.db"):
        """Initialize database connection."""
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        # Connect to database
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
            
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            # Create users table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                level TEXT DEFAULT 'beginner',
                join_date TEXT,
                last_active TEXT,
                assessment_done BOOLEAN DEFAULT FALSE
            )
            ''')
            
            # Create progress table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                section TEXT,
                level TEXT,
                score REAL DEFAULT 0,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            # Create vocabulary table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                word TEXT,
                score INTEGER DEFAULT 0,
                last_practiced TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            # Create user_grammar table to track completed grammar lessons
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_grammar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                level TEXT,
                topic_id INTEGER,
                score INTEGER DEFAULT 0,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            # Create user_conversation table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic_id INTEGER,
                level TEXT,
                seen_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            # Create index for faster lookups
            self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_conversation_user_level 
            ON user_conversation (user_id, level)
            ''')
            
            # Create vocab_tested table to track tested words
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocab_tested (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                word TEXT,
                tested_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            self.conn.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def register_user(self, user_id, username):
        """Register a new user or update existing username."""
        try:
            # Check if user exists
            self.cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
            existing_user = self.cursor.fetchone()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if existing_user:
                # Update username if different
                if existing_user[0] != username:
                    self.cursor.execute(
                        "UPDATE users SET username = ? WHERE user_id = ?",
                        (username, user_id)
                    )
                    self.conn.commit()
                # User already exists
                return False
            else:
                # Add new user
                self.cursor.execute(
                    "INSERT INTO users (user_id, username, join_date, last_active, assessment_done) VALUES (?, ?, ?, ?, ?)",
                    (user_id, username, now, now, 0)
                )
                self.conn.commit()
                # New user was added
                return True
        except Exception as e:
            print(f"Error registering user: {e}")
            return False
            
    
    def update_last_active(self, user_id):
        """Update the last active timestamp for a user."""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "UPDATE users SET last_active = ? WHERE user_id = ?",
                (now, user_id)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error updating last active: {e}")
    
    def get_user_level(self, user_id):
        """Get the user's current level."""
        try:
            self.cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            
            if result:
                return result[0]
            else:
                return "beginner"  # Default level
        except Exception as e:
            print(f"Error getting user level: {e}")
            return "beginner"  # Default level
    
    def update_user_level(self, user_id, level):
        """Update the user's level."""
        try:
            self.cursor.execute(
                "UPDATE users SET level = ? WHERE user_id = ?",
                (level, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user level: {e}")
            return False
                
    def force_update_level(self, user_id, level):
        """Force update level with more robust error handling."""
        try:
            # First check if user exists
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
            exists = self.cursor.fetchone()[0] > 0
            
            if not exists:
                # Create user if doesn't exist
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute(
                    "INSERT INTO users (user_id, username, level, join_date, last_active) VALUES (?, ?, ?, ?, ?)",
                    (user_id, f"user_{user_id}", level, now, now)
                )
            else:
                # Update existing user
                self.cursor.execute(
                    "UPDATE users SET level = ? WHERE user_id = ?", 
                    (level, user_id)
                )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error in force_update_level: {e}")
            return False
    
    def add_progress(self, user_id, section, score):
        """Add a progress entry for a user."""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            level = self.get_user_level(user_id)
            self.cursor.execute(
                "INSERT INTO progress (user_id, section, level, score, date) VALUES (?, ?, ?, ?, ?)",
                (user_id, section, level, score, now)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding progress: {e}")
            return False
    
    def get_user_progress(self, user_id):
        """Get progress for all sections and levels."""
        progress = {}
        for section in ['vocabulary', 'grammar', 'conversation', 'assessment']:
            progress[section] = {}
            for level in ['beginner', 'amatثur', 'intermediate', 'advanced']:
                progress[section][level] = self.get_section_progress(user_id, section, level)
        return progress

    def add_section_progress(self, user_id, section, level, increment):
        """Increase progress for a section and level, capped at 100."""
        # Get current progress
        current = self.get_section_progress(user_id, section, level)
        new_score = min(100, current + increment)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO progress (user_id, section, level, score, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, section, level, new_score, now)
        )
        self.conn.commit()
        return new_score

    def get_section_progress(self, user_id, section, level):
        """Get progress percent for a section and level."""
        self.cursor.execute(
            "SELECT score FROM progress WHERE user_id = ? AND section = ? AND level = ? ORDER BY date DESC LIMIT 1",
            (user_id, section, level)
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def check_and_upgrade_level(self, user_id):
        """If all 3 sections for current level are >=80, upgrade user to next level and return True if upgraded."""
        current_level = self.get_user_level(user_id)
        levels = ['beginner', 'amateur', 'intermediate', 'advanced']
        if current_level == 'advanced':
            return False
        idx = levels.index(current_level)
        for section in ['vocabulary', 'grammar', 'conversation']:
            if self.get_section_progress(user_id, section, current_level) < 80:
                return False
        # Upgrade
        new_level = levels[idx+1]
        self.update_user_level(user_id, new_level)
        return True
    
    def get_users_with_notifications(self):
        """Get all users who have notifications enabled."""
        try:
            self.cursor.execute(
                "SELECT user_id FROM users WHERE notifications = 1"
            )
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting users with notifications: {e}")
            return []
        
    def save_assessment_result(self, user_id, percentage):
        """Save assessment result and return success status."""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO progress (user_id, section, level, score, date) VALUES (?, ?, ?, ?, ?)",
                (user_id, "assessment", self.get_user_level(user_id), percentage, now)
            )
            self.conn.commit()
            return True, None
        except Exception as e:
            error_msg = f"Error saving assessment result: {e}"
            print(error_msg)
            return False, error_msg
    
    def get_latest_assessment_result(self, user_id):
        """Get the latest assessment result for a user."""
        try:
            self.cursor.execute(
                """
                SELECT score FROM progress 
                WHERE user_id = ? AND section = 'assessment' 
                ORDER BY date DESC LIMIT 1
                """,
                (user_id,)
            )
            result = self.cursor.fetchone()
            
            if result:
                score = result[0]
                # Determine level based on score
                level = "beginner"
                if score >= 80:
                    level = "advanced"
                elif score >= 60:
                    level = "intermediate"
                elif score >= 40:
                    level = "amatثur"
                return level, score
            else:
                return None, None
        except Exception as e:
            print(f"Error getting latest assessment result: {e}")
            return None, None
    
    def debug_database(self, user_id):
        """Comprehensive database diagnostic."""
        debug_info = {
            'db_exists': False,
            'db_size': 0,
            'tables': [],
            'table_structures': {},
            'integrity_check': 'Not checked',
            'foreign_key_violations': [],
            'errors': [],
            'user_exists': False,
            'user_level': None,
            'user_record': {},
            'progress_count': 0,
            'assessment_progress_count': 0,
            'last_assessment': None
        }
        
        try:
            import os
            # Check if database file exists
            if os.path.exists("user_data.db"):
                debug_info['db_exists'] = True
                debug_info['db_size'] = os.path.getsize("user_data.db")
            
            # Get all tables
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in self.cursor.fetchall()]
            debug_info['tables'] = tables
            
            # Check table structure for each table
            for table in tables:
                try:
                    self.cursor.execute(f"PRAGMA table_info({table})")
                    columns = [{'name': row[1], 'type': row[2]} for row in self.cursor.fetchall()]
                    debug_info['table_structures'][table] = columns
                except Exception as e:
                    debug_info['errors'].append(f"Error getting structure for table {table}: {e}")
            
            # Run integrity check
            self.cursor.execute("PRAGMA integrity_check")
            integrity_result = self.cursor.fetchone()
            debug_info['integrity_check'] = integrity_result[0] if integrity_result else "Failed"
            
            # Check for foreign key violations
            self.cursor.execute("PRAGMA foreign_key_check")
            fk_violations = self.cursor.fetchall()
            debug_info['foreign_key_violations'] = fk_violations
            
            # Check if user exists
            self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user_row = self.cursor.fetchone()
            
            if user_row:
                debug_info['user_exists'] = True
                debug_info['user_level'] = user_row[2]  # Level is at index 2
                debug_info['user_record'] = {
                    'user_id': user_row[0],
                    'username': user_row[1],
                    'level': user_row[2],
                    'join_date': user_row[3],
                    'last_active': user_row[4],
                    'notifications': user_row[5] if len(user_row) > 5 else 1
                }
            
            # Check progress records
            if 'progress' in tables:
                self.cursor.execute("SELECT COUNT(*) FROM progress")
                debug_info['progress_count'] = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM progress WHERE section = 'assessment'")
                debug_info['assessment_progress_count'] = self.cursor.fetchone()[0]
                
                # Get last assessment
                self.cursor.execute(
                    """
                    SELECT score, date FROM progress 
                    WHERE user_id = ? AND section = 'assessment'
                    ORDER BY date DESC LIMIT 1
                    """,
                    (user_id,)
                )
                last_assessment = self.cursor.fetchone()
            
                if last_assessment:
                    debug_info['last_assessment'] = {
                        'score': last_assessment[0],
                        'date': last_assessment[1]
                    }
            
        except Exception as e:
            debug_info['errors'].append(f"General diagnostic error: {e}")
        
        return debug_info

    def get_words_studied_count(self, user_id):
        """Get the count of unique words studied by a user."""
        try:
            self.cursor.execute(
                "SELECT COUNT(DISTINCT word) FROM vocabulary WHERE user_id = ?",
                (user_id,)
            )
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error getting words studied count: {e}")
            return 0
    
    def add_word_studied(self, user_id, word, score):
        """Record that a user has studied a specific word."""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO vocabulary (user_id, word, score, last_practiced) VALUES (?, ?, ?, ?)",
                (user_id, word, score, now)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding word studied: {e}")
            # Check if vocabulary table exists, create if not
            try:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vocabulary (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        word TEXT,
                        score INTEGER DEFAULT 0,
                        last_practiced TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                """)
                self.conn.commit()
                
                # Try again after creating table
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute(
                    "INSERT INTO vocabulary (user_id, word, score, last_practiced) VALUES (?, ?, ?, ?)",
                    (user_id, word, score, now)
                )
                self.conn.commit()
                return True
            except Exception as create_e:
                print(f"Error creating vocabulary table: {create_e}")
            return False

    def get_recent_studied_words(self, user_id, limit=20):
        """Get recently studied words for testing."""
        try:
            self.cursor.execute("""
                SELECT DISTINCT word, 
                       (SELECT definition FROM vocabulary_words WHERE word = v.word LIMIT 1) as definition
                FROM vocabulary v
                WHERE user_id = ?
                GROUP BY word
                ORDER BY MAX(last_practiced) DESC
                LIMIT ?
            """, (user_id, limit))
            
            words = []
            for row in self.cursor.fetchall():
                if row[1]:  # Check if definition is not None
                    words.append({
                        'word': row[0],
                        'definition': row[1]
                    })
            
            return words
        except Exception as e:
            print(f"Error getting recent studied words: {e}")
            return []

    def get_random_definitions(self, user_id, count=3):
        """Get random definitions for quiz options, excluding user's current words."""
        try:
            # First, get the user's level
            level = self.get_user_level(user_id)
            
            # Then get random definitions from vocabulary at that level
            self.cursor.execute("""
                SELECT DISTINCT definition 
                FROM vocabulary_words 
                WHERE level = ? 
                AND word NOT IN (
                    SELECT word FROM vocabulary WHERE user_id = ?
                )
                ORDER BY RANDOM()
                LIMIT ?
            """, (level, user_id, count))
            
            definitions = [row[0] for row in self.cursor.fetchall()]
            
            # If we don't have enough, get from any level
            if len(definitions) < count:
                additional_needed = count - len(definitions)
                self.cursor.execute("""
                    SELECT DISTINCT definition 
                    FROM vocabulary_words 
                    WHERE definition NOT IN (?)
                    ORDER BY RANDOM()
                    LIMIT ?
                """, (','.join(definitions), additional_needed))
                
                definitions.extend([row[0] for row in self.cursor.fetchall()])
            
            return definitions
        except Exception as e:
            print(f"Error getting random definitions: {e}")
            return ["Option A", "Option B", "Option C"][:count]  # Return fallback options

    def add_grammar_seen(self, user_id, lesson_title, level):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO user_grammar (user_id, lesson_title, level, date) VALUES (?, ?, ?, ?)",
            (user_id, lesson_title, level, now)
        )
        self.conn.commit()

    def get_seen_grammar_titles(self, user_id, level):
        self.cursor.execute(
            "SELECT lesson_title FROM user_grammar WHERE user_id = ? AND level = ?",
            (user_id, level)
        )
        return set(row[0] for row in self.cursor.fetchall())

    def reset_grammar_seen(self, user_id, level):
        self.cursor.execute(
            "DELETE FROM user_grammar WHERE user_id = ? AND level = ?",
            (user_id, level)
        )
        self.conn.commit()

    def add_conversation_seen(self, user_id, topic, level):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO user_conversation (user_id, topic, level, date) VALUES (?, ?, ?, ?)",
            (user_id, topic, level, now)
        )
        self.conn.commit()

    def get_seen_conversation_topics(self, user_id, level):
        self.cursor.execute(
            "SELECT topic FROM user_conversation WHERE user_id = ? AND level = ?",
            (user_id, level)
        )
        return set(row[0] for row in self.cursor.fetchall())

    def reset_conversation_seen(self, user_id, level):
        self.cursor.execute(
            "DELETE FROM user_conversation WHERE user_id = ? AND level = ?",
            (user_id, level)
        )
        self.conn.commit()

    def set_assessment_done(self, user_id, done: bool):
        self.cursor.execute(
            "UPDATE users SET assessment_done = ? WHERE user_id = ?",
            (1 if done else 0, user_id)
        )
        self.conn.commit()

    def is_assessment_done(self, user_id):
        self.cursor.execute(
            "SELECT assessment_done FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = self.cursor.fetchone()
        return result and result[0] == 1

    def get_avg_vocab_score(self, user_id, level):
        """Get the average score of vocabulary practice for a user and level."""
        try:
            self.cursor.execute(
                "SELECT AVG(score) FROM vocabulary v JOIN vocabulary_words w ON v.word = w.word WHERE v.user_id = ? AND w.level = ?",
                (user_id, level)
            )
            result = self.cursor.fetchone()
            return result[0] if result and result[0] is not None else 0
        except Exception as e:
            print(f"Error getting average vocabulary score: {e}")
            return 0

    def get_next_untested_words(self, user_id, level, batch_size=20):
        """Get the next batch of untested words for a user and level."""
        try:
            self.cursor.execute('''
                SELECT w.word, w.definition
                FROM vocabulary_words w
                LEFT JOIN vocab_tested t ON w.word = t.word AND t.user_id = ?
                WHERE w.level = ?
                AND w.word IN (SELECT word FROM vocabulary WHERE user_id = ?)
                AND t.word IS NULL
                LIMIT ?
            ''', (user_id, level, user_id, batch_size))
            return [{'word': row[0], 'definition': row[1]} for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting untested words: {e}")
            return []

    def mark_words_tested(self, user_id, words):
        """Mark a list of words as tested for a user."""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for word in words:
                self.cursor.execute(
                    "INSERT INTO vocab_tested (user_id, word, tested_at) VALUES (?, ?, ?)",
                    (user_id, word, now)
                )
            self.conn.commit()
        except Exception as e:
            print(f"Error marking words as tested: {e}")