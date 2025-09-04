#!/usr/bin/env python3
"""
Sample Data Generator for English Learning Telegram Bot
Generates realistic test data for demonstration and thesis purposes
"""

import sqlite3
import random
import json
from datetime import datetime, timedelta
from faker import Faker
import numpy as np

# Configure Faker for Persian names
fake = Faker(['fa_IR', 'en_US'])

class SampleDataGenerator:
    """Generate realistic sample data for the English learning bot."""
    
    def __init__(self, user_db_path="user_data.db", content_db_path="content_data.db"):
        self.user_db_path = user_db_path
        self.content_db_path = content_db_path
        
        # Sample vocabulary words for different levels
        self.vocabulary_words = {
            'beginner': [
                {'word': 'hello', 'definition': 'سلام', 'example': 'Hello, how are you?'},
                {'word': 'book', 'definition': 'کتاب', 'example': 'I read a good book yesterday.'},
                {'word': 'water', 'definition': 'آب', 'example': 'Please give me some water.'},
                {'word': 'house', 'definition': 'خانه', 'example': 'My house is very beautiful.'},
                {'word': 'friend', 'definition': 'دوست', 'example': 'She is my best friend.'},
                {'word': 'food', 'definition': 'غذا', 'example': 'The food tastes delicious.'},
                {'word': 'school', 'definition': 'مدرسه', 'example': 'Children go to school every day.'},
                {'word': 'happy', 'definition': 'خوشحال', 'example': 'I am happy to see you.'},
                {'word': 'family', 'definition': 'خانواده', 'example': 'My family is very important to me.'},
                {'word': 'work', 'definition': 'کار', 'example': 'I work in an office.'}
            ],
            'amateur': [
                {'word': 'computer', 'definition': 'رایانه', 'example': 'I use my computer for work.'},
                {'word': 'beautiful', 'definition': 'زیبا', 'example': 'The sunset is beautiful tonight.'},
                {'word': 'important', 'definition': 'مهم', 'example': 'Education is very important.'},
                {'word': 'different', 'definition': 'متفاوت', 'example': 'We have different opinions.'},
                {'word': 'problem', 'definition': 'مشکل', 'example': 'We need to solve this problem.'},
                {'word': 'understand', 'definition': 'درک کردن', 'example': 'Do you understand the question?'},
                {'word': 'develop', 'definition': 'توسعه دادن', 'example': 'We need to develop new skills.'},
                {'word': 'experience', 'definition': 'تجربه', 'example': 'This job requires experience.'},
                {'word': 'environment', 'definition': 'محیط', 'example': 'We must protect our environment.'},
                {'word': 'government', 'definition': 'دولت', 'example': 'The government announced new policies.'}
            ],
            'intermediate': [
                {'word': 'achievement', 'definition': 'دستاورد', 'example': 'Graduating was a great achievement.'},
                {'word': 'sophisticated', 'definition': 'پیچیده', 'example': 'This is a sophisticated system.'},
                {'word': 'innovative', 'definition': 'نوآورانه', 'example': 'We need innovative solutions.'},
                {'word': 'competitive', 'definition': 'رقابتی', 'example': 'The market is very competitive.'},
                {'word': 'comprehensive', 'definition': 'جامع', 'example': 'We need a comprehensive plan.'},
                {'word': 'analyze', 'definition': 'تجزیه و تحلیل کردن', 'example': 'Let me analyze this data.'},
                {'word': 'demonstrate', 'definition': 'نشان دادن', 'example': 'Can you demonstrate this technique?'},
                {'word': 'investigate', 'definition': 'بررسی کردن', 'example': 'Police will investigate the case.'},
                {'word': 'methodology', 'definition': 'روش‌شناسی', 'example': 'Our research methodology is solid.'},
                {'word': 'philosophy', 'definition': 'فلسفه', 'example': 'Eastern philosophy is fascinating.'}
            ],
            'advanced': [
                {'word': 'entrepreneurship', 'definition': 'کارآفرینی', 'example': 'Entrepreneurship requires courage.'},
                {'word': 'contemporary', 'definition': 'معاصر', 'example': 'Contemporary art is thought-provoking.'},
                {'word': 'unprecedented', 'definition': 'بی‌سابقه', 'example': 'This is an unprecedented situation.'},
                {'word': 'metamorphosis', 'definition': 'دگردیسی', 'example': 'The company underwent a metamorphosis.'},
                {'word': 'paradigm', 'definition': 'الگو', 'example': 'We need a new paradigm for education.'},
                {'word': 'synthesis', 'definition': 'ترکیب', 'example': 'This book is a synthesis of many ideas.'},
                {'word': 'empirical', 'definition': 'تجربی', 'example': 'We need empirical evidence.'},
                {'word': 'ubiquitous', 'definition': 'همه‌جا حاضر', 'example': 'Smartphones are ubiquitous today.'},
                {'word': 'intrinsic', 'definition': 'ذاتی', 'example': 'This has intrinsic value.'},
                {'word': 'cognitive', 'definition': 'شناختی', 'example': 'Cognitive skills are important.'}
            ]
        }
        
        # Sample user profiles
        self.user_profiles = [
            {'age_range': '18-25', 'education': 'student', 'motivation': 'academic'},
            {'age_range': '26-35', 'education': 'bachelor', 'motivation': 'career'},
            {'age_range': '36-45', 'education': 'master', 'motivation': 'business'},
            {'age_range': '46-55', 'education': 'high_school', 'motivation': 'personal'},
            {'age_range': '25-30', 'education': 'bachelor', 'motivation': 'travel'}
        ]
    
    def generate_sample_users(self, count=50):
        """Generate sample users with realistic data."""
        users = []
        levels = ['beginner', 'amateur', 'intermediate', 'advanced']
        level_weights = [0.4, 0.3, 0.2, 0.1]  # More beginners, fewer advanced
        
        for i in range(count):
            # Generate user ID (starting from 1000 to avoid conflicts)
            user_id = 1000 + i
            
            # Generate username
            username = fake.user_name()
            
            # Select level based on weights
            level = np.random.choice(levels, p=level_weights)
            
            # Generate join date (last 6 months)
            join_date = fake.date_time_between(start_date='-6M', end_date='now')
            
            # Generate last active (between join date and now, weighted towards recent)
            days_since_join = (datetime.now() - join_date).days
            if days_since_join > 0:
                last_active_offset = min(days_since_join, np.random.exponential(5))
                last_active = datetime.now() - timedelta(days=last_active_offset)
            else:
                last_active = datetime.now()
            
            # Assessment completion (80% completion rate)
            assessment_done = random.random() < 0.8
            
            users.append({
                'user_id': user_id,
                'username': username,
                'level': level,
                'join_date': join_date.strftime('%Y-%m-%d %H:%M:%S'),
                'last_active': last_active.strftime('%Y-%m-%d %H:%M:%S'),
                'assessment_done': 1 if assessment_done else 0,
                'profile': random.choice(self.user_profiles)
            })
        
        return users
    
    def generate_vocabulary_practice(self, users):
        """Generate vocabulary practice data."""
        vocabulary_data = []
        
        for user in users:
            if not user['assessment_done']:
                continue
                
            user_id = user['user_id']
            level = user['level']
            
            # Get words for this level
            level_words = self.vocabulary_words.get(level, [])
            
            # Generate practice sessions (1-15 words per user)
            num_words = random.randint(1, min(15, len(level_words)))
            practiced_words = random.sample(level_words, num_words)
            
            for word_data in practiced_words:
                # Generate practice date (after join date)
                join_date = datetime.strptime(user['join_date'], '%Y-%m-%d %H:%M:%S')
                last_active = datetime.strptime(user['last_active'], '%Y-%m-%d %H:%M:%S')
                
                practice_date = fake.date_time_between(
                    start_date=join_date,
                    end_date=last_active
                )
                
                # Generate score (weighted towards higher scores for practice)
                score = max(30, min(100, int(np.random.normal(75, 15))))
                
                vocabulary_data.append({
                    'user_id': user_id,
                    'word': word_data['word'],
                    'score': score,
                    'last_practiced': practice_date.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return vocabulary_data
    
    def generate_progress_data(self, users):
        """Generate progress data for all sections."""
        progress_data = []
        sections = ['vocabulary', 'grammar', 'conversation', 'assessment']
        
        for user in users:
            user_id = user['user_id']
            level = user['level']
            join_date = datetime.strptime(user['join_date'], '%Y-%m-%d %H:%M:%S')
            last_active = datetime.strptime(user['last_active'], '%Y-%m-%d %H:%M:%S')
            
            # Generate assessment data first (if completed)
            if user['assessment_done']:
                assessment_score = self._get_assessment_score_for_level(level)
                assessment_date = join_date + timedelta(hours=random.randint(1, 48))
                
                progress_data.append({
                    'user_id': user_id,
                    'section': 'assessment',
                    'level': level,
                    'score': assessment_score,
                    'date': assessment_date.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # Generate learning section data
            for section in ['vocabulary', 'grammar', 'conversation']:
                if not user['assessment_done']:
                    continue
                
                # Number of sessions for this section (varies by user engagement)
                engagement_level = random.choice(['low', 'medium', 'high'])
                session_counts = {
                    'low': (1, 5),
                    'medium': (5, 15),
                    'high': (15, 30)
                }
                
                num_sessions = random.randint(*session_counts[engagement_level])
                
                # Generate sessions over time
                for session in range(num_sessions):
                    # Session date (progressive over time)
                    progress_ratio = session / max(1, num_sessions - 1)
                    time_range = (last_active - join_date).total_seconds()
                    session_offset = join_date + timedelta(
                        seconds=progress_ratio * time_range + random.randint(-3600, 3600)
                    )
                    
                    # Ensure session is within valid range
                    if session_offset < join_date:
                        session_offset = join_date + timedelta(hours=1)
                    elif session_offset > last_active:
                        session_offset = last_active
                    
                    # Generate score with improvement over time
                    base_score = self._get_base_score_for_level(level)
                    improvement = progress_ratio * 15  # Up to 15 points improvement
                    session_variation = random.uniform(-10, 10)
                    
                    score = max(20, min(100, base_score + improvement + session_variation))
                    
                    progress_data.append({
                        'user_id': user_id,
                        'section': section,
                        'level': level,
                        'score': round(score, 1),
                        'date': session_offset.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return progress_data
    
    def generate_grammar_data(self, users):
        """Generate grammar completion data."""
        grammar_data = []
        
        for user in users:
            if not user['assessment_done']:
                continue
                
            user_id = user['user_id']
            level = user['level']
            
            # Random number of completed grammar lessons (0-5 per level)
            num_completed = random.randint(0, 5)
            
            if num_completed > 0:
                completed_lessons = random.sample(range(1, 6), num_completed)
                
                join_date = datetime.strptime(user['join_date'], '%Y-%m-%d %H:%M:%S')
                last_active = datetime.strptime(user['last_active'], '%Y-%m-%d %H:%M:%S')
                
                for lesson_id in completed_lessons:
                    completion_date = fake.date_time_between(
                        start_date=join_date + timedelta(days=1),
                        end_date=last_active
                    )
                    
                    # Generate score (grammar tends to be harder)
                    base_score = self._get_base_score_for_level(level) - 5
                    score = max(40, min(100, int(np.random.normal(base_score, 12))))
                    
                    grammar_data.append({
                        'user_id': user_id,
                        'level': level,
                        'topic_id': lesson_id,
                        'score': score,
                        'completed_at': completion_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return grammar_data
    
    def _get_assessment_score_for_level(self, level):
        """Get realistic assessment score based on level."""
        score_ranges = {
            'beginner': (15, 35),
            'amateur': (30, 55),
            'intermediate': (55, 85),
            'advanced': (80, 95)
        }
        return random.randint(*score_ranges[level])
    
    def _get_base_score_for_level(self, level):
        """Get base performance score for level."""
        base_scores = {
            'beginner': 65,
            'amateur': 70,
            'intermediate': 75,
            'advanced': 80
        }
        return base_scores[level]
    
    def populate_sample_data(self, num_users=50):
        """Populate database with sample data."""
        print(f"🔄 Generating sample data for {num_users} users...")
        
        # Generate data
        users = self.generate_sample_users(num_users)
        vocabulary_data = self.generate_vocabulary_practice(users)
        progress_data = self.generate_progress_data(users)
        grammar_data = self.generate_grammar_data(users)
        
        # Insert into database
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        
        try:
            # Insert users
            for user in users:
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, level, join_date, last_active, assessment_done)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user['user_id'], user['username'], user['level'],
                    user['join_date'], user['last_active'], user['assessment_done']
                ))
            
            # Insert vocabulary data
            for vocab in vocabulary_data:
                cursor.execute("""
                    INSERT INTO vocabulary (user_id, word, score, last_practiced)
                    VALUES (?, ?, ?, ?)
                """, (vocab['user_id'], vocab['word'], vocab['score'], vocab['last_practiced']))
            
            # Insert progress data
            for progress in progress_data:
                cursor.execute("""
                    INSERT INTO progress (user_id, section, level, score, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    progress['user_id'], progress['section'], progress['level'],
                    progress['score'], progress['date']
                ))
            
            # Insert grammar data
            for grammar in grammar_data:
                cursor.execute("""
                    INSERT INTO user_grammar (user_id, level, topic_id, score, completed_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    grammar['user_id'], grammar['level'], grammar['topic_id'],
                    grammar['score'], grammar['completed_at']
                ))
            
            conn.commit()
            
            print("✅ Sample data inserted successfully!")
            print(f"   👥 Users: {len(users)}")
            print(f"   📚 Vocabulary entries: {len(vocabulary_data)}")
            print(f"   📈 Progress entries: {len(progress_data)}")
            print(f"   📝 Grammar completions: {len(grammar_data)}")
            
            return {
                'users': len(users),
                'vocabulary': len(vocabulary_data),
                'progress': len(progress_data),
                'grammar': len(grammar_data)
            }
            
        except Exception as e:
            print(f"❌ Error inserting sample data: {e}")
            conn.rollback()
            return None
        
        finally:
            conn.close()
    
    def export_sample_data(self, filename="sample_dataset.json"):
        """Export generated data as JSON for analysis."""
        print("📤 Exporting sample dataset...")
        
        conn = sqlite3.connect(self.user_db_path)
        
        # Fetch all data
        users_df = pd.read_sql_query("SELECT * FROM users WHERE user_id >= 1000", conn)
        progress_df = pd.read_sql_query("""
            SELECT * FROM progress 
            WHERE user_id >= 1000 
            ORDER BY user_id, date
        """, conn)
        vocabulary_df = pd.read_sql_query("""
            SELECT * FROM vocabulary 
            WHERE user_id >= 1000
        """, conn)
        grammar_df = pd.read_sql_query("""
            SELECT * FROM user_grammar 
            WHERE user_id >= 1000
        """, conn)
        
        conn.close()
        
        # Convert to dictionaries
        dataset = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'description': 'Sample dataset for English Learning Telegram Bot',
                'total_users': len(users_df),
                'total_progress_records': len(progress_df),
                'total_vocabulary_records': len(vocabulary_df),
                'total_grammar_records': len(grammar_df)
            },
            'users': users_df.to_dict('records'),
            'progress': progress_df.to_dict('records'),
            'vocabulary': vocabulary_df.to_dict('records'),
            'grammar': grammar_df.to_dict('records')
        }
        
        # Export to JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Dataset exported to {filename}")
        return dataset
    
    def generate_summary_report(self):
        """Generate a summary report of the sample data."""
        conn = sqlite3.connect(self.user_db_path)
        
        # Basic statistics
        stats = {
            'user_stats': {},
            'learning_stats': {},
            'engagement_stats': {}
        }
        
        try:
            cursor = conn.cursor()
            
            # User statistics
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_id >= 1000")
            stats['user_stats']['total_sample_users'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT level, COUNT(*) 
                FROM users WHERE user_id >= 1000 
                GROUP BY level
            """)
            stats['user_stats']['level_distribution'] = dict(cursor.fetchall())
            
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE user_id >= 1000 AND assessment_done = 1
            """)
            stats['user_stats']['assessed_users'] = cursor.fetchone()[0]
            
            # Learning statistics
            cursor.execute("""
                SELECT section, COUNT(*), AVG(score) 
                FROM progress 
                WHERE user_id >= 1000 AND section != 'assessment'
                GROUP BY section
            """)
            learning_data = cursor.fetchall()
            stats['learning_stats'] = {
                row[0]: {'sessions': row[1], 'avg_score': round(row[2], 1)}
                for row in learning_data
            }
            
            # Engagement statistics
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) 
                FROM progress 
                WHERE user_id >= 1000
            """)
            stats['engagement_stats']['active_learners'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT user_id, COUNT(*) as sessions
                FROM progress 
                WHERE user_id >= 1000 
                GROUP BY user_id
            """)
            session_counts = [row[1] for row in cursor.fetchall()]
            if session_counts:
                stats['engagement_stats']['avg_sessions_per_user'] = round(
                    sum(session_counts) / len(session_counts), 1
                )
                stats['engagement_stats']['max_sessions'] = max(session_counts)
            
        except Exception as e:
            print(f"Error generating summary: {e}")
        
        finally:
            conn.close()
        
        return stats

# Main execution
if __name__ == "__main__":
    import pandas as pd
    
    generator = SampleDataGenerator()
    
    # Generate sample data
    result = generator.populate_sample_data(num_users=50)
    
    if result:
        # Export dataset
        dataset = generator.export_sample_data()
        
        # Generate summary
        summary = generator.generate_summary_report()
        
        print("\n📊 Sample Dataset Summary:")
        print(f"   Total Users: {summary['user_stats']['total_sample_users']}")
        print(f"   Level Distribution: {summary['user_stats']['level_distribution']}")
        print(f"   Assessment Completion: {summary['user_stats']['assessed_users']}")
        print(f"   Active Learners: {summary['engagement_stats']['active_learners']}")
        print(f"   Avg Sessions/User: {summary['engagement_stats'].get('avg_sessions_per_user', 0)}")
        
        print("\n🎯 Learning Statistics:")
        for section, data in summary['learning_stats'].items():
            print(f"   {section}: {data['sessions']} sessions, {data['avg_score']}% avg score")
        
        print("\n✨ Sample dataset ready for thesis demonstration!")
