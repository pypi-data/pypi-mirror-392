"""HTML parsing uchun kuchli parser"""

from bs4 import BeautifulSoup
from lxml import html as lxml_html
from typing import List, Optional, Dict, Any


class Parser:
    """
    HTML parsing uchun mukammal parser
    
    Misol:
        parser = Parser(html_text)
        element = parser.find('.class-name')
        elements = parser.find_all('div')
        text = parser.css('h1').text()
    """
    
    def __init__(self, html: str, parser: str = 'lxml'):
        """
        Parser yaratish
        
        Args:
            html: HTML matn
            parser: Parser turi ('lxml', 'html.parser', 'html5lib')
        """
        self.html = html
        self.soup = BeautifulSoup(html, parser)
        self.lxml_tree = lxml_html.fromstring(html)
    
    def find(self, selector: str, **kwargs) -> Optional['Element']:
        """
        Bitta elementni topish (CSS selector yoki teg nomi)
        
        Args:
            selector: CSS selector ('.class', '#id', 'tag')
            **kwargs: Qo'shimcha filtrlar
            
        Returns:
            Element obyekti yoki None
            
        Misol:
            parser.find('.title')
            parser.find('#main-content')
            parser.find('a', href=True)
        """
        if selector.startswith('.'):
            # Class bo'yicha
            elem = self.soup.find(class_=selector[1:], **kwargs)
        elif selector.startswith('#'):
            # ID bo'yicha
            elem = self.soup.find(id=selector[1:], **kwargs)
        else:
            # Teg nomi bo'yicha
            elem = self.soup.find(selector, **kwargs)
        
        return Element(elem, self) if elem else None
    
    def find_all(self, selector: str, limit: Optional[int] = None, **kwargs) -> List['Element']:
        """
        Bir nechta elementlarni topish
        
        Args:
            selector: CSS selector yoki teg nomi
            limit: Maksimal soni
            **kwargs: Qo'shimcha filtrlar
            
        Returns:
            Element obyektlari ro'yxati
        """
        if selector.startswith('.'):
            elems = self.soup.find_all(class_=selector[1:], limit=limit, **kwargs)
        elif selector.startswith('#'):
            elems = self.soup.find_all(id=selector[1:], limit=limit, **kwargs)
        else:
            elems = self.soup.find_all(selector, limit=limit, **kwargs)
        
        return [Element(elem, self) for elem in elems]
    
    def css(self, selector: str) -> Optional['Element']:
        """
        CSS selector bo'yicha bitta element topish
        
        Args:
            selector: CSS selector
            
        Returns:
            Element obyekti
            
        Misol:
            parser.css('div.content > p')
            parser.css('a[href*="example"]')
        """
        elem = self.soup.select_one(selector)
        return Element(elem, self) if elem else None
    
    def css_all(self, selector: str) -> List['Element']:
        """
        CSS selector bo'yicha barcha elementlarni topish
        
        Args:
            selector: CSS selector
            
        Returns:
            Element obyektlari ro'yxati
        """
        elems = self.soup.select(selector)
        return [Element(elem, self) for elem in elems]
    
    def xpath(self, xpath_expr: str) -> List['Element']:
        """
        XPath bo'yicha elementlarni topish
        
        Args:
            xpath_expr: XPath ifoda
            
        Returns:
            Element obyektlari ro'yxati
            
        Misol:
            parser.xpath('//div[@class="content"]//p')
            parser.xpath('//a[contains(@href, "example")]')
        """
        elems = self.lxml_tree.xpath(xpath_expr)
        result = []
        for elem in elems:
            if hasattr(elem, 'tag'):
                # Element obyekti
                html_str = lxml_html.tostring(elem, encoding='unicode')
                soup_elem = BeautifulSoup(html_str, 'lxml').find()
                result.append(Element(soup_elem, self))
            else:
                # Matn yoki attribute
                result.append(elem)
        return result
    
    def get_text(self, separator: str = ' ', strip: bool = True) -> str:
        """
        Barcha matnni olish
        
        Args:
            separator: Matnlarni ajratuvchi
            strip: Bo'sh joylarni tozalash
            
        Returns:
            Matn
        """
        return self.soup.get_text(separator=separator, strip=strip)


class Element:
    """HTML elementi uchun wrapper klass"""
    
    def __init__(self, element, parser: Parser):
        self._element = element
        self._parser = parser
    
    def text(self, strip: bool = True) -> str:
        """
        Element matni
        
        Args:
            strip: Bo'sh joylarni tozalash
            
        Returns:
            Matn
        """
        if not self._element:
            return ""
        text = self._element.get_text()
        return text.strip() if strip else text
    
    def attr(self, name: str, default: Any = None) -> Any:
        """
        Attribute (xususiyat) qiymatini olish
        
        Args:
            name: Attribute nomi
            default: Standart qiymat (agar topilmasa)
            
        Returns:
            Attribute qiymati
            
        Misol:
            element.attr('href')
            element.attr('class')
            element.attr('data-id')
        """
        if not self._element:
            return default
        return self._element.get(name, default)
    
    def attrs(self) -> Dict[str, Any]:
        """Barcha attributlarni olish"""
        if not self._element:
            return {}
        return dict(self._element.attrs)
    
    def find(self, selector: str, **kwargs) -> Optional['Element']:
        """Ichidan bitta elementni topish"""
        if not self._element:
            return None
        
        if selector.startswith('.'):
            elem = self._element.find(class_=selector[1:], **kwargs)
        elif selector.startswith('#'):
            elem = self._element.find(id=selector[1:], **kwargs)
        else:
            elem = self._element.find(selector, **kwargs)
        
        return Element(elem, self._parser) if elem else None
    
    def find_all(self, selector: str, **kwargs) -> List['Element']:
        """Ichidan barcha elementlarni topish"""
        if not self._element:
            return []
        
        if selector.startswith('.'):
            elems = self._element.find_all(class_=selector[1:], **kwargs)
        elif selector.startswith('#'):
            elems = self._element.find_all(id=selector[1:], **kwargs)
        else:
            elems = self._element.find_all(selector, **kwargs)
        
        return [Element(elem, self._parser) for elem in elems]
    
    def css(self, selector: str) -> Optional['Element']:
        """CSS selector bo'yicha ichidan topish"""
        if not self._element:
            return None
        elem = self._element.select_one(selector)
        return Element(elem, self._parser) if elem else None
    
    def css_all(self, selector: str) -> List['Element']:
        """CSS selector bo'yicha barcha ichki elementlarni topish"""
        if not self._element:
            return []
        elems = self._element.select(selector)
        return [Element(elem, self._parser) for elem in elems]
    
    def parent(self) -> Optional['Element']:
        """Ota elementni olish"""
        if not self._element or not self._element.parent:
            return None
        return Element(self._element.parent, self._parser)
    
    def next_sibling(self) -> Optional['Element']:
        """Keyingi qo'shni elementni olish"""
        if not self._element:
            return None
        sibling = self._element.find_next_sibling()
        return Element(sibling, self._parser) if sibling else None
    
    def prev_sibling(self) -> Optional['Element']:
        """Oldingi qo'shni elementni olish"""
        if not self._element:
            return None
        sibling = self._element.find_previous_sibling()
        return Element(sibling, self._parser) if sibling else None
    
    @property
    def tag(self) -> str:
        """Element teg nomi"""
        return self._element.name if self._element else ""
    
    @property
    def html(self) -> str:
        """Element HTML kodi"""
        return str(self._element) if self._element else ""
    
    def exists(self) -> bool:
        """Element mavjudmi?"""
        return self._element is not None