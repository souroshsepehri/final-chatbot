"""
Performance monitoring utilities for the chatbot.
"""

import time
import functools
from typing import Dict, List, Optional
from collections import defaultdict, deque
import threading


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self, max_history: int = 100):
        """Initialize performance monitor."""
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Record a performance metric."""
        with self.lock:
            self.metrics[name].append({
                'value': value,
                'timestamp': time.time(),
                'metadata': metadata or {}
            })
    
    def get_average(self, name: str, window_seconds: Optional[int] = None) -> Optional[float]:
        """Get average value for a metric."""
        with self.lock:
            if name not in self.metrics or not self.metrics[name]:
                return None
            
            current_time = time.time()
            values = []
            
            for entry in self.metrics[name]:
                if window_seconds is None or (current_time - entry['timestamp']) <= window_seconds:
                    values.append(entry['value'])
            
            return sum(values) / len(values) if values else None
    
    def get_stats(self, name: str, window_seconds: Optional[int] = None) -> Dict:
        """Get comprehensive stats for a metric."""
        with self.lock:
            if name not in self.metrics or not self.metrics[name]:
                return {}
            
            current_time = time.time()
            values = []
            
            for entry in self.metrics[name]:
                if window_seconds is None or (current_time - entry['timestamp']) <= window_seconds:
                    values.append(entry['value'])
            
            if not values:
                return {}
            
            return {
                'count': len(values),
                'average': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest': values[-1] if values else None
            }
    
    def get_all_stats(self, window_seconds: Optional[int] = None) -> Dict:
        """Get stats for all metrics."""
        with self.lock:
            return {
                name: self.get_stats(name, window_seconds)
                for name in self.metrics.keys()
            }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def time_function(name: str):
    """Decorator to time function execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                performance_monitor.record_metric(f"{name}_success", execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_metric(f"{name}_error", execution_time, {'error': str(e)})
                raise
        return wrapper
    return decorator


def track_api_call(api_name: str):
    """Decorator to track API call performance."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                performance_monitor.record_metric(f"api_{api_name}", execution_time, {
                    'success': True,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                })
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_metric(f"api_{api_name}", execution_time, {
                    'success': False,
                    'error': str(e),
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                })
                raise
        return wrapper
    return decorator


def get_performance_summary() -> Dict:
    """Get a summary of all performance metrics."""
    stats = performance_monitor.get_all_stats(window_seconds=3600)  # Last hour
    
    # Calculate overall performance
    total_requests = sum(stat.get('count', 0) for stat in stats.values())
    avg_response_time = None
    
    if total_requests > 0:
        total_time = sum(stat.get('average', 0) * stat.get('count', 0) for stat in stats.values())
        avg_response_time = total_time / total_requests
    
    return {
        'total_requests_last_hour': total_requests,
        'average_response_time_ms': avg_response_time * 1000 if avg_response_time else None,
        'metrics': stats,
        'recommendations': _generate_recommendations(stats)
    }


def _generate_recommendations(stats: Dict) -> List[str]:
    """Generate performance recommendations based on metrics."""
    recommendations = []
    
    # Check for slow API calls
    for metric_name, stat in stats.items():
        if metric_name.startswith('api_') and stat.get('average', 0) > 5.0:  # > 5 seconds
            recommendations.append(f"API {metric_name[4:]} is slow (avg: {stat['average']:.2f}s)")
        
        if metric_name.startswith('embedding_') and stat.get('average', 0) > 2.0:  # > 2 seconds
            recommendations.append(f"Embedding computation is slow (avg: {stat['average']:.2f}s)")
    
    # Check for high error rates
    for metric_name, stat in stats.items():
        if metric_name.endswith('_error') and stat.get('count', 0) > 10:
            base_metric = metric_name[:-6]  # Remove '_error'
            success_count = stats.get(f"{base_metric}_success", {}).get('count', 0)
            error_count = stat.get('count', 0)
            total_count = success_count + error_count
            
            if total_count > 0 and (error_count / total_count) > 0.1:  # > 10% error rate
                recommendations.append(f"High error rate for {base_metric}: {error_count}/{total_count} ({error_count/total_count*100:.1f}%)")
    
    if not recommendations:
        recommendations.append("Performance looks good!")
    
    return recommendations





















