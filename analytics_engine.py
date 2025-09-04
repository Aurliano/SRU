#!/usr/bin/env python3
"""
Advanced Analytics Engine for English Learning Telegram Bot
Comprehensive analytics and metrics for research and thesis purposes
"""

import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    """Advanced analytics engine for comprehensive data analysis."""
    
    def __init__(self, user_db_path="user_data.db", content_db_path="content_data.db"):
        self.user_db_path = user_db_path
        self.content_db_path = content_db_path
        
        # Set up matplotlib for Persian text
        plt.rcParams['font.family'] = ['Arial Unicode MS', 'Tahoma', 'DejaVu Sans']
        
    def get_connection(self, db_type='user'):
        """Get database connection."""
        db_path = self.user_db_path if db_type == 'user' else self.content_db_path
        return sqlite3.connect(db_path)
    
    def get_comprehensive_user_stats(self):
        """Get comprehensive user statistics for research analysis."""
        try:
            conn = self.get_connection('user')
            
            # Basic user statistics
            basic_stats = pd.read_sql_query("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN assessment_done = 1 THEN 1 END) as assessed_users,
                    COUNT(CASE WHEN last_active >= date('now', '-7 days') THEN 1 END) as active_7d,
                    COUNT(CASE WHEN last_active >= date('now', '-30 days') THEN 1 END) as active_30d,
                    AVG(julianday('now') - julianday(join_date)) as avg_user_age_days
                FROM users
            """, conn)
            
            # User distribution by level
            level_dist = pd.read_sql_query("""
                SELECT level, COUNT(*) as count 
                FROM users 
                GROUP BY level
            """, conn)
            
            # User retention analysis
            retention_data = pd.read_sql_query("""
                SELECT 
                    u.user_id,
                    u.join_date,
                    u.last_active,
                    julianday(u.last_active) - julianday(u.join_date) as days_active,
                    COUNT(p.id) as total_activities
                FROM users u
                LEFT JOIN progress p ON u.user_id = p.user_id
                GROUP BY u.user_id
            """, conn)
            
            conn.close()
            
            return {
                'basic_stats': basic_stats.to_dict('records')[0],
                'level_distribution': level_dist.to_dict('records'),
                'retention_data': retention_data.to_dict('records')
            }
        except Exception as e:
            print(f"Error getting comprehensive user stats: {e}")
            return {}
    
    def get_learning_effectiveness_metrics(self):
        """Analyze learning effectiveness across different sections."""
        try:
            conn = self.get_connection('user')
            
            # Progress analysis by section and level
            progress_analysis = pd.read_sql_query("""
                SELECT 
                    section,
                    level,
                    COUNT(*) as total_sessions,
                    AVG(score) as avg_score,
                    MIN(score) as min_score,
                    MAX(score) as max_score,
                    STDDEV(score) as score_stddev
                FROM progress 
                WHERE section IN ('vocabulary', 'grammar', 'conversation')
                GROUP BY section, level
                ORDER BY section, level
            """, conn)
            
            # Learning progression over time
            learning_progression = pd.read_sql_query("""
                SELECT 
                    user_id,
                    section,
                    level,
                    score,
                    date,
                    ROW_NUMBER() OVER (PARTITION BY user_id, section ORDER BY date) as session_number
                FROM progress 
                WHERE section IN ('vocabulary', 'grammar', 'conversation')
                ORDER BY user_id, section, date
            """, conn)
            
            # Assessment vs practice correlation
            assessment_correlation = pd.read_sql_query("""
                SELECT 
                    u.user_id,
                    u.level,
                    a.score as assessment_score,
                    AVG(p.score) as avg_practice_score,
                    COUNT(p.id) as practice_sessions
                FROM users u
                JOIN progress a ON u.user_id = a.user_id AND a.section = 'assessment'
                LEFT JOIN progress p ON u.user_id = p.user_id AND p.section != 'assessment'
                GROUP BY u.user_id, u.level, a.score
                HAVING practice_sessions > 5
            """, conn)
            
            conn.close()
            
            return {
                'progress_analysis': progress_analysis.to_dict('records'),
                'learning_progression': learning_progression.to_dict('records'),
                'assessment_correlation': assessment_correlation.to_dict('records')
            }
        except Exception as e:
            print(f"Error getting learning effectiveness metrics: {e}")
            return {}
    
    def get_engagement_metrics(self):
        """Analyze user engagement patterns."""
        try:
            conn = self.get_connection('user')
            
            # Daily activity patterns
            daily_activity = pd.read_sql_query("""
                SELECT 
                    strftime('%H', date) as hour_of_day,
                    COUNT(*) as activity_count
                FROM progress 
                GROUP BY strftime('%H', date)
                ORDER BY hour_of_day
            """, conn)
            
            # Weekly patterns
            weekly_activity = pd.read_sql_query("""
                SELECT 
                    CASE strftime('%w', date)
                        WHEN '0' THEN 'Sunday'
                        WHEN '1' THEN 'Monday' 
                        WHEN '2' THEN 'Tuesday'
                        WHEN '3' THEN 'Wednesday'
                        WHEN '4' THEN 'Thursday'
                        WHEN '5' THEN 'Friday'
                        WHEN '6' THEN 'Saturday'
                    END as day_of_week,
                    COUNT(*) as activity_count
                FROM progress 
                GROUP BY strftime('%w', date)
                ORDER BY strftime('%w', date)
            """, conn)
            
            # Session length analysis (based on consecutive activities)
            session_analysis = pd.read_sql_query("""
                SELECT 
                    user_id,
                    date(date) as session_date,
                    COUNT(*) as activities_per_session,
                    section
                FROM progress 
                GROUP BY user_id, date(date), section
            """, conn)
            
            # User journey analysis
            user_journey = pd.read_sql_query("""
                SELECT 
                    user_id,
                    section,
                    COUNT(*) as section_usage,
                    MIN(date) as first_use,
                    MAX(date) as last_use,
                    julianday(MAX(date)) - julianday(MIN(date)) as usage_span_days
                FROM progress 
                WHERE section IN ('vocabulary', 'grammar', 'conversation')
                GROUP BY user_id, section
            """, conn)
            
            conn.close()
            
            return {
                'daily_activity': daily_activity.to_dict('records'),
                'weekly_activity': weekly_activity.to_dict('records'),
                'session_analysis': session_analysis.to_dict('records'),
                'user_journey': user_journey.to_dict('records')
            }
        except Exception as e:
            print(f"Error getting engagement metrics: {e}")
            return {}
    
    def get_ai_performance_metrics(self):
        """Analyze AI scoring and feedback performance."""
        try:
            conn = self.get_connection('user')
            
            # Score distribution analysis
            score_distribution = pd.read_sql_query("""
                SELECT 
                    section,
                    level,
                    CASE 
                        WHEN score >= 90 THEN 'Excellent (90-100)'
                        WHEN score >= 80 THEN 'Good (80-89)'
                        WHEN score >= 70 THEN 'Average (70-79)'
                        WHEN score >= 60 THEN 'Below Average (60-69)'
                        ELSE 'Poor (<60)'
                    END as score_range,
                    COUNT(*) as count,
                    AVG(score) as avg_score_in_range
                FROM progress 
                WHERE section IN ('vocabulary', 'grammar', 'conversation')
                GROUP BY section, level, score_range
                ORDER BY section, level, avg_score_in_range DESC
            """, conn)
            
            # Improvement tracking
            improvement_tracking = pd.read_sql_query("""
                WITH user_progress AS (
                    SELECT 
                        user_id,
                        section,
                        score,
                        date,
                        ROW_NUMBER() OVER (PARTITION BY user_id, section ORDER BY date) as attempt_number,
                        LAG(score) OVER (PARTITION BY user_id, section ORDER BY date) as previous_score
                    FROM progress 
                    WHERE section IN ('vocabulary', 'grammar', 'conversation')
                )
                SELECT 
                    section,
                    attempt_number,
                    COUNT(*) as total_attempts,
                    AVG(score) as avg_score,
                    AVG(score - COALESCE(previous_score, score)) as avg_improvement,
                    COUNT(CASE WHEN score > COALESCE(previous_score, 0) THEN 1 END) as improved_attempts
                FROM user_progress 
                WHERE attempt_number <= 10  -- Focus on first 10 attempts
                GROUP BY section, attempt_number
                ORDER BY section, attempt_number
            """, conn)
            
            conn.close()
            
            return {
                'score_distribution': score_distribution.to_dict('records'),
                'improvement_tracking': improvement_tracking.to_dict('records')
            }
        except Exception as e:
            print(f"Error getting AI performance metrics: {e}")
            return {}
    
    def get_content_effectiveness_metrics(self):
        """Analyze effectiveness of different content types."""
        try:
            conn_user = self.get_connection('user')
            conn_content = self.get_connection('content')
            
            # Vocabulary effectiveness
            vocab_effectiveness = pd.read_sql_query("""
                SELECT 
                    v.word,
                    v.level,
                    COUNT(*) as practice_count,
                    AVG(v.score) as avg_score,
                    MIN(v.score) as min_score,
                    MAX(v.score) as max_score,
                    COUNT(DISTINCT v.user_id) as unique_users
                FROM vocabulary v
                GROUP BY v.word, v.level
                HAVING practice_count >= 3  -- Words practiced by at least 3 sessions
                ORDER BY avg_score DESC, practice_count DESC
            """, conn_user)
            
            # Grammar lesson effectiveness
            grammar_effectiveness = pd.read_sql_query("""
                SELECT 
                    ug.topic_id,
                    ug.level,
                    COUNT(*) as completion_count,
                    AVG(ug.score) as avg_score,
                    MIN(ug.score) as min_score,
                    MAX(ug.score) as max_score,
                    COUNT(DISTINCT ug.user_id) as unique_users
                FROM user_grammar ug
                GROUP BY ug.topic_id, ug.level
                ORDER BY avg_score DESC, completion_count DESC
            """, conn_user)
            
            # Level progression analysis
            level_progression = pd.read_sql_query("""
                WITH user_levels AS (
                    SELECT 
                        user_id,
                        level,
                        join_date,
                        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY join_date) as level_sequence
                    FROM (
                        SELECT DISTINCT 
                            user_id, 
                            level,
                            MIN(date) as join_date
                        FROM progress 
                        GROUP BY user_id, level
                    )
                )
                SELECT 
                    level,
                    level_sequence,
                    COUNT(*) as user_count,
                    AVG(julianday('now') - julianday(join_date)) as avg_time_in_level
                FROM user_levels
                GROUP BY level, level_sequence
                ORDER BY level_sequence, level
            """, conn_user)
            
            conn_user.close()
            conn_content.close()
            
            return {
                'vocabulary_effectiveness': vocab_effectiveness.to_dict('records'),
                'grammar_effectiveness': grammar_effectiveness.to_dict('records'),
                'level_progression': level_progression.to_dict('records')
            }
        except Exception as e:
            print(f"Error getting content effectiveness metrics: {e}")
            return {}
    
    def generate_statistical_report(self):
        """Generate comprehensive statistical report."""
        try:
            # Collect all metrics
            user_stats = self.get_comprehensive_user_stats()
            learning_metrics = self.get_learning_effectiveness_metrics()
            engagement_metrics = self.get_engagement_metrics()
            ai_metrics = self.get_ai_performance_metrics()
            content_metrics = self.get_content_effectiveness_metrics()
            
            # Statistical analysis
            report = {
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_users': user_stats.get('basic_stats', {}).get('total_users', 0),
                    'assessed_users': user_stats.get('basic_stats', {}).get('assessed_users', 0),
                    'active_users_7d': user_stats.get('basic_stats', {}).get('active_7d', 0),
                    'avg_user_age_days': user_stats.get('basic_stats', {}).get('avg_user_age_days', 0)
                },
                'user_analytics': user_stats,
                'learning_effectiveness': learning_metrics,
                'engagement_patterns': engagement_metrics,
                'ai_performance': ai_metrics,
                'content_effectiveness': content_metrics,
                'statistical_insights': self.calculate_statistical_insights()
            }
            
            return report
        except Exception as e:
            print(f"Error generating statistical report: {e}")
            return {}
    
    def calculate_statistical_insights(self):
        """Calculate advanced statistical insights."""
        try:
            conn = self.get_connection('user')
            
            # Get all progress data for statistical analysis
            df = pd.read_sql_query("""
                SELECT 
                    user_id,
                    section,
                    level,
                    score,
                    date,
                    julianday(date) - julianday((SELECT MIN(date) FROM progress)) as days_since_start
                FROM progress 
                WHERE section IN ('vocabulary', 'grammar', 'conversation')
                ORDER BY user_id, section, date
            """, conn)
            
            conn.close()
            
            if df.empty:
                return {"error": "No progress data available for analysis"}
            
            insights = {}
            
            # Overall score statistics
            insights['overall_score_stats'] = {
                'mean': float(df['score'].mean()),
                'median': float(df['score'].median()),
                'std_dev': float(df['score'].std()),
                'min': float(df['score'].min()),
                'max': float(df['score'].max()),
                'q25': float(df['score'].quantile(0.25)),
                'q75': float(df['score'].quantile(0.75))
            }
            
            # Section comparison (ANOVA)
            section_groups = [group['score'].values for name, group in df.groupby('section')]
            if len(section_groups) > 1:
                f_stat, p_value = stats.f_oneway(*section_groups)
                insights['section_comparison'] = {
                    'f_statistic': float(f_stat),
                    'p_value': float(p_value),
                    'significant_difference': p_value < 0.05
                }
            
            # Learning curve analysis
            for section in df['section'].unique():
                section_data = df[df['section'] == section].copy()
                if len(section_data) > 10:  # Need sufficient data
                    # Calculate correlation between time and score
                    correlation, p_val = stats.pearsonr(section_data['days_since_start'], section_data['score'])
                    insights[f'{section}_learning_curve'] = {
                        'correlation_with_time': float(correlation),
                        'p_value': float(p_val),
                        'improving_over_time': correlation > 0 and p_val < 0.05
                    }
            
            # User performance distribution
            user_avg_scores = df.groupby('user_id')['score'].mean()
            insights['user_performance_distribution'] = {
                'high_performers_pct': float((user_avg_scores >= 80).mean() * 100),
                'medium_performers_pct': float(((user_avg_scores >= 60) & (user_avg_scores < 80)).mean() * 100),
                'low_performers_pct': float((user_avg_scores < 60).mean() * 100)
            }
            
            return insights
            
        except Exception as e:
            print(f"Error calculating statistical insights: {e}")
            return {"error": str(e)}
    
    def export_analytics_data(self, format='json', filename=None):
        """Export analytics data in various formats."""
        if filename is None:
            filename = f"bot_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        report = self.generate_statistical_report()
        
        if format.lower() == 'json':
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        elif format.lower() == 'csv':
            # Export key metrics as CSV
            try:
                conn = self.get_connection('user')
                
                # Export progress data
                df_progress = pd.read_sql_query("""
                    SELECT * FROM progress ORDER BY user_id, date
                """, conn)
                df_progress.to_csv(f"{filename}_progress.csv", index=False)
                
                # Export user data
                df_users = pd.read_sql_query("""
                    SELECT * FROM users ORDER BY user_id
                """, conn)
                df_users.to_csv(f"{filename}_users.csv", index=False)
                
                # Export vocabulary data
                df_vocab = pd.read_sql_query("""
                    SELECT * FROM vocabulary ORDER BY user_id, last_practiced
                """, conn)
                df_vocab.to_csv(f"{filename}_vocabulary.csv", index=False)
                
                conn.close()
                
            except Exception as e:
                print(f"Error exporting CSV data: {e}")
        
        return f"Analytics data exported as {filename}.{format}"
    
    def generate_research_plots(self, save_path="analytics_plots"):
        """Generate research-quality plots for thesis."""
        import os
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        try:
            # Set style for research plots
            plt.style.use('seaborn-v0_8')
            
            # Plot 1: Learning Progression Over Time
            conn = self.get_connection('user')
            df_progress = pd.read_sql_query("""
                SELECT 
                    section,
                    date,
                    AVG(score) as avg_score,
                    COUNT(*) as session_count
                FROM progress 
                WHERE section IN ('vocabulary', 'grammar', 'conversation')
                GROUP BY section, date(date)
                ORDER BY date
            """, conn)
            
            if not df_progress.empty:
                plt.figure(figsize=(12, 8))
                for section in df_progress['section'].unique():
                    section_data = df_progress[df_progress['section'] == section]
                    plt.plot(pd.to_datetime(section_data['date']), 
                           section_data['avg_score'], 
                           marker='o', label=section.title(), linewidth=2)
                
                plt.title('Learning Progression Over Time by Section', fontsize=16, fontweight='bold')
                plt.xlabel('Date', fontsize=12)
                plt.ylabel('Average Score', fontsize=12)
                plt.legend(fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(f"{save_path}/learning_progression.png", dpi=300, bbox_inches='tight')
                plt.close()
            
            # Plot 2: Score Distribution by Section
            df_scores = pd.read_sql_query("""
                SELECT section, score FROM progress 
                WHERE section IN ('vocabulary', 'grammar', 'conversation')
            """, conn)
            
            if not df_scores.empty:
                plt.figure(figsize=(12, 8))
                sections = df_scores['section'].unique()
                
                for i, section in enumerate(sections):
                    plt.subplot(2, 2, i+1)
                    section_scores = df_scores[df_scores['section'] == section]['score']
                    plt.hist(section_scores, bins=20, alpha=0.7, color=plt.cm.Set3(i))
                    plt.title(f'{section.title()} Score Distribution')
                    plt.xlabel('Score')
                    plt.ylabel('Frequency')
                    plt.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.savefig(f"{save_path}/score_distributions.png", dpi=300, bbox_inches='tight')
                plt.close()
            
            # Plot 3: User Engagement Heatmap
            df_engagement = pd.read_sql_query("""
                SELECT 
                    strftime('%H', date) as hour,
                    CASE strftime('%w', date)
                        WHEN '0' THEN 'Sun'
                        WHEN '1' THEN 'Mon' 
                        WHEN '2' THEN 'Tue'
                        WHEN '3' THEN 'Wed'
                        WHEN '4' THEN 'Thu'
                        WHEN '5' THEN 'Fri'
                        WHEN '6' THEN 'Sat'
                    END as day,
                    COUNT(*) as activity_count
                FROM progress 
                GROUP BY strftime('%H', date), strftime('%w', date)
            """, conn)
            
            if not df_engagement.empty:
                # Create heatmap data
                heatmap_data = df_engagement.pivot(index='hour', columns='day', values='activity_count')
                heatmap_data = heatmap_data.fillna(0)
                
                plt.figure(figsize=(10, 8))
                sns.heatmap(heatmap_data, annot=True, fmt='g', cmap='YlOrRd', cbar_kws={'label': 'Activity Count'})
                plt.title('User Activity Heatmap (Hour vs Day of Week)', fontsize=16, fontweight='bold')
                plt.xlabel('Day of Week', fontsize=12)
                plt.ylabel('Hour of Day', fontsize=12)
                plt.tight_layout()
                plt.savefig(f"{save_path}/engagement_heatmap.png", dpi=300, bbox_inches='tight')
                plt.close()
            
            conn.close()
            
            return f"Research plots saved to {save_path}/"
            
        except Exception as e:
            print(f"Error generating research plots: {e}")
            return f"Error: {e}"

# Main execution for testing
if __name__ == "__main__":
    analytics = AdvancedAnalytics()
    
    print("🔍 Generating comprehensive analytics report...")
    report = analytics.generate_statistical_report()
    
    print("📊 Exporting analytics data...")
    analytics.export_analytics_data('json')
    analytics.export_analytics_data('csv')
    
    print("📈 Generating research plots...")
    analytics.generate_research_plots()
    
    print("✅ Advanced analytics completed!")
    
    # Print summary
    if 'summary' in report:
        summary = report['summary']
        print(f"\n📋 Summary:")
        print(f"   Total Users: {summary.get('total_users', 0)}")
        print(f"   Assessed Users: {summary.get('assessed_users', 0)}")
        print(f"   Active Users (7d): {summary.get('active_users_7d', 0)}")
        print(f"   Avg User Age: {summary.get('avg_user_age_days', 0):.1f} days")
