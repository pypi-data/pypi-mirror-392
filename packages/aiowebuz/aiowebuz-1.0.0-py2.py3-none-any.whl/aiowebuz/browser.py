"""Brauzer avtomatizatsiyasi uchun modul"""

from seleniumbase import Driver, SB
from typing import Optional, List
import time


class Browser:
    """
    Brauzer bilan ishlash uchun klass (SeleniumBase asosida)
    
    Misol:
        browser = Browser()
        browser.open('https://example.com')
        browser.click('.button')
        text = browser.get_text('h1')
        browser.close()
    """
    
    def __init__(self, headless: bool = False, browser_type: str = 'chrome'):
        """
        Brauzer yaratish
        
        Args:
            headless: Ko'rinmas rejim (True/False)
            browser_type: Brauzer turi ('chrome', 'firefox', 'edge')
        """
        self.driver = Driver(
            browser=browser_type,
            headless=headless,
            uc=True  # Undetected mode
        )
    
    def open(self, url: str):
        """
        Sahifani ochish
        
        Args:
            url: Manzil
        """
        self.driver.get(url)
    
    def click(self, selector: str, timeout: int = 10):
        """
        Elementga bosish
        
        Args:
            selector: CSS selector
            timeout: Kutish vaqti
        """
        self.driver.click(selector, timeout=timeout)
    
    def type(self, selector: str, text: str, timeout: int = 10):
        """
        Matn kiritish
        
        Args:
            selector: CSS selector
            text: Kiritish uchun matn
            timeout: Kutish vaqti
        """
        self.driver.type(selector, text, timeout=timeout)
    
    def get_text(self, selector: str, timeout: int = 10) -> str:
        """
        Element matnini olish
        
        Args:
            selector: CSS selector
            timeout: Kutish vaqti
            
        Returns:
            Matn
        """
        return self.driver.get_text(selector, timeout=timeout)
    
    def get_attribute(self, selector: str, attribute: str, timeout: int = 10) -> str:
        """
        Attribute qiymatini olish
        
        Args:
            selector: CSS selector
            attribute: Attribute nomi
            timeout: Kutish vaqti
            
        Returns:
            Attribute qiymati
        """
        return self.driver.get_attribute(selector, attribute, timeout=timeout)
    
    def find_element(self, selector: str, timeout: int = 10):
        """
        Elementni topish
        
        Args:
            selector: CSS selector
            timeout: Kutish vaqti
            
        Returns:
            Element obyekti
        """
        return self.driver.find_element(selector, timeout=timeout)
    
    def find_elements(self, selector: str) -> List:
        """
        Barcha elementlarni topish
        
        Args:
            selector: CSS selector
            
        Returns:
            Elementlar ro'yxati
        """
        return self.driver.find_elements(selector)
    
    def wait(self, seconds: float):
        """
        Kutish
        
        Args:
            seconds: Soniyalar
        """
        time.sleep(seconds)
    
    def wait_for_element(self, selector: str, timeout: int = 10):
        """
        Element paydo bo'lishini kutish
        
        Args:
            selector: CSS selector
            timeout: Kutish vaqti
        """
        self.driver.wait_for_element(selector, timeout=timeout)
    
    def screenshot(self, filename: str):
        """
        Skrinshot olish
        
        Args:
            filename: Fayl nomi
        """
        self.driver.save_screenshot(filename)
    
    def execute_script(self, script: str, *args):
        """
        JavaScript kodini bajarish
        
        Args:
            script: JavaScript kodi
            *args: Argumentlar
            
        Returns:
            Natija
        """
        return self.driver.execute_script(script, *args)
    
    def scroll_to(self, selector: str):
        """
        Elementgacha scroll qilish
        
        Args:
            selector: CSS selector
        """
        self.driver.scroll_to(selector)
    
    def scroll_to_bottom(self):
        """Sahifa oxirigacha scroll qilish"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def get_page_source(self) -> str:
        """
        Sahifa HTML kodini olish
        
        Returns:
            HTML kod
        """
        return self.driver.page_source
    
    def get_current_url(self) -> str:
        """
        Joriy URLni olish
        
        Returns:
            URL
        """
        return self.driver.current_url
    
    def back(self):
        """Orqaga qaytish"""
        self.driver.back()
    
    def forward(self):
        """Oldinga o'tish"""
        self.driver.forward()
    
    def refresh(self):
        """Sahifani yangilash"""
        self.driver.refresh()
    
    def close(self):
        """Brauzerni yopish"""
        self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()