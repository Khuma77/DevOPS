from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge, Info
from flask import Blueprint, Response
import psutil
import time

metrics_bp = Blueprint('metrics', __name__)

# System metrics
system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
system_memory_usage = Gauge('system_memory_usage_percent', 'System memory usage percentage')
system_disk_usage = Gauge('system_disk_usage_percent', 'System disk usage percentage')

# Application info
app_info = Info('app_info', 'Application information')
app_info.info({
    'version': '1.0.0',
    'name': 'agro_shop',
    'environment': 'development'
})

def update_system_metrics():
    """Update system metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage.set(memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        system_disk_usage.set(disk_percent)
        
    except Exception as e:
        print(f"Error updating system metrics: {e}")

@metrics_bp.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    # Update system metrics before serving
    update_system_metrics()
    
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@metrics_bp.route('/health')
def health_check():
    """Enhanced health check with system info"""
    try:
        # Basic system info
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "system": {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": (disk.used / disk.total) * 100,
                "uptime": time.time() - psutil.boot_time()
            }
        }, 200
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }, 500