#!/usr/bin/env python3
"""
Simple Dataset Generator for English Learning Telegram Bot
Creates basic test data without external dependencies
"""

import sqlite3
import random
import json
from datetime import datetime, timedelta

def generate_simple_dataset():
    """Generate a simple dataset with test users and activities."""
    
    # Sample users data
    users = [
        {"user_id": 1001, "username": "student_alice", "level": "beginner", "assessment_done": 1},
        {"user_id": 1002, "username": "learner_bob", "level": "amateur", "assessment_done": 1},
        {"user_id": 1003, "username": "english_sara", "level": "intermediate", "assessment_done": 1},
        {"user_id": 1004, "username": "advanced_mike", "level": "advanced", "assessment_done": 1},
        {"user_id": 1005, "username": "beginner_lisa", "level": "beginner", "assessment_done": 1},
        {"user_id": 1006, "username": "student_john", "level": "amateur", "assessment_done": 0},
        {"user_id": 1007, "username": "learner_emma", "level": "intermediate", "assessment_done": 1},
        {"user_id": 1008, "username": "english_david", "level": "beginner", "assessment_done": 1},
        {"user_id": 1009, "username": "advanced_jane", "level": "advanced", "assessment_done": 1},
        {"user_id": 1010, "username": "practice_tom", "level": "amateur", "assessment_done": 1}
    ]
    
    # Add join and last active dates
    base_date = datetime.now() - timedelta(days=30)
    for i, user in enumerate(users):
        join_date = base_date + timedelta(days=i*3)
        last_active = join_date + timedelta(days=random.randint(1, 20))
        user["join_date"] = join_date.strftime('%Y-%m-%d %H:%M:%S')
        user["last_active"] = last_active.strftime('%Y-%m-%d %H:%M:%S')
    
    # Sample progress data
    progress_data = []
    sections = ["vocabulary", "grammar", "conversation", "assessment"]
    
    for user in users:
        if not user["assessment_done"]:
            continue
            
        user_id = user["user_id"]
        level = user["level"]
        
        # Assessment score based on level
        level_scores = {
            "beginner": random.randint(15, 35),
            "amateur": random.randint(30, 55), 
            "intermediate": random.randint(55, 85),
            "advanced": random.randint(80, 95)
        }
        
        join_date = datetime.strptime(user["join_date"], '%Y-%m-%d %H:%M:%S')
        
        # Add assessment record
        assessment_date = join_date + timedelta(hours=1)
        progress_data.append({
            "user_id": user_id,
            "section": "assessment",
            "level": level,
            "score": level_scores[level],
            "date": assessment_date.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Add learning activities
        num_activities = random.randint(5, 25)
        for activity in range(num_activities):
            section = random.choice(["vocabulary", "grammar", "conversation"])
            activity_date = join_date + timedelta(days=random.randint(1, 15))
            
            # Score based on level with some variation
            base_score = {"beginner": 65, "amateur": 70, "intermediate": 75, "advanced": 80}[level]
            score = base_score + random.randint(-15, 20)
            score = max(30, min(100, score))
            
            progress_data.append({
                "user_id": user_id,
                "section": section,
                "level": level,
                "score": score,
                "date": activity_date.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Sample vocabulary data
    vocabulary_words = ["hello", "book", "computer", "beautiful", "important", "achievement"]
    vocabulary_data = []
    
    for user in users:
        if not user["assessment_done"]:
            continue
            
        user_id = user["user_id"]
        num_words = random.randint(3, 8)
        practiced_words = random.sample(vocabulary_words, min(num_words, len(vocabulary_words)))
        
        join_date = datetime.strptime(user["join_date"], '%Y-%m-%d %H:%M:%S')
        
        for word in practiced_words:
            practice_date = join_date + timedelta(days=random.randint(1, 10))
            score = random.randint(50, 95)
            
            vocabulary_data.append({
                "user_id": user_id,
                "word": word,
                "score": score,
                "last_practiced": practice_date.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Sample grammar data
    grammar_data = []
    for user in users:
        if not user["assessment_done"]:
            continue
            
        user_id = user["user_id"]
        level = user["level"]
        
        # Random completed lessons
        num_lessons = random.randint(1, 4)
        completed_lessons = random.sample(range(1, 6), num_lessons)
        
        join_date = datetime.strptime(user["join_date"], '%Y-%m-%d %H:%M:%S')
        
        for lesson_id in completed_lessons:
            completion_date = join_date + timedelta(days=random.randint(2, 12))
            score = random.randint(55, 90)
            
            grammar_data.append({
                "user_id": user_id,
                "level": level,
                "topic_id": lesson_id,
                "score": score,
                "completed_at": completion_date.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return {
        "users": users,
        "progress": progress_data,
        "vocabulary": vocabulary_data,
        "grammar": grammar_data
    }

def populate_database(dataset):
    """Populate the database with sample dataset."""
    print("🔄 Populating database with sample data...")
    
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    try:
        # Insert users
        for user in dataset["users"]:
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, level, join_date, last_active, assessment_done)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user["user_id"], user["username"], user["level"],
                user["join_date"], user["last_active"], user["assessment_done"]
            ))
        
        # Insert progress data
        for progress in dataset["progress"]:
            cursor.execute("""
                INSERT INTO progress (user_id, section, level, score, date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                progress["user_id"], progress["section"], progress["level"],
                progress["score"], progress["date"]
            ))
        
        # Insert vocabulary data
        for vocab in dataset["vocabulary"]:
            cursor.execute("""
                INSERT INTO vocabulary (user_id, word, score, last_practiced)
                VALUES (?, ?, ?, ?)
            """, (vocab["user_id"], vocab["word"], vocab["score"], vocab["last_practiced"]))
        
        # Insert grammar data
        for grammar in dataset["grammar"]:
            cursor.execute("""
                INSERT INTO user_grammar (user_id, level, topic_id, score, completed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                grammar["user_id"], grammar["level"], grammar["topic_id"],
                grammar["score"], grammar["completed_at"]
            ))
        
        conn.commit()
        
        print("✅ Sample data inserted successfully!")
        print(f"   👥 Users: {len(dataset['users'])}")
        print(f"   📈 Progress entries: {len(dataset['progress'])}")
        print(f"   📚 Vocabulary entries: {len(dataset['vocabulary'])}")
        print(f"   📝 Grammar completions: {len(dataset['grammar'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def export_dataset(dataset, filename="simple_dataset.json"):
    """Export dataset to JSON file."""
    export_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "Simple test dataset for English Learning Bot",
            "total_users": len(dataset["users"]),
            "total_progress": len(dataset["progress"]),
            "total_vocabulary": len(dataset["vocabulary"]),
            "total_grammar": len(dataset["grammar"])
        },
        "data": dataset
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"📤 Dataset exported to {filename}")
    return export_data

def generate_summary():
    """Generate summary of the dataset."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    try:
        # User summary
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_id >= 1000")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT level, COUNT(*) FROM users WHERE user_id >= 1000 GROUP BY level")
        level_dist = dict(cursor.fetchall())
        
        # Progress summary
        cursor.execute("""
            SELECT section, COUNT(*), AVG(score), MIN(score), MAX(score)
            FROM progress WHERE user_id >= 1000 AND section != 'assessment'
            GROUP BY section
        """)
        progress_stats = cursor.fetchall()
        
        # Assessment summary
        cursor.execute("""
            SELECT AVG(score), MIN(score), MAX(score)
            FROM progress WHERE user_id >= 1000 AND section = 'assessment'
        """)
        assessment_stats = cursor.fetchone()
        
        print("\n📊 Dataset Summary Report:")
        print("=" * 40)
        print(f"👥 Total Test Users: {total_users}")
        print(f"📋 Level Distribution: {level_dist}")
        
        if assessment_stats[0]:
            print(f"🧪 Assessment Scores: Avg={assessment_stats[0]:.1f}, Range={assessment_stats[1]}-{assessment_stats[2]}")
        
        print("\n📈 Learning Activities:")
        for section, count, avg_score, min_score, max_score in progress_stats:
            print(f"   {section}: {count} sessions, {avg_score:.1f}% avg (range: {min_score}-{max_score})")
        
        print("\n✨ Dataset ready for testing and analysis!")
        
    except Exception as e:
        print(f"Error generating summary: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Generating Simple Test Dataset...")
    
    # Generate dataset
    dataset = generate_simple_dataset()
    
    # Populate database
    success = populate_database(dataset)
    
    if success:
        # Export to JSON
        export_dataset(dataset)
        
        # Generate summary
        generate_summary()
        
        print("\n🎯 Test dataset is ready!")
        print("   📊 Use analytics_engine.py to analyze the data")
        print("   🔧 Use admin_panel.py to view in web interface")
        print("   📈 Dataset contains realistic learning progressions")
    else:
        print("❌ Failed to create test dataset")
