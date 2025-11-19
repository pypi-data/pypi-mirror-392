from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from typing import List, Optional

class Tugma:
    """
    Oddiy tugmalar (ReplyKeyboard) yaratish uchun klass
    
    Misol:
        tugma = Tugma()
        tugma.qator(["✅ Ha", "❌ Yo'q"])
        tugma.qator(["🔙 Orqaga"])
    """
    
    def __init__(self, bir_martalik: bool = False, o_lcham_moslashtirish: bool = True):
        """
        Args:
            bir_martalik: Tugma bosilganda klaviatura yashirilsinmi
            o_lcham_moslashtirish: Tugmalar o'lchamini moslashtirish
        """
        self.tugmalar: List[List[KeyboardButton]] = []
        self.bir_martalik = bir_martalik
        self.o_lcham = o_lcham_moslashtirish
    
    def qator(self, tugmalar: List[str]) -> 'Tugma':
        """
        Yangi qator qo'shish
        
        Args:
            tugmalar: Tugmalar matni ro'yxati
            
        Returns:
            O'z obyekti (zanjir usulida ishlatish uchun)
        """
        qator = [KeyboardButton(text=text) for text in tugmalar]
        self.tugmalar.append(qator)
        return self
    
    def kontakt(self, matn: str) -> 'Tugma':
        """Kontakt so'rash tugmasini qo'shish"""
        self.tugmalar.append([KeyboardButton(text=matn, request_contact=True)])
        return self
    
    def joylashuv(self, matn: str) -> 'Tugma':
        """Joylashuv so'rash tugmasini qo'shish"""
        self.tugmalar.append([KeyboardButton(text=matn, request_location=True)])
        return self
    
    def yasash(self) -> ReplyKeyboardMarkup:
        """Tugmalarni yaratish"""
        return ReplyKeyboardMarkup(
            keyboard=self.tugmalar,
            resize_keyboard=self.o_lcham,
            one_time_keyboard=self.bir_martalik
        )


class InlineTugma:
    """
    Inline tugmalar yaratish uchun klass
    
    Misol:
        tugma = InlineTugma()
        tugma.qator([("✅ Tasdiq", "tasdiq"), ("❌ Bekor", "bekor")])
        tugma.url("Google", "https://google.com")
    """
    
    def __init__(self):
        self.tugmalar: List[List[InlineKeyboardButton]] = []
    
    def qator(self, tugmalar: List[tuple]) -> 'InlineTugma':
        """
        Yangi qator qo'shish
        
        Args:
            tugmalar: [(matn, callback_data), ...] formatidagi ro'yxat
            
        Returns:
            O'z obyekti
        """
        qator = [
            InlineKeyboardButton(text=text, callback_data=data)
            for text, data in tugmalar
        ]
        self.tugmalar.append(qator)
        return self
    
    def url(self, matn: str, havola: str) -> 'InlineTugma':
        """URL tugmasi qo'shish"""
        self.tugmalar.append([
            InlineKeyboardButton(text=matn, url=havola)
        ])
        return self
    
    def yasash(self) -> InlineKeyboardMarkup:
        """Tugmalarni yaratish"""
        return InlineKeyboardMarkup(inline_keyboard=self.tugmalar)