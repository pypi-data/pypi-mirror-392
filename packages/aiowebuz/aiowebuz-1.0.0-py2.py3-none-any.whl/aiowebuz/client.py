"""HTTP so'rovlarni bajarish uchun klient"""

import requests
import httpx
from typing import Optional, Dict, Any
from .parser import Parser


class WebClient:
    """
    Sinxron HTTP so'rovlar uchun klient (requests asosida)
    
    Misol:
        client = WebClient()
        response = client.get('https://example.com')
        parser = response.parse()
    """
    
    def __init__(self, headers: Optional[Dict] = None, timeout: int = 30):
        """
        Yangi klient yaratish
        
        Args:
            headers: HTTP sarlavhalar (headers)
            timeout: Kutish vaqti (soniyalarda)
        """
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        self.timeout = timeout
    
    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> 'Response':
        """
        GET so'rov yuborish
        
        Args:
            url: Manzil (URL)
            params: Query parametrlar
            **kwargs: Qo'shimcha parametrlar
            
        Returns:
            Response obyekti
        """
        resp = self.session.get(url, params=params, timeout=self.timeout, **kwargs)
        return Response(resp)
    
    def post(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> 'Response':
        """
        POST so'rov yuborish
        
        Args:
            url: Manzil (URL)
            data: Form ma'lumotlari
            json: JSON ma'lumotlar
            **kwargs: Qo'shimcha parametrlar
            
        Returns:
            Response obyekti
        """
        resp = self.session.post(url, data=data, json=json, timeout=self.timeout, **kwargs)
        return Response(resp)
    
    def put(self, url: str, data: Optional[Dict] = None, **kwargs) -> 'Response':
        """PUT so'rov yuborish"""
        resp = self.session.put(url, data=data, timeout=self.timeout, **kwargs)
        return Response(resp)
    
    def delete(self, url: str, **kwargs) -> 'Response':
        """DELETE so'rov yuborish"""
        resp = self.session.delete(url, timeout=self.timeout, **kwargs)
        return Response(resp)
    
    def set_cookies(self, cookies: Dict):
        """Cookie'larni o'rnatish"""
        self.session.cookies.update(cookies)
    
    def set_headers(self, headers: Dict):
        """Sarlavhalarni o'rnatish"""
        self.session.headers.update(headers)
    
    def close(self):
        """Sessiyani yopish"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class AsyncWebClient:
    """
    Asinxron HTTP so'rovlar uchun klient (httpx asosida)
    
    Misol:
        async with AsyncWebClient() as client:
            response = await client.get('https://example.com')
            parser = response.parse()
    """
    
    def __init__(self, headers: Optional[Dict] = None, timeout: int = 30):
        """
        Yangi async klient yaratish
        
        Args:
            headers: HTTP sarlavhalar
            timeout: Kutish vaqti (soniyalarda)
        """
        self.client = httpx.AsyncClient(headers=headers or {}, timeout=timeout)
    
    async def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> 'Response':
        """
        Async GET so'rov
        
        Args:
            url: Manzil
            params: Query parametrlar
            
        Returns:
            Response obyekti
        """
        resp = await self.client.get(url, params=params, **kwargs)
        return Response(resp, is_async=True)
    
    async def post(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> 'Response':
        """Async POST so'rov"""
        resp = await self.client.post(url, data=data, json=json, **kwargs)
        return Response(resp, is_async=True)
    
    async def put(self, url: str, data: Optional[Dict] = None, **kwargs) -> 'Response':
        """Async PUT so'rov"""
        resp = await self.client.put(url, data=data, **kwargs)
        return Response(resp, is_async=True)
    
    async def delete(self, url: str, **kwargs) -> 'Response':
        """Async DELETE so'rov"""
        resp = await self.client.delete(url, **kwargs)
        return Response(resp, is_async=True)
    
    def set_cookies(self, cookies: Dict):
        """Cookie'larni o'rnatish"""
        self.client.cookies.update(cookies)
    
    def set_headers(self, headers: Dict):
        """Sarlavhalarni o'rnatish"""
        self.client.headers.update(headers)
    
    async def close(self):
        """Klientni yopish"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()


class Response:
    """HTTP javob (response) uchun wrapper klass"""
    
    def __init__(self, response, is_async: bool = False):
        self._response = response
        self.is_async = is_async
    
    @property
    def text(self) -> str:
        """Matn ko'rinishidagi javob"""
        return self._response.text
    
    @property
    def content(self) -> bytes:
        """Bytes ko'rinishidagi javob"""
        return self._response.content
    
    @property
    def status_code(self) -> int:
        """Status kod (200, 404, va h.k.)"""
        return self._response.status_code
    
    @property
    def headers(self) -> Dict:
        """Javob sarlavhalari"""
        return dict(self._response.headers)
    
    @property
    def cookies(self) -> Dict:
        """Cookie'lar"""
        return dict(self._response.cookies)
    
    @property
    def url(self) -> str:
        """So'rov yuborilgan URL"""
        return str(self._response.url)
    
    def json(self) -> Any:
        """JSON ko'rinishida qaytarish"""
        return self._response.json()
    
    def parse(self, parser: str = 'lxml') -> Parser:
        """
        HTML ni parsing qilish uchun Parser obyektini qaytaradi
        
        Args:
            parser: Parser turi ('lxml', 'html.parser', 'html5lib')
            
        Returns:
            Parser obyekti
        """
        return Parser(self.text, parser=parser)
    
    def is_success(self) -> bool:
        """So'rov muvaffaqiyatli bo'lganmi?"""
        return 200 <= self.status_code < 300