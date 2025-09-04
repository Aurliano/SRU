#!/usr/bin/env python3
"""
Integration module for adding analytics and performance monitoring to the main bot
This module provides decorators and middleware to seamlessly integrate monitoring
"""

import functools
import time
import logging
from datetime import datetime
from performance_monitor import global_monitor, track_performance
from analytics_engine import AdvancedAnalytics

logger = logging.getLogger(__name__)

class BotAnalyticsIntegration:
    """Integration class for analytics and monitoring."""
    
    def __init__(self):
        self.monitor = global_monitor
        self.analytics = AdvancedAnalytics()
        self.session_start_times = {}
    
    def track_user_message(self, user_id, message_type='text', command=None):
        """Track user message and extract insights."""
        try:
            # Track basic message
            self.monitor.track_message(user_id, message_type)
            
            # Track command if present
            if command:
                self.monitor.track_command(command)
            
            # Update session tracking
            if user_id not in self.session_start_times:
                self.session_start_times[user_id] = time.time()
            
            logger.info(f"Tracked message from user {user_id}: {message_type}")
            
        except Exception as e:
            logger.error(f"Error tracking user message: {e}")
            self.monitor.track_error('message_tracking_error', str(e))
    
    def track_ai_interaction(self, user_id, section, prompt_length, response_time_ms, success=True, error=None):
        """Track AI interaction with detailed metrics."""
        try:
            # Track AI API call
            self.monitor.track_ai_api_call(response_time_ms, success)
            
            # Track section-specific usage
            self.monitor.request_counts[f'ai_{section}'] += 1
            
            if not success and error:
                self.monitor.track_error(f'ai_{section}_error', error)
            
            logger.info(f"Tracked AI interaction: user={user_id}, section={section}, "
                       f"response_time={response_time_ms}ms, success={success}")
            
        except Exception as e:
            logger.error(f"Error tracking AI interaction: {e}")
            self.monitor.track_error('ai_tracking_error', str(e))
    
    def track_database_operation(self, operation_type, execution_time_ms, success=True, error=None):
        """Track database operations."""
        try:
            self.monitor.track_database_query(operation_type, execution_time_ms, success)
            
            if not success and error:
                self.monitor.track_error(f'db_{operation_type}_error', error)
            
            logger.debug(f"Tracked DB operation: {operation_type}, time={execution_time_ms}ms, success={success}")
            
        except Exception as e:
            logger.error(f"Error tracking database operation: {e}")
    
    def track_user_progress(self, user_id, section, score, level):
        """Track user learning progress."""
        try:
            # This integrates with the existing progress tracking
            # Additional analytics can be added here
            
            progress_data = {
                'user_id': user_id,
                'section': section,
                'score': score,
                'level': level,
                'timestamp': datetime.now().isoformat()
            }
            
            # You could store this in a separate analytics database
            # or send to external analytics service
            
            logger.info(f"Tracked user progress: {progress_data}")
            
        except Exception as e:
            logger.error(f"Error tracking user progress: {e}")
            self.monitor.track_error('progress_tracking_error', str(e))
    
    def track_session_end(self, user_id):
        """Track when user session ends."""
        try:
            if user_id in self.session_start_times:
                session_duration = time.time() - self.session_start_times[user_id]
                
                # Track session duration
                if not hasattr(self.monitor.bot_metrics, 'session_durations'):
                    self.monitor.bot_metrics['session_durations'] = []
                
                self.monitor.bot_metrics['session_durations'].append({
                    'user_id': user_id,
                    'duration_seconds': session_duration,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Clean up
                del self.session_start_times[user_id]
                
                logger.info(f"Tracked session end: user={user_id}, duration={session_duration:.1f}s")
        
        except Exception as e:
            logger.error(f"Error tracking session end: {e}")
    
    def get_real_time_metrics(self):
        """Get real-time metrics for admin panel."""
        try:
            return self.monitor.get_current_metrics()
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {}
    
    def generate_performance_alert(self, threshold_type='error_rate', threshold_value=5.0):
        """Generate performance alerts when thresholds are exceeded."""
        try:
            current_metrics = self.monitor.get_current_metrics()
            alerts = []
            
            if threshold_type == 'error_rate':
                error_rate = current_metrics.get('bot_performance', {}).get('error_rate_percent', 0)
                if error_rate > threshold_value:
                    alerts.append({
                        'type': 'HIGH_ERROR_RATE',
                        'value': error_rate,
                        'threshold': threshold_value,
                        'timestamp': datetime.now().isoformat(),
                        'severity': 'HIGH' if error_rate > threshold_value * 2 else 'MEDIUM'
                    })
            
            elif threshold_type == 'response_time':
                ai_latency = current_metrics.get('bot_performance', {}).get('avg_ai_latency_ms', 0)
                if ai_latency > threshold_value:
                    alerts.append({
                        'type': 'HIGH_RESPONSE_TIME',
                        'value': ai_latency,
                        'threshold': threshold_value,
                        'timestamp': datetime.now().isoformat(),
                        'severity': 'HIGH' if ai_latency > threshold_value * 1.5 else 'MEDIUM'
                    })
            
            elif threshold_type == 'system_load':
                # Would need to implement system load checking
                pass
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating performance alert: {e}")
            return []

# Global integration instance
bot_analytics = BotAnalyticsIntegration()

# Decorators for easy integration
def track_telegram_handler(handler_type='message'):
    """Decorator to track Telegram handlers."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            start_time = time.time()
            user_id = None
            success = True
            error = None
            
            try:
                # Extract user ID
                if update.effective_user:
                    user_id = update.effective_user.id
                elif update.effective_chat:
                    user_id = update.effective_chat.id
                
                # Track the handler call
                if user_id:
                    if handler_type == 'command':
                        command_name = getattr(func, '__name__', 'unknown')
                        bot_analytics.track_user_message(user_id, 'command', command_name)
                    else:
                        bot_analytics.track_user_message(user_id, handler_type)
                
                # Execute the handler
                result = await func(update, context, *args, **kwargs)
                return result
                
            except Exception as e:
                success = False
                error = str(e)
                bot_analytics.monitor.track_error(f'{handler_type}_handler_error', error)
                raise
            
            finally:
                # Track execution time
                execution_time = (time.time() - start_time) * 1000
                logger.debug(f"Handler {func.__name__} executed in {execution_time:.1f}ms")
        
        return wrapper
    return decorator

def track_ai_call(section='general'):
    """Decorator to track AI API calls."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            user_id = None
            
            try:
                # Try to extract user_id from arguments
                if args and hasattr(args[0], 'effective_user'):
                    user_id = args[0].effective_user.id
                
                result = await func(*args, **kwargs)
                return result
                
            except Exception as e:
                success = False
                error = str(e)
                raise
            
            finally:
                execution_time = (time.time() - start_time) * 1000
                bot_analytics.track_ai_interaction(
                    user_id or 0, section, 0, execution_time, success, error
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            user_id = None
            
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                success = False
                error = str(e)
                raise
            
            finally:
                execution_time = (time.time() - start_time) * 1000
                bot_analytics.track_ai_interaction(
                    user_id or 0, section, 0, execution_time, success, error
                )
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def track_database_call(operation_type='query'):
    """Decorator to track database calls."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                success = False
                error = str(e)
                raise
            
            finally:
                execution_time = (time.time() - start_time) * 1000
                bot_analytics.track_database_operation(operation_type, execution_time, success, error)
        
        return wrapper
    return decorator

# Middleware for automatic tracking
class AnalyticsMiddleware:
    """Middleware to automatically track all bot interactions."""
    
    def __init__(self):
        self.analytics = bot_analytics
    
    async def process_update(self, update, context):
        """Process each update and track metrics."""
        try:
            # Track the update
            if update.message:
                user_id = update.effective_user.id if update.effective_user else None
                if user_id:
                    message_type = 'text'
                    if update.message.photo:
                        message_type = 'photo'
                    elif update.message.voice:
                        message_type = 'voice'
                    elif update.message.document:
                        message_type = 'document'
                    
                    self.analytics.track_user_message(user_id, message_type)
            
            elif update.callback_query:
                user_id = update.effective_user.id if update.effective_user else None
                if user_id:
                    self.analytics.track_user_message(user_id, 'callback_query')
            
        except Exception as e:
            logger.error(f"Error in analytics middleware: {e}")

# Health check endpoint for monitoring
def get_health_status():
    """Get current health status of the bot."""
    try:
        current_metrics = bot_analytics.get_real_time_metrics()
        performance_report = bot_analytics.monitor.get_performance_report(hours=1)
        
        # Determine overall health
        system_health = performance_report.get('performance_analysis', {}).get('system_health', {})
        health_score = system_health.get('health_score', 0)
        
        if health_score >= 80:
            status = 'HEALTHY'
        elif health_score >= 60:
            status = 'WARNING'
        else:
            status = 'CRITICAL'
        
        return {
            'status': status,
            'health_score': health_score,
            'timestamp': datetime.now().isoformat(),
            'uptime_hours': current_metrics.get('uptime_hours', 0),
            'active_users': current_metrics.get('system_performance', {}).get('active_users_count', 0),
            'error_rate': current_metrics.get('bot_performance', {}).get('error_rate_percent', 0),
            'response_time_ms': current_metrics.get('bot_performance', {}).get('avg_ai_latency_ms', 0)
        }
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Export functions for use in main bot
__all__ = [
    'bot_analytics',
    'track_telegram_handler',
    'track_ai_call',
    'track_database_call',
    'AnalyticsMiddleware',
    'get_health_status'
]

# Example integration code for bot.py
"""
# Add to bot.py imports:
from bot_integration import track_telegram_handler, track_ai_call, bot_analytics

# Add decorators to handlers:
@track_telegram_handler('command')
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # existing code
    pass

@track_ai_call('vocabulary')
async def handle_vocabulary_practice(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    # existing code
    pass

# Add to main function:
def main():
    # existing code
    
    # Add health check endpoint (if using webhooks)
    application.add_handler(MessageHandler(filters.Regex(r'/health'), lambda u, c: get_health_status()))
    
    # existing code
"""
