from aiogram.types import FSInputFile, BufferedInputFile, URLInputFile
from typing import Union
import aiohttp

class Media:
    """Media fayllar bilan ishlash uchun yordamchi klass"""
    
    @staticmethod
    def fayldan(yo_l: str):
        """
        Fayldan media yaratish
        
        Args:
            yo_l: Fayl yo'li
            
        Returns:
            FSInputFile obyekti
        """
        return FSInputFile(yo_l)
    
    @staticmethod
    def bytesdan(data: bytes, fayl_nomi: str = "file"):
        """
        Bytes dan media yaratish
        
        Args:
            data: Bytes ma'lumot
            fayl_nomi: Fayl nomi
            
        Returns:
            BufferedInputFile obyekti
        """
        return BufferedInputFile(data, filename=fayl_nomi)
    
    @staticmethod
    def urldan(url: str):
        """
        URL dan media yaratish
        
        Args:
            url: Media URL manzili
            
        Returns:
            URLInputFile obyekti
        """
        return URLInputFile(url)
    
    @staticmethod
    async def yuklab_olish(url: str) -> bytes:
        """
        URL dan fayl yuklab olish
        
        Args:
            url: Fayl URL manzili
            
        Returns:
            Yuklangan fayl bytes formatida
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()