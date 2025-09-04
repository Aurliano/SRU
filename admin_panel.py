#!/usr/bin/env python3
"""
Admin Panel for English Learning Telegram Bot
A web-based admin interface for managing users, content, and viewing analytics
"""

import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import plotly.graph_objs as go
import plotly.utils
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

class AdminDatabase:
    """Database interface for admin operations."""
    
    def __init__(self):
        self.user_db_path = "user_data.db"
        self.content_db_path = "content_data.db"
    
    def get_connection(self, db_type='user'):
        """Get database connection."""
        db_path = self.user_db_path if db_type == 'user' else self.content_db_path
        return sqlite3.connect(db_path)
    
    def get_user_stats(self):
        """Get comprehensive user statistics."""
        try:
            conn = self.get_connection('user')
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Users by level
            cursor.execute("SELECT level, COUNT(*) FROM users GROUP BY level")
            users_by_level = dict(cursor.fetchall())
            
            # Active users (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM users WHERE last_active >= ?", (week_ago,))
            active_users = cursor.fetchone()[0]
            
            # Users who completed assessment
            cursor.execute("SELECT COUNT(*) FROM users WHERE assessment_done = 1")
            assessed_users = cursor.fetchone()[0]
            
            # Average progress by section
            cursor.execute("""
                SELECT section, AVG(score) 
                FROM progress 
                WHERE section IN ('vocabulary', 'grammar', 'conversation')
                GROUP BY section
            """)
            avg_progress = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_users': total_users,
                'users_by_level': users_by_level,
                'active_users': active_users,
                'assessed_users': assessed_users,
                'avg_progress': avg_progress
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}
    
    def get_all_users(self, limit=50, offset=0):
        """Get all users with pagination."""
        try:
            conn = self.get_connection('user')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, level, join_date, last_active, assessment_done
                FROM users 
                ORDER BY last_active DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'level': row[2],
                    'join_date': row[3],
                    'last_active': row[4],
                    'assessment_done': bool(row[5])
                })
            
            conn.close()
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_user_details(self, user_id):
        """Get detailed information about a specific user."""
        try:
            conn = self.get_connection('user')
            cursor = conn.cursor()
            
            # User basic info
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                return None
            
            user_info = {
                'user_id': user_row[0],
                'username': user_row[1],
                'level': user_row[2],
                'join_date': user_row[3],
                'last_active': user_row[4],
                'assessment_done': bool(user_row[5])
            }
            
            # Progress data
            cursor.execute("""
                SELECT section, level, score, date 
                FROM progress 
                WHERE user_id = ? 
                ORDER BY date DESC
            """, (user_id,))
            progress_data = cursor.fetchall()
            
            # Vocabulary practiced
            cursor.execute("""
                SELECT word, score, last_practiced 
                FROM vocabulary 
                WHERE user_id = ? 
                ORDER BY last_practiced DESC 
                LIMIT 10
            """, (user_id,))
            vocabulary_data = cursor.fetchall()
            
            # Grammar completed
            cursor.execute("""
                SELECT level, topic_id, score, completed_at 
                FROM user_grammar 
                WHERE user_id = ? 
                ORDER BY completed_at DESC
            """, (user_id,))
            grammar_data = cursor.fetchall()
            
            conn.close()
            
            user_info.update({
                'progress_data': progress_data,
                'vocabulary_data': vocabulary_data,
                'grammar_data': grammar_data
            })
            
            return user_info
            
        except Exception as e:
            print(f"Error getting user details: {e}")
            return None
    
    def get_content_stats(self):
        """Get content statistics."""
        try:
            conn = self.get_connection('content')
            cursor = conn.cursor()
            
            # Vocabulary count by level
            cursor.execute("SELECT level, COUNT(*) FROM vocabulary_words GROUP BY level")
            vocab_by_level = dict(cursor.fetchall())
            
            # Grammar lessons count by level
            cursor.execute("SELECT level, COUNT(*) FROM grammar_lessons GROUP BY level")
            grammar_by_level = dict(cursor.fetchall())
            
            # Assessment questions count by level
            cursor.execute("SELECT level, COUNT(*) FROM assessment_questions GROUP BY level")
            assessment_by_level = dict(cursor.fetchall())
            
            # Conversation topics count by level
            cursor.execute("SELECT level, COUNT(*) FROM conversation_topics GROUP BY level")
            conversation_by_level = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'vocabulary': vocab_by_level,
                'grammar': grammar_by_level,
                'assessment': assessment_by_level,
                'conversation': conversation_by_level
            }
        except Exception as e:
            print(f"Error getting content stats: {e}")
            return {}
    
    def get_usage_analytics(self, days=30):
        """Get usage analytics for the last N days."""
        try:
            conn = self.get_connection('user')
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Daily active users
            cursor.execute("""
                SELECT DATE(last_active) as date, COUNT(DISTINCT user_id) as users
                FROM users 
                WHERE last_active >= ?
                GROUP BY DATE(last_active)
                ORDER BY date
            """, (start_date,))
            daily_users = cursor.fetchall()
            
            # Daily progress entries
            cursor.execute("""
                SELECT DATE(date) as date, COUNT(*) as entries
                FROM progress 
                WHERE date >= ?
                GROUP BY DATE(date)
                ORDER BY date
            """, (start_date,))
            daily_progress = cursor.fetchall()
            
            # Section popularity
            cursor.execute("""
                SELECT section, COUNT(*) as count
                FROM progress 
                WHERE date >= ? AND section != 'assessment'
                GROUP BY section
                ORDER BY count DESC
            """, (start_date,))
            section_popularity = cursor.fetchall()
            
            conn.close()
            
            return {
                'daily_users': daily_users,
                'daily_progress': daily_progress,
                'section_popularity': section_popularity
            }
        except Exception as e:
            print(f"Error getting usage analytics: {e}")
            return {}

# Initialize database
admin_db = AdminDatabase()

@app.route('/')
def dashboard():
    """Main dashboard page."""
    user_stats = admin_db.get_user_stats()
    content_stats = admin_db.get_content_stats()
    usage_analytics = admin_db.get_usage_analytics()
    
    return render_template('dashboard.html', 
                         user_stats=user_stats,
                         content_stats=content_stats,
                         usage_analytics=usage_analytics)

@app.route('/users')
def users_list():
    """Users management page."""
    page = request.args.get('page', 1, type=int)
    limit = 20
    offset = (page - 1) * limit
    
    users = admin_db.get_all_users(limit=limit, offset=offset)
    return render_template('users.html', users=users, page=page)

@app.route('/user/<int:user_id>')
def user_details(user_id):
    """User details page."""
    user_info = admin_db.get_user_details(user_id)
    if not user_info:
        flash('User not found', 'error')
        return redirect(url_for('users_list'))
    
    return render_template('user_details.html', user=user_info)

@app.route('/content')
def content_management():
    """Content management page."""
    content_stats = admin_db.get_content_stats()
    return render_template('content.html', content_stats=content_stats)

@app.route('/analytics')
def analytics():
    """Analytics page."""
    days = request.args.get('days', 30, type=int)
    analytics_data = admin_db.get_usage_analytics(days=days)
    user_stats = admin_db.get_user_stats()
    
    return render_template('analytics.html', 
                         analytics=analytics_data,
                         user_stats=user_stats,
                         days=days)

@app.route('/api/chart-data/<chart_type>')
def chart_data(chart_type):
    """API endpoint for chart data."""
    if chart_type == 'users_by_level':
        user_stats = admin_db.get_user_stats()
        return jsonify(user_stats.get('users_by_level', {}))
    
    elif chart_type == 'progress_by_section':
        user_stats = admin_db.get_user_stats()
        return jsonify(user_stats.get('avg_progress', {}))
    
    elif chart_type == 'daily_activity':
        days = request.args.get('days', 30, type=int)
        analytics = admin_db.get_usage_analytics(days=days)
        return jsonify({
            'daily_users': analytics.get('daily_users', []),
            'daily_progress': analytics.get('daily_progress', [])
        })
    
    return jsonify({})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
