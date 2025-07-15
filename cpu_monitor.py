import psutil
import time
import threading
import queue
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CPUMetrics:
    timestamp: datetime
    cpu_percent: float
    cpu_freq: float
    memory_percent: float
    memory_used: float
    memory_total: float
    temperature: Optional[float] = None


class CPUMonitor:
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.is_monitoring = False
        self.metrics_queue = queue.Queue()
        self.metrics_history: List[CPUMetrics] = []
        self.max_history_size = 1000
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start monitoring CPU metrics in a separate thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring CPU metrics"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_queue.put(metrics)
                
                # Add to history and maintain size limit
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.interval)
    
    def _collect_metrics(self) -> CPUMetrics:
        """Collect current CPU and memory metrics"""
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # Get CPU frequency
        cpu_freq = psutil.cpu_freq()
        current_freq = cpu_freq.current if cpu_freq else 0
        
        # Get memory usage
        memory = psutil.virtual_memory()
        
        # Try to get temperature (may not be available on all systems)
        temperature = self._get_temperature()
        
        return CPUMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            cpu_freq=current_freq,
            memory_percent=memory.percent,
            memory_used=memory.used / (1024**3),  # Convert to GB
            memory_total=memory.total / (1024**3),  # Convert to GB
            temperature=temperature
        )
    
    def _get_temperature(self) -> Optional[float]:
        """Try to get CPU temperature (may not work on all systems)"""
        try:
            # Try to get temperature sensors
            temps = psutil.sensors_temperatures()
            if temps:
                # Look for CPU temperature
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        if entries:
                            return entries[0].current
                # If no CPU-specific sensor, return first available
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
            return None
        except:
            return None
    
    def get_current_metrics(self) -> CPUMetrics:
        """Get current CPU metrics"""
        return self._collect_metrics()
    
    def get_latest_metrics(self, count: int = 10) -> List[CPUMetrics]:
        """Get latest metrics from history"""
        return self.metrics_history[-count:] if self.metrics_history else []
    
    def get_average_metrics(self, duration_seconds: int = 60) -> Dict:
        """Get average metrics over the specified duration"""
        if not self.metrics_history:
            return {}
        
        # Filter metrics within the specified duration
        cutoff_time = datetime.now().timestamp() - duration_seconds
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp.timestamp() > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_freq = sum(m.cpu_freq for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        
        # Calculate temperature average if available
        temp_readings = [m.temperature for m in recent_metrics if m.temperature is not None]
        avg_temp = sum(temp_readings) / len(temp_readings) if temp_readings else None
        
        return {
            'duration_seconds': duration_seconds,
            'sample_count': len(recent_metrics),
            'avg_cpu_percent': round(avg_cpu, 2),
            'avg_cpu_freq': round(avg_freq, 2),
            'avg_memory_percent': round(avg_memory, 2),
            'avg_temperature': round(avg_temp, 2) if avg_temp else None,
            'max_cpu_percent': max(m.cpu_percent for m in recent_metrics),
            'max_memory_percent': max(m.memory_percent for m in recent_metrics)
        }
    
    def get_system_info(self) -> Dict:
        """Get detailed system information"""
        # CPU info
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'cpu_percent_per_core': psutil.cpu_percent(percpu=True, interval=1)
        }
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'percent': memory.percent
        }
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_info = {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': round((disk.used / disk.total) * 100, 2)
        }
        
        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        return {
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime_hours': round((datetime.now() - boot_time).total_seconds() / 3600, 2)
        }
    
    def clear_history(self):
        """Clear metrics history"""
        self.metrics_history.clear()
    
    def export_metrics(self, filename: str = None) -> str:
        """Export metrics history to JSON file"""
        import json
        
        if not filename:
            filename = f"cpu_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'export_time': datetime.now().isoformat(),
            'total_samples': len(self.metrics_history),
            'metrics': [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'cpu_percent': m.cpu_percent,
                    'cpu_freq': m.cpu_freq,
                    'memory_percent': m.memory_percent,
                    'memory_used_gb': m.memory_used,
                    'memory_total_gb': m.memory_total,
                    'temperature': m.temperature
                }
                for m in self.metrics_history
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename


class StressTestMonitor:
    def __init__(self):
        self.cpu_monitor = CPUMonitor(interval=0.5)
        self.stress_test_active = False
        self.test_start_time = None
        self.test_results = {}
    
    def start_stress_test_monitoring(self, test_name: str):
        """Start monitoring for a stress test"""
        self.stress_test_active = True
        self.test_start_time = datetime.now()
        self.cpu_monitor.clear_history()
        self.cpu_monitor.start_monitoring()
        print(f"Started monitoring for stress test: {test_name}")
    
    def stop_stress_test_monitoring(self) -> Dict:
        """Stop monitoring and return test results"""
        self.stress_test_active = False
        self.cpu_monitor.stop_monitoring()
        
        if self.test_start_time:
            test_duration = (datetime.now() - self.test_start_time).total_seconds()
            
            # Get metrics for the entire test duration
            metrics = self.cpu_monitor.get_average_metrics(int(test_duration))
            metrics['test_duration_seconds'] = test_duration
            metrics['test_start_time'] = self.test_start_time.isoformat()
            metrics['test_end_time'] = datetime.now().isoformat()
            
            # Get peak values
            if self.cpu_monitor.metrics_history:
                metrics['peak_cpu_percent'] = max(m.cpu_percent for m in self.cpu_monitor.metrics_history)
                metrics['peak_memory_percent'] = max(m.memory_percent for m in self.cpu_monitor.metrics_history)
                metrics['peak_temperature'] = max(
                    (m.temperature for m in self.cpu_monitor.metrics_history if m.temperature is not None),
                    default=None
                )
            
            return metrics
        
        return {}
    
    def get_realtime_metrics(self) -> Dict:
        """Get real-time metrics during stress test"""
        if self.stress_test_active:
            current = self.cpu_monitor.get_current_metrics()
            return {
                'current_cpu_percent': current.cpu_percent,
                'current_memory_percent': current.memory_percent,
                'current_temperature': current.temperature,
                'test_duration': (datetime.now() - self.test_start_time).total_seconds() if self.test_start_time else 0
            }
        return {}