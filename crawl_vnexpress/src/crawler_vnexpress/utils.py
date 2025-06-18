import requests
from bs4 import BeautifulSoup
from functools import wraps
from typing import Callable
import time


def retry(times: int, sleep_time: float = 0.5):
    """
    Retry decorator to re-run a function multiple times on failure.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(url: str, *args, **kwargs):
            attempt = 0
            while attempt <= times:
                try:
                    return func(url, *args, **kwargs)
                except Exception as e:
                    print(f"[RETRY] Failed to load: {url} (Attempt {attempt + 1}/{times + 1}) - {e}")
                    time.sleep(sleep_time)
                attempt += 1
            print(f"[ERROR] Gave up loading: {url}")
            return None
        return wrapper
    return decorator


def get_soup(func: Callable):
    """
    Convert raw HTML from a URL to BeautifulSoup object.
    """
    @wraps(func)
    def wrapper(url: str, *args, **kwargs):
        try:
            content = func(url, *args, **kwargs)
            if content is None:
                print(f"[ERROR] Cannot fetch: {url}")
                return BeautifulSoup("", "lxml")
            return BeautifulSoup(content, "lxml")
        except Exception as e:
            print(f"[EXCEPTION] URL: {url} - {str(e)}")
            return BeautifulSoup("", "lxml")
    return wrapper
