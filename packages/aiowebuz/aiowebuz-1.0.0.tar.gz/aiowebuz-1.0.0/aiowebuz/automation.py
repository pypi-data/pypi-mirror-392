"""GUI avtomatizatsiya uchun modul"""

import pyautogui
from typing import Optional, Tuple
import time


class Automation:
    """
    GUI avtomatizatsiya uchun klass (PyAutoGUI asosida)
    
    Misol:
        auto = Automation()
        auto.click(100, 200)
        auto.type_text('Salom dunyo!')
        pos = auto.find_image('tugma.png')
    """
    
    def __init__(self):
        """Automation obyektini yaratish"""
        pyautogui.PAUSE = 0.5  # Har bir harakat orasida pauza
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1, button: str = 'left'):
        """
        Sichqoncha bilan bosish
        
        Args:
            x: X koordinata (None bo'lsa joriy pozitsiya)
            y: Y koordinata
            clicks: Necha marta bosish
            button: Tugma ('left', 'right', 'middle')
        """
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
        else:
            pyautogui.click(clicks=clicks, button=button)
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """
        Ikki marta bosish
        
        Args:
            x: X koordinata
            y: Y koordinata
        """
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.doubleClick()
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """
        O'ng tugma bilan bosish
        
        Args:
            x: X koordinata
            y: Y koordinata
        """
        self.click(x, y, button='right')
    
    def move_to(self, x: int, y: int, duration: float = 0.5):
        """
        Sichqonchani harakatlantirish
        
        Args:
            x: X koordinata
            y: Y koordinata
            duration: Harakat davomiyligi (soniyalarda)
        """
        pyautogui.moveTo(x, y, duration=duration)
    
    def drag_to(self, x: int, y: int, duration: float = 0.5, button: str = 'left'):
        """
        Sichqonchani sudrab borish
        
        Args:
            x: X koordinata
            y: Y koordinata
            duration: Davomiylik
            button: Tugma
        """
        pyautogui.dragTo(x, y, duration=duration, button=button)
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None):
        """
        Scroll qilish
        
        Args:
            clicks: Scroll miqdori (musbat - yuqoriga, manfiy - pastga)
            x: X koordinata
            y: Y koordinata
        """
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x=x, y=y)
        else:
            pyautogui.scroll(clicks)
    
    def type_text(self, text: str, interval: float = 0.05):
        """
        Matn yozish
        
        Args:
            text: Yoziladigan matn
            interval: Harflar orasidagi interval
        """
        pyautogui.write(text, interval=interval)
    
    def press(self, key: str, presses: int = 1):
        """
        Klaviatura tugmasini bosish
        
        Args:
            key: Tugma nomi ('enter', 'space', 'esc', va h.k.)
            presses: Necha marta bosish
        """
        pyautogui.press(key, presses=presses)
    
    def hotkey(self, *keys):
        """
        Klaviatura kombinatsiyasini bosish
        
        Args:
            *keys: Tugmalar ('ctrl', 'c' va h.k.)
            
        Misol:
            auto.hotkey('ctrl', 'c')  # Nusxa olish
            auto.hotkey('ctrl', 'v')  # Qo'yish
        """
        pyautogui.hotkey(*keys)
    
    def screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Ekran rasmini olish
        
        Args:
            filename: Fayl nomi (None bo'lsa PIL Image qaytaradi)
            
        Returns:
            Fayl yo'li yoki Image obyekti
        """
        if filename:
            pyautogui.screenshot(filename)
            return filename
        else:
            return pyautogui.screenshot()
    
    def find_image(self, image_path: str, confidence: float = 0.9) -> Optional[Tuple[int, int, int, int]]:
        """
        Ekrandan rasm topish
        
        Args:
            image_path: Rasm fayl yo'li
            confidence: Ishonch darajasi (0-1)
            
        Returns:
            (x, y, width, height) yoki None
        """
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            return location
        except:
            return None
    
    def click_image(self, image_path: str, confidence: float = 0.9) -> bool:
        """
        Ekrandan topilgan rasmga bosish
        
        Args:
            image_path: Rasm fayl yo'li
            confidence: Ishonch darajasi
            
        Returns:
            Topilgan va bosilgan bo'lsa True
        """
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                return True
            return False
        except:
            return False
    
    def get_position(self) -> Tuple[int, int]:
        """
        Sichqoncha pozitsiyasini olish
        
        Returns:
            (x, y) koordinatalar
        """
        return pyautogui.position()
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Ekran o'lchamini olish
        
        Returns:
            (width, height)
        """
        return pyautogui.size()
    
    def wait(self, seconds: float):
        """
        Kutish
        
        Args:
            seconds: Soniyalar
        """
        time.sleep(seconds)