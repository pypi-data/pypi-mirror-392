"""Yordamchi funksiyalar"""

import re
from urllib.parse import urljoin, urlparse
from typing import List, Optional


def clean_text(text: str) -> str:
    """
    Matnni tozalash (ortiqcha bo'sh joylarni olib tashlash)
    
    Args:
        text: Tozalanadigan matn
        
    Returns:
        Tozalangan matn
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_emails(text: str) -> List[str]:
    """
    Matndan email manzillarni ajratib olish
    
    Args:
        text: Matn
        
    Returns:
        Email'lar ro'yxati
    """
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)


def extract_urls(text: str) -> List[str]:
    """
    Matndan URLlarni ajratib olish
    
    Args:
        text: Matn
        
    Returns:
        URLlar ro'yxati
    """
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(pattern, text)


def make_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Nisbiy URLni absolyut URLga aylantirish
    
    Args:
        base_url: Asosiy URL
        relative_url: Nisbiy URL
        
    Returns:
        Absolyut URL
    """
    return urljoin(base_url, relative_url)


def is_valid_url(url: str) -> bool:
    """
    URL to'g'riligini tekshirish
    
    Args:
        url: URL
        
    Returns:
        To'g'ri bo'lsa True
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_domain(url: str) -> Optional[str]:
    """
    URLdan domenni ajratib olish
    
    Args:
        url: URL
        
    Returns:
        Domen nomi
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return None