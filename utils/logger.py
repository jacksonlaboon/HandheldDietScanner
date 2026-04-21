"""
Logging utility for HandheldDietScanner
"""
import logging
import sys
from config import LOG_FILE, LOG_LEVEL


def setup_logger(log_file: str = LOG_FILE, level: str = LOG_LEVEL) -> logging.Logger:
    """Setup and return the application logger
    
    Args:
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("HandheldDietScanner")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler for detailed logs
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except IOError as e:
        print(f"Warning: Could not create log file {log_file}: {e}")
    
    # Console handler for important messages
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """Get the application logger instance
    
    Returns:
        Logger instance (will setup if not already done)
    """
    logger = logging.getLogger("HandheldDietScanner")
    if not logger.handlers:
        return setup_logger()
    return logger