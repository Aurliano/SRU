#!/usr/bin/env python3
"""
Performance Monitoring System for English Learning Telegram Bot
Real-time monitoring and performance metrics collection
"""

import time
import psutil
import sqlite3
import threading
import json
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Real-time performance monitoring and metrics collection."""
    
    def __init__(self, max_history=1000):
        self.metrics = defaultdict(list)
        self.max_history = max_history
        self.start_time = time.time()
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(deque)
        self.error_counts = defaultdict(int)
        self.active_users = set()
        
        # System metrics
        self.system_metrics = {
            'cpu_usage': deque(maxlen=max_history),
            'memory_usage': deque(maxlen=max_history),
            'disk_usage': deque(maxlen=max_history),
            'network_io': deque(maxlen=max_history)
        }
        
        # Bot-specific metrics
        self.bot_metrics = {
            'messages_processed': 0,
            'commands_executed': defaultdict(int),
            'ai_api_calls': 0,
            'ai_api_latency': deque(maxlen=max_history),
            'database_queries': 0,
            'database_latency': deque(maxlen=max_history),
            'errors': defaultdict(int),
            'user_sessions': defaultdict(int)
        }
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_system(self):
        """Background thread to monitor system metrics."""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_metrics['cpu_usage'].append({
                    'timestamp': datetime.now().isoformat(),
                    'value': cpu_percent
                })
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_metrics['memory_usage'].append({
                    'timestamp': datetime.now().isoformat(),
                    'percent': memory.percent,
                    'used_mb': memory.used / 1024 / 1024,
                    'available_mb': memory.available / 1024 / 1024
                })
                
                # Disk usage
                disk = psutil.disk_usage('.')
                self.system_metrics['disk_usage'].append({
                    'timestamp': datetime.now().isoformat(),
                    'percent': (disk.used / disk.total) * 100,
                    'used_gb': disk.used / 1024 / 1024 / 1024,
                    'free_gb': disk.free / 1024 / 1024 / 1024
                })
                
                # Network I/O
                net_io = psutil.net_io_counters()
                self.system_metrics['network_io'].append({
                    'timestamp': datetime.now().isoformat(),
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                })
                
                time.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(10)
    
    def track_message(self, user_id, message_type='text'):
        """Track incoming message."""
        self.bot_metrics['messages_processed'] += 1
        self.active_users.add(user_id)
        self.bot_metrics['user_sessions'][user_id] += 1
        
        # Track message types
        self.request_counts[f'message_{message_type}'] += 1
    
    def track_command(self, command_name):
        """Track command execution."""
        self.bot_metrics['commands_executed'][command_name] += 1
        self.request_counts[f'command_{command_name}'] += 1
    
    def track_ai_api_call(self, latency_ms, success=True):
        """Track AI API call performance."""
        self.bot_metrics['ai_api_calls'] += 1
        self.bot_metrics['ai_api_latency'].append({
            'timestamp': datetime.now().isoformat(),
            'latency_ms': latency_ms,
            'success': success
        })
        
        if not success:
            self.bot_metrics['errors']['ai_api_error'] += 1
    
    def track_database_query(self, query_type, latency_ms, success=True):
        """Track database query performance."""
        self.bot_metrics['database_queries'] += 1
        self.bot_metrics['database_latency'].append({
            'timestamp': datetime.now().isoformat(),
            'query_type': query_type,
            'latency_ms': latency_ms,
            'success': success
        })
        
        if not success:
            self.bot_metrics['errors'][f'db_{query_type}_error'] += 1
    
    def track_error(self, error_type, error_details=None):
        """Track application errors."""
        self.bot_metrics['errors'][error_type] += 1
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'details': str(error_details) if error_details else None
        }
        
        if 'error_log' not in self.bot_metrics:
            self.bot_metrics['error_log'] = deque(maxlen=self.max_history)
        self.bot_metrics['error_log'].append(error_entry)
    
    def get_current_metrics(self):
        """Get current performance metrics."""
        current_time = datetime.now()
        uptime_seconds = time.time() - self.start_time
        
        # Calculate averages for recent metrics
        recent_cpu = [m['value'] for m in list(self.system_metrics['cpu_usage'])[-10:]]
        recent_memory = [m['percent'] for m in list(self.system_metrics['memory_usage'])[-10:]]
        
        avg_cpu = sum(recent_cpu) / len(recent_cpu) if recent_cpu else 0
        avg_memory = sum(recent_memory) / len(recent_memory) if recent_memory else 0
        
        # AI API performance
        recent_ai_latency = [m['latency_ms'] for m in list(self.bot_metrics['ai_api_latency'])[-50:]]
        avg_ai_latency = sum(recent_ai_latency) / len(recent_ai_latency) if recent_ai_latency else 0
        
        # Database performance
        recent_db_latency = [m['latency_ms'] for m in list(self.bot_metrics['database_latency'])[-50:]]
        avg_db_latency = sum(recent_db_latency) / len(recent_db_latency) if recent_db_latency else 0
        
        return {
            'timestamp': current_time.isoformat(),
            'uptime_seconds': uptime_seconds,
            'uptime_hours': uptime_seconds / 3600,
            'system_performance': {
                'cpu_usage_percent': avg_cpu,
                'memory_usage_percent': avg_memory,
                'active_users_count': len(self.active_users),
                'messages_per_minute': self.calculate_messages_per_minute()
            },
            'bot_performance': {
                'total_messages': self.bot_metrics['messages_processed'],
                'total_ai_calls': self.bot_metrics['ai_api_calls'],
                'total_db_queries': self.bot_metrics['database_queries'],
                'avg_ai_latency_ms': avg_ai_latency,
                'avg_db_latency_ms': avg_db_latency,
                'error_rate_percent': self.calculate_error_rate()
            },
            'command_stats': dict(self.bot_metrics['commands_executed']),
            'error_stats': dict(self.bot_metrics['errors'])
        }
    
    def calculate_messages_per_minute(self):
        """Calculate messages per minute rate."""
        if self.start_time == 0:
            return 0
        
        elapsed_minutes = (time.time() - self.start_time) / 60
        if elapsed_minutes == 0:
            return 0
        
        return self.bot_metrics['messages_processed'] / elapsed_minutes
    
    def calculate_error_rate(self):
        """Calculate overall error rate percentage."""
        total_operations = (
            self.bot_metrics['messages_processed'] + 
            self.bot_metrics['ai_api_calls'] + 
            self.bot_metrics['database_queries']
        )
        
        if total_operations == 0:
            return 0
        
        total_errors = sum(self.bot_metrics['errors'].values())
        return (total_errors / total_operations) * 100
    
    def get_performance_report(self, hours=24):
        """Generate comprehensive performance report."""
        current_metrics = self.get_current_metrics()
        
        # Performance analysis
        performance_analysis = {
            'system_health': self.analyze_system_health(),
            'bot_efficiency': self.analyze_bot_efficiency(),
            'user_satisfaction': self.analyze_user_satisfaction(),
            'scalability_metrics': self.analyze_scalability()
        }
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_period_hours': hours,
            'current_metrics': current_metrics,
            'performance_analysis': performance_analysis,
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def analyze_system_health(self):
        """Analyze overall system health."""
        recent_cpu = [m['value'] for m in list(self.system_metrics['cpu_usage'])[-20:]]
        recent_memory = [m['percent'] for m in list(self.system_metrics['memory_usage'])[-20:]]
        
        avg_cpu = sum(recent_cpu) / len(recent_cpu) if recent_cpu else 0
        avg_memory = sum(recent_memory) / len(recent_memory) if recent_memory else 0
        
        health_score = 100
        
        # CPU health
        if avg_cpu > 80:
            health_score -= 30
        elif avg_cpu > 60:
            health_score -= 15
        
        # Memory health
        if avg_memory > 85:
            health_score -= 25
        elif avg_memory > 70:
            health_score -= 10
        
        # Error rate health
        error_rate = self.calculate_error_rate()
        if error_rate > 5:
            health_score -= 20
        elif error_rate > 2:
            health_score -= 10
        
        return {
            'health_score': max(0, health_score),
            'cpu_status': 'Critical' if avg_cpu > 80 else 'Warning' if avg_cpu > 60 else 'Good',
            'memory_status': 'Critical' if avg_memory > 85 else 'Warning' if avg_memory > 70 else 'Good',
            'error_status': 'Critical' if error_rate > 5 else 'Warning' if error_rate > 2 else 'Good'
        }
    
    def analyze_bot_efficiency(self):
        """Analyze bot operational efficiency."""
        recent_ai_latency = [m['latency_ms'] for m in list(self.bot_metrics['ai_api_latency'])[-100:]]
        recent_db_latency = [m['latency_ms'] for m in list(self.bot_metrics['database_latency'])[-100:]]
        
        avg_ai_latency = sum(recent_ai_latency) / len(recent_ai_latency) if recent_ai_latency else 0
        avg_db_latency = sum(recent_db_latency) / len(recent_db_latency) if recent_db_latency else 0
        
        return {
            'ai_performance': {
                'avg_latency_ms': avg_ai_latency,
                'status': 'Good' if avg_ai_latency < 2000 else 'Warning' if avg_ai_latency < 5000 else 'Critical'
            },
            'database_performance': {
                'avg_latency_ms': avg_db_latency,
                'status': 'Good' if avg_db_latency < 100 else 'Warning' if avg_db_latency < 500 else 'Critical'
            },
            'throughput': {
                'messages_per_minute': self.calculate_messages_per_minute(),
                'status': 'Good' if self.calculate_messages_per_minute() > 10 else 'Normal'
            }
        }
    
    def analyze_user_satisfaction(self):
        """Analyze user satisfaction metrics."""
        total_errors = sum(self.bot_metrics['errors'].values())
        total_messages = self.bot_metrics['messages_processed']
        
        error_rate = (total_errors / total_messages * 100) if total_messages > 0 else 0
        
        # Calculate user retention (simplified)
        unique_users = len(self.active_users)
        avg_sessions_per_user = (
            sum(self.bot_metrics['user_sessions'].values()) / unique_users 
            if unique_users > 0 else 0
        )
        
        satisfaction_score = 100 - (error_rate * 10)  # Simple formula
        
        return {
            'satisfaction_score': max(0, min(100, satisfaction_score)),
            'error_rate_percent': error_rate,
            'unique_users': unique_users,
            'avg_sessions_per_user': avg_sessions_per_user,
            'user_engagement': 'High' if avg_sessions_per_user > 10 else 'Medium' if avg_sessions_per_user > 5 else 'Low'
        }
    
    def analyze_scalability(self):
        """Analyze system scalability metrics."""
        current_load = len(self.active_users)
        messages_per_minute = self.calculate_messages_per_minute()
        
        # Estimate capacity based on current performance
        recent_cpu = [m['value'] for m in list(self.system_metrics['cpu_usage'])[-10:]]
        avg_cpu = sum(recent_cpu) / len(recent_cpu) if recent_cpu else 0
        
        # Simple scalability estimation
        if avg_cpu > 0:
            estimated_max_users = int((80 / avg_cpu) * current_load) if current_load > 0 else 1000
        else:
            estimated_max_users = 1000
        
        return {
            'current_load': current_load,
            'estimated_max_users': estimated_max_users,
            'messages_per_minute': messages_per_minute,
            'scalability_status': 'Good' if current_load < estimated_max_users * 0.5 else 'Warning',
            'bottlenecks': self.identify_bottlenecks()
        }
    
    def identify_bottlenecks(self):
        """Identify potential system bottlenecks."""
        bottlenecks = []
        
        # CPU bottleneck
        recent_cpu = [m['value'] for m in list(self.system_metrics['cpu_usage'])[-10:]]
        avg_cpu = sum(recent_cpu) / len(recent_cpu) if recent_cpu else 0
        if avg_cpu > 70:
            bottlenecks.append('High CPU usage')
        
        # Memory bottleneck
        recent_memory = [m['percent'] for m in list(self.system_metrics['memory_usage'])[-10:]]
        avg_memory = sum(recent_memory) / len(recent_memory) if recent_memory else 0
        if avg_memory > 75:
            bottlenecks.append('High memory usage')
        
        # AI API bottleneck
        recent_ai_latency = [m['latency_ms'] for m in list(self.bot_metrics['ai_api_latency'])[-20:]]
        avg_ai_latency = sum(recent_ai_latency) / len(recent_ai_latency) if recent_ai_latency else 0
        if avg_ai_latency > 3000:
            bottlenecks.append('Slow AI API responses')
        
        # Database bottleneck
        recent_db_latency = [m['latency_ms'] for m in list(self.bot_metrics['database_latency'])[-20:]]
        avg_db_latency = sum(recent_db_latency) / len(recent_db_latency) if recent_db_latency else 0
        if avg_db_latency > 200:
            bottlenecks.append('Slow database queries')
        
        return bottlenecks
    
    def generate_recommendations(self):
        """Generate performance improvement recommendations."""
        recommendations = []
        
        system_health = self.analyze_system_health()
        bot_efficiency = self.analyze_bot_efficiency()
        scalability = self.analyze_scalability()
        
        # System recommendations
        if system_health['cpu_status'] in ['Warning', 'Critical']:
            recommendations.append({
                'type': 'System',
                'priority': 'High' if system_health['cpu_status'] == 'Critical' else 'Medium',
                'recommendation': 'Optimize CPU usage or upgrade server capacity'
            })
        
        if system_health['memory_status'] in ['Warning', 'Critical']:
            recommendations.append({
                'type': 'System',
                'priority': 'High' if system_health['memory_status'] == 'Critical' else 'Medium',
                'recommendation': 'Optimize memory usage or increase RAM'
            })
        
        # Bot performance recommendations
        if bot_efficiency['ai_performance']['status'] in ['Warning', 'Critical']:
            recommendations.append({
                'type': 'Bot',
                'priority': 'Medium',
                'recommendation': 'Optimize AI API calls or implement caching'
            })
        
        if bot_efficiency['database_performance']['status'] in ['Warning', 'Critical']:
            recommendations.append({
                'type': 'Database',
                'priority': 'High',
                'recommendation': 'Optimize database queries and add indexes'
            })
        
        # Scalability recommendations
        if scalability['scalability_status'] == 'Warning':
            recommendations.append({
                'type': 'Scalability',
                'priority': 'Medium',
                'recommendation': 'Plan for horizontal scaling or load balancing'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'General',
                'priority': 'Low',
                'recommendation': 'System is performing well. Continue monitoring.'
            })
        
        return recommendations
    
    def export_metrics(self, filename=None):
        """Export performance metrics to file."""
        if filename is None:
            filename = f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'system_metrics': {
                key: list(value) for key, value in self.system_metrics.items()
            },
            'bot_metrics': {
                key: list(value) if hasattr(value, '__iter__') and not isinstance(value, (str, dict)) 
                else dict(value) if isinstance(value, defaultdict) 
                else value
                for key, value in self.bot_metrics.items()
            },
            'current_status': self.get_current_metrics()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        return filename
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

# Decorator for tracking function performance
def track_performance(monitor, operation_type='general'):
    """Decorator to track function execution performance."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                monitor.track_error(f"{operation_type}_error", str(e))
                raise
            finally:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                if operation_type == 'ai_api':
                    monitor.track_ai_api_call(latency_ms, success)
                elif operation_type == 'database':
                    monitor.track_database_query('general', latency_ms, success)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                monitor.track_error(f"{operation_type}_error", str(e))
                raise
            finally:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                if operation_type == 'ai_api':
                    monitor.track_ai_api_call(latency_ms, success)
                elif operation_type == 'database':
                    monitor.track_database_query('general', latency_ms, success)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global performance monitor instance
global_monitor = PerformanceMonitor()

# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Test the performance monitor
    monitor = PerformanceMonitor()
    
    # Simulate some operations
    for i in range(10):
        monitor.track_message(f"user_{i}", 'text')
        monitor.track_command('start')
        monitor.track_ai_api_call(1500 + i * 100, True)
        monitor.track_database_query('SELECT', 50 + i * 10, True)
        time.sleep(0.1)
    
    # Get current metrics
    metrics = monitor.get_current_metrics()
    print("Current Metrics:")
    print(json.dumps(metrics, indent=2))
    
    # Generate performance report
    report = monitor.get_performance_report()
    print("\nPerformance Report:")
    print(json.dumps(report, indent=2, default=str))
    
    # Export metrics
    filename = monitor.export_metrics()
    print(f"\nMetrics exported to: {filename}")
    
    # Stop monitoring
    monitor.stop_monitoring()
