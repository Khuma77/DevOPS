import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Setup structured logging for Loki"""
    
    # Create custom formatter for JSON logs
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with JSON format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler for application logs
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Setup specific loggers
    loggers = ['api', 'admin', 'cart', 'orders', 'products']
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.propagate = True  # Allow propagation to root logger
    
    # Flask logger
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.WARNING)  # Reduce Flask noise
    
    return root_logger

def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)