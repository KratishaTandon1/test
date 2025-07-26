"""
Performance monitoring and optimization module
Ensures time and size compliance while maintaining accuracy
"""

import time
import psutil
import os
import sys
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    processing_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    files_processed: int
    avg_time_per_file: float
    peak_memory_mb: float
    
class PerformanceMonitor:
    """Monitors and optimizes performance for strict compliance"""
    
    def __init__(self, max_processing_time: float = 10.0, max_memory_mb: float = 200.0):
        self.max_processing_time = max_processing_time  # 10 seconds for 50-page PDF
        self.max_memory_mb = max_memory_mb  # 200MB max model size
        self.process = psutil.Process()
        self.metrics_history: List[PerformanceMetrics] = []
        self.cpu_count = os.cpu_count() or 8  # Assume 8 CPUs if unknown
    
    @contextmanager
    def monitor_extraction(self, file_count: int = 1):
        """Context manager for monitoring extraction performance"""
        # Record initial state
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_cpu_times = self.process.cpu_times()
        peak_memory = start_memory
        
        try:
            yield self
            
        finally:
            # Calculate final metrics
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            end_cpu_times = self.process.cpu_times()
            
            processing_time = end_time - start_time
            avg_time_per_file = processing_time / max(1, file_count)
            cpu_usage = ((end_cpu_times.user - start_cpu_times.user) / 
                        max(0.01, processing_time)) * 100
            
            # Store metrics
            metrics = PerformanceMetrics(
                processing_time=processing_time,
                memory_usage_mb=end_memory,
                cpu_usage_percent=cpu_usage,
                files_processed=file_count,
                avg_time_per_file=avg_time_per_file,
                peak_memory_mb=max(start_memory, end_memory)
            )
            
            self.metrics_history.append(metrics)
            
            # Check compliance
            self.check_compliance(metrics)
    
    def check_compliance(self, metrics: PerformanceMetrics):
        """Check if processing meets strict performance constraints"""
        violations = []
        
        # Time constraint check (10 seconds for 50-page PDF)
        if metrics.processing_time > self.max_processing_time:
            violations.append(f"Processing time {metrics.processing_time:.2f}s exceeds limit {self.max_processing_time}s")
        
        # Memory constraint check (200MB max)
        if metrics.peak_memory_mb > self.max_memory_mb:
            violations.append(f"Memory usage {metrics.peak_memory_mb:.1f}MB exceeds limit {self.max_memory_mb}MB")
        
        # Performance feedback
        if violations:
            print(f"⚠️  Performance violations detected:")
            for violation in violations:
                print(f"   • {violation}")
        else:
            print(f"✅ Performance compliant: {metrics.processing_time:.2f}s, {metrics.peak_memory_mb:.1f}MB")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        return {
            'latest_processing_time': latest.processing_time,
            'latest_memory_mb': latest.memory_usage_mb,
            'avg_time_per_file': latest.avg_time_per_file,
            'cpu_usage_percent': latest.cpu_usage_percent,
            'files_processed': latest.files_processed,
            'constraint_compliance': {
                'time_compliant': latest.processing_time <= self.max_processing_time,
                'memory_compliant': latest.peak_memory_mb <= self.max_memory_mb
            }
        }

class SizeOptimizer:
    """Optimizes memory usage and file sizes"""
    
    @staticmethod
    def get_memory_usage() -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    @staticmethod
    def optimize_config_for_performance(base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize configuration for strict 10-second compliance"""
        optimized = base_config.copy()
        
        # Aggressive clustering optimization for speed
        if 'extraction' in optimized:
            if 'clustering' in optimized['extraction']:
                optimized['extraction']['clustering'].update({
                    'max_clusters': 3,  # Reduced for speed
                    'n_init': 3,       # Fewer initializations
                    'cluster_ratio': 5  # Faster convergence
                })
            
            # Optimize parallel processing for 8 CPUs
            optimized['extraction']['max_workers'] = 6  # Leave 2 CPUs for system
        
        # Aggressive text limits for faster processing
        if 'extraction' in optimized and 'text_limits' in optimized['extraction']:
            optimized['extraction']['text_limits'].update({
                'max_simple_heading': 80,   # Reduced for speed
                'max_complex_heading': 120, # Reduced for speed
                'max_form_heading': 60      # Reduced for speed
            })
        
        return optimized
