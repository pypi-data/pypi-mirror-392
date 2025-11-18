"""
AioWebUz - O'zbek tilida mukammal web parsing kutubxonasi
HTTP so'rovlar, parsing, brauzer avtomatizatsiyasi va boshqalarni o'z ichiga oladi
"""

__version__ = "1.0.0"
__author__ = "oscoder"

from .client import WebClient, AsyncWebClient
from .parser import Parser
from .browser import Browser
from .downloader import Downloader
from .automation import Automation

__all__ = [
    'WebClient',
    'AsyncWebClient',
    'Parser',
    'Browser',
    'Downloader',
    'Automation',
]