from aiogram.fsm.state import State, StatesGroup

class HolatGuruhi(StatesGroup):
    """
    Holatlar guruhini yaratish uchun klass
    
    Misol:
        class Royxat(HolatGuruhi):
            ism = Holat()
            yosh = Holat()
            telefon = Holat()
    """
    pass

def Holat():
    """
    Holat yaratish
    
    Returns:
        State obyekti
    """
    return State()