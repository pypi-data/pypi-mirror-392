from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from typing import Callable, Optional, Union, List
import asyncio
import logging

class OsonBot:
    """
    Telegram bot yaratish uchun juda oson klass.
    
    Misol:
        bot = OsonBot("TOKEN")
        
        @bot.xabar("/start")
        def start(xabar):
            bot.yuborish(xabar, "Salom!")
    """
    
    def __init__(self, token: str, log_darajasi: str = "INFO"):
        """
        Bot yaratish
        
        Args:
            token: Bot tokeni (@BotFather dan olinadi)
            log_darajasi: Log darajasi (DEBUG, INFO, WARNING, ERROR)
        """
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self._sozlamalar()
        
        # Logging sozlash
        logging.basicConfig(
            level=getattr(logging, log_darajasi.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _sozlamalar(self):
        """Standart sozlamalarni o'rnatish"""
        self._xabar_handlerlari = []
        self._callback_handlerlari = []
    
    def xabar(self, 
              komanda: Optional[Union[str, List[str]]] = None,
              matn: Optional[str] = None,
              holat: Optional[str] = None):
        """
        Xabar uchun handler qo'shish (dekorator)
        
        Args:
            komanda: Komanda yoki komandalar ro'yxati (/start, /help)
            matn: Aniq matn
            holat: Holat nomi
            
        Misol:
            @bot.xabar("/start")
            def start_handler(xabar):
                bot.yuborish(xabar, "Salom!")
        """
        def decorator(func: Callable):
            filters = []
            
            if komanda:
                if isinstance(komanda, list):
                    for cmd in komanda:
                        cmd = cmd.replace("/", "")
                        filters.append(Command(cmd))
                else:
                    cmd = komanda.replace("/", "")
                    self.dp.message.register(func, Command(cmd))
                    return func
            
            if matn:
                filters.append(F.text == matn)
            
            if holat:
                filters.append(StateFilter(holat))
            
            if not filters:
                self.dp.message.register(func)
            else:
                self.dp.message.register(func, *filters)
            
            return func
        return decorator
    
    def callback(self, data: Optional[str] = None):
        """
        Inline tugma bosilishi uchun handler (dekorator)
        
        Args:
            data: Callback data (masalan: "tasdiq", "bekor")
            
        Misol:
            @bot.callback("tasdiq")
            def tasdiq_handler(callback):
                bot.javob_berish(callback, "Tasdiqlandi!")
        """
        def decorator(func: Callable):
            if data:
                self.dp.callback_query.register(func, F.data == data)
            else:
                self.dp.callback_query.register(func)
            return func
        return decorator
    
    def har_qanday_xabar(self):
        """
        Har qanday xabar uchun handler (dekorator)
        
        Misol:
            @bot.har_qanday_xabar()
            def barcha_xabarlar(xabar):
                print(f"Xabar keldi: {xabar.text}")
        """
        def decorator(func: Callable):
            self.dp.message.register(func)
            return func
        return decorator
    
    async def yuborish(self, 
                       xabar: Message, 
                       matn: str,
                       tugmalar: Optional[Union['Tugma', 'InlineTugma']] = None,
                       parse_mode: str = "HTML"):
        """
        Xabar yuborish
        
        Args:
            xabar: Kelgan xabar obyekti
            matn: Yuboriladigan matn
            tugmalar: Tugmalar (Tugma yoki InlineTugma obyekti)
            parse_mode: Matn formati (HTML, Markdown)
            
        Returns:
            Yuborilgan xabar obyekti
        """
        keyboard = None
        if tugmalar:
            keyboard = tugmalar.yasash()
        
        return await xabar.answer(
            matn,
            reply_markup=keyboard,
            parse_mode=parse_mode
        )
    
    async def tahrirlash(self,
                        callback: CallbackQuery,
                        matn: str,
                        tugmalar: Optional['InlineTugma'] = None,
                        parse_mode: str = "HTML"):
        """
        Xabarni tahrirlash
        
        Args:
            callback: Callback query obyekti
            matn: Yangi matn
            tugmalar: Yangi tugmalar
            parse_mode: Matn formati
        """
        keyboard = None
        if tugmalar:
            keyboard = tugmalar.yasash()
        
        await callback.message.edit_text(
            matn,
            reply_markup=keyboard,
            parse_mode=parse_mode
        )
    
    async def javob_berish(self, 
                          callback: CallbackQuery, 
                          matn: str,
                          ogohlantirish: bool = False):
        """
        Callback query ga javob berish
        
        Args:
            callback: Callback query obyekti
            matn: Javob matni
            ogohlantirish: Alert ko'rinishida ko'rsatish
        """
        await callback.answer(matn, show_alert=ogohlantirish)
    
    async def rasm_yuborish(self,
                           xabar: Message,
                           rasm: Union[str, bytes],
                           izoh: str = "",
                           tugmalar: Optional[Union['Tugma', 'InlineTugma']] = None):
        """
        Rasm yuborish
        
        Args:
            xabar: Xabar obyekti
            rasm: Rasm fayl yo'li yoki bytes
            izoh: Rasm izohi
            tugmalar: Tugmalar
        """
        keyboard = None
        if tugmalar:
            keyboard = tugmalar.yasash()
        
        if isinstance(rasm, str):
            return await xabar.answer_photo(
                photo=rasm,
                caption=izoh,
                reply_markup=keyboard
            )
        else:
            from aiogram.types import BufferedInputFile
            photo = BufferedInputFile(rasm, filename="rasm.jpg")
            return await xabar.answer_photo(
                photo=photo,
                caption=izoh,
                reply_markup=keyboard
            )
    
    async def video_yuborish(self,
                            xabar: Message,
                            video: Union[str, bytes],
                            izoh: str = "",
                            tugmalar: Optional[Union['Tugma', 'InlineTugma']] = None):
        """Video yuborish"""
        keyboard = None
        if tugmalar:
            keyboard = tugmalar.yasash()
        
        return await xabar.answer_video(
            video=video,
            caption=izoh,
            reply_markup=keyboard
        )
    
    async def fayl_yuborish(self,
                           xabar: Message,
                           fayl: Union[str, bytes],
                           izoh: str = "",
                           tugmalar: Optional[Union['Tugma', 'InlineTugma']] = None):
        """Fayl yuborish"""
        keyboard = None
        if tugmalar:
            keyboard = tugmalar.yasash()
        
        return await xabar.answer_document(
            document=fayl,
            caption=izoh,
            reply_markup=keyboard
        )
    
    async def holat_olish(self, xabar: Message) -> FSMContext:
        """
        Foydalanuvchi holatini olish
        
        Args:
            xabar: Xabar obyekti
            
        Returns:
            FSMContext obyekti
        """
        return await self.dp.fsm.get_context(
            bot=self.bot,
            user_id=xabar.from_user.id,
            chat_id=xabar.chat.id
        )
    
    async def holat_ozgartirish(self, xabar: Message, holat):
        """
        Foydalanuvchi holatini o'zgartirish
        
        Args:
            xabar: Xabar obyekti
            holat: Yangi holat
        """
        state = await self.holat_olish(xabar)
        await state.set_state(holat)
    
    async def holat_tozalash(self, xabar: Message):
        """Holatni tozalash"""
        state = await self.holat_olish(xabar)
        await state.clear()
    
    async def malumot_saqlash(self, xabar: Message, kalit: str, qiymat):
        """
        Ma'lumot saqlash
        
        Args:
            xabar: Xabar obyekti
            kalit: Ma'lumot kaliti
            qiymat: Ma'lumot qiymati
        """
        state = await self.holat_olish(xabar)
        await state.update_data(**{kalit: qiymat})
    
    async def malumot_olish(self, xabar: Message, kalit: Optional[str] = None):
        """
        Ma'lumot olish
        
        Args:
            xabar: Xabar obyekti
            kalit: Ma'lumot kaliti (agar berilmasa, barcha ma'lumotlar qaytadi)
            
        Returns:
            Saqlangan ma'lumot
        """
        state = await self.holat_olish(xabar)
        data = await state.get_data()
        
        if kalit:
            return data.get(kalit)
        return data
    
    def ishga_tushirish(self):
        """
        Botni ishga tushirish
        
        Misol:
            bot.ishga_tushirish()
        """
        self.logger.info("Bot ishga tushirilmoqda...")
        asyncio.run(self.dp.start_polling(self.bot))
    
    def to_xtatish(self):
        """Botni to'xtatish"""
        self.logger.info("Bot to'xtatilmoqda...")
        asyncio.run(self.bot.session.close())