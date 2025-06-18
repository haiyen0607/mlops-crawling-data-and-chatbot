#Chứa các hàm tiện ích dùng chung như xử lý thời gian, làm sạch dữ liệu, log, v.v.

import requests
from bs4 import BeautifulSoup
from functools import wraps
from typing import Callable
import time


def retry(times: int, sleep_time: float = 0.5):
    def decorator(func: Callable):
        @wraps(func)
        def warpper(url: str, *args, **kwargs):
            attempt = 0
            while attempt <= times:
                try:
                    return func(url, *args, **kwargs)
                except Exception:
                    time.sleep(sleep_time)
                attempt += 1
            return None
        return warpper
    return decorator


def get_soup(func: Callable):
    @wraps(func)
    def wrapper(url: str, *args, **kwargs):
        try:
            content = func(url, *args, **kwargs)
            if content is None:
                return BeautifulSoup("", "lxml")
            return BeautifulSoup(content, "lxml")
        except Exception:
            return BeautifulSoup("", "lxml")
    return wrapper
