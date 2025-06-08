"""Utility functions for Rick and Morty API client."""
import logging
import time
from functools import wraps
from typing import Callable, Any, Optional, TypeVar, Union
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from .config import Config

# Type variable for generic return type
T = TypeVar('T')

def setup_logging(name: str, level: str = Config.LOG_LEVEL) -> logging.Logger:
    """Set up logging for a module."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(Config.LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def retry_with_backoff(
    max_retries: int = Config.MAX_RETRIES,
    delay: float = Config.RETRY_DELAY,
    backoff: float = Config.RETRY_BACKOFF,
    exceptions: tuple = (RequestException, Timeout, ConnectionError)
) -> Callable:
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = logging.getLogger(func.__module__)
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {wait_time:.1f} seconds..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed: {str(e)}")
            
            raise last_exception
        return wrapper
    return decorator

def extract_id_from_url(url: str, resource_type: str = "location") -> Optional[int]:
    """Extract ID from Rick and Morty API URL."""
    if not url:
        return None
    
    try:
        if f"/{resource_type}/" in url:
            return int(url.split(f"/{resource_type}/")[-1])
    except (ValueError, IndexError):
        pass
    
    return None

def validate_response(response: requests.Response) -> bool:
    """Validate API response."""
    if response.status_code != 200:
        return False
    
    try:
        data = response.json()
        return isinstance(data, dict)
    except ValueError:
        return False

def chunks(lst: list, n: int) -> list:
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class ProgressTracker:
    """Track and display progress for long-running operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.logger = logging.getLogger(__name__)
    
    def update(self, amount: int = 1):
        """Update progress."""
        self.current += amount
        if Config.ENABLE_PROGRESS:
            percentage = (self.current / self.total) * 100
            elapsed = time.time() - self.start_time
            rate = self.current / elapsed if elapsed > 0 else 0
            
            self.logger.info(
                f"{self.description}: {self.current}/{self.total} "
                f"({percentage:.1f}%) - {rate:.1f} items/sec"
            )
    
    def finish(self):
        """Mark progress as complete."""
        elapsed = time.time() - self.start_time
        self.logger.info(
            f"{self.description} completed: {self.total} items in {elapsed:.1f}s"
        )

class APIError(Exception):
    """Custom exception for API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

def handle_api_error(response: requests.Response) -> None:
    """Handle API error responses."""
    if response.status_code == 404:
        raise APIError("Resource not found", status_code=404)
    elif response.status_code == 429:
        raise APIError("Rate limit exceeded", status_code=429)
    elif response.status_code >= 500:
        raise APIError("Server error", status_code=response.status_code)
    elif response.status_code >= 400:
        raise APIError(
            f"Client error: {response.text}", 
            status_code=response.status_code
        )