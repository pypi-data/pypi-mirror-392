"""Fayllarni yuklab olish uchun modul"""

import wget
import os
from typing import Optional
from pathlib import Path


class Downloader:
    """
    Fayllarni yuklab olish uchun klass
    
    Misol:
        dl = Downloader()
        dl.download('https://example.com/file.pdf', 'yuklamalar/')
    """
    
    def __init__(self, output_dir: str = './downloads'):
        """
        Downloader yaratish
        
        Args:
            output_dir: Yuklanmalar papkasi
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def download(self, url: str, output: Optional[str] = None, filename: Optional[str] = None) -> str:
        """
        Faylni yuklab olish
        
        Args:
            url: Fayl manzili
            output: Chiqish papkasi (None bo'lsa standart ishlatiladi)
            filename: Fayl nomi (None bo'lsa avtomatik aniqlanadi)
            
        Returns:
            Yuklangan fayl yo'li
            
        Misol:
            downloader.download('https://example.com/file.pdf')
            downloader.download('https://example.com/image.jpg', filename='rasm.jpg')
        """
        output_path = output or self.output_dir
        
        if filename:
            full_path = os.path.join(output_path, filename)
            result = wget.download(url, out=full_path)
        else:
            result = wget.download(url, out=output_path)
        
        print()  # wget yangi qatorga o'tish uchun
        return result
    
    def download_multiple(self, urls: list, output: Optional[str] = None) -> list:
        """
        Bir nechta fayllarni yuklab olish
        
        Args:
            urls: URLlar ro'yxati
            output: Chiqish papkasi
            
        Returns:
            Yuklangan fayllar yo'llari ro'yxati
        """
        results = []
        for url in urls:
            try:
                result = self.download(url, output=output)
                results.append(result)
            except Exception as e:
                print(f"Xatolik: {url} yuklanmadi - {e}")
                results.append(None)
        return results