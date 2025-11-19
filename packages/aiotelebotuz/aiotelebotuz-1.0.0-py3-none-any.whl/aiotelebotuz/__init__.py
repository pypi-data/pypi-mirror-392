"""
AioTeleBotUz - Aiogram 3 uchun o'zbekcha va juda oson kutubxona
"""

from .bot import OsonBot
from .tugmalar import Tugma, InlineTugma
from .holat import Holat, HolatGuruhi
from .media import Media

__version__ = "1.0.0"
__all__ = [
    'OsonBot',
    'Tugma',
    'InlineTugma',
    'Holat',
    'HolatGuruhi',
    'Media',
]