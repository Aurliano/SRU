#!/usr/bin/env python3
"""
Test script to populate content_data.db with vocabulary and grammar lessons.
Run this script to initialize the database with all content.
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_manager import ContentManager

def main():
    """Main function to test and populate the content database."""
    print("🚀 Starting content database population...")
    
    try:
        # Initialize content manager
        content_manager = ContentManager()
        
        print("✅ Content manager initialized successfully")
        
        # Test vocabulary population
        print("\n📚 Testing vocabulary population...")
        vocab_count = content_manager.get_total_vocabulary_count('beginner')
        print(f"Beginner vocabulary count: {vocab_count}")
        
        # Test grammar lessons
        print("\n📝 Testing grammar lessons...")
        grammar_count = content_manager.get_total_grammar_count('beginner')
        print(f"Beginner grammar count: {grammar_count}")
        
        # Test getting vocabulary
        print("\n🔤 Testing vocabulary retrieval...")
        words = content_manager.get_vocabulary_for_level('beginner', 5)
        print(f"Retrieved {len(words)} words for beginner level")
        for i, word in enumerate(words[:3]):  # Show first 3 words
            print(f"  {i+1}. {word['word']} - {word['definition']}")
        
        # Test getting grammar lesson
        print("\n📖 Testing grammar lesson retrieval...")
        lesson = content_manager.get_grammar_lesson_for_level(12345, 'beginner')  # Test user ID
        if lesson:
            print(f"Retrieved grammar lesson: {lesson['title']}")
        else:
            print("No grammar lesson retrieved")
        
        # Test conversation topics
        print("\n🗣️ Testing conversation topics...")
        topic = content_manager.get_fallback_conversation_topics(12345, 'beginner')  # Test user ID
        if topic:
            print(f"Retrieved conversation topic: {topic['title']}")
            print(f"Description: {topic['description']}")
            print(f"Starter: {topic['starter']}")
        else:
            print("No conversation topic retrieved")
        
        # Test conversation count
        conv_count = content_manager.get_total_conversation_count('beginner')
        print(f"Beginner conversation topics count: {conv_count}")
        
        print("\n🎉 Content database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during content database test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
