"""Class representing a text message to be displayed on the screen"""

from .functions import get_millis

TEXT_DISPLAY_TIME_MS = 3 * 1000
TEXT_COLOR = (0, 0, 0)

class TextMessage:
    
    def __init__(self, message, x, y):
        self.message = message
        self.color = TEXT_COLOR
        self.spawn_time = get_millis()
        self.x = x
        self.y = y
        
    def is_active(self):
        return self.spawn_time > (get_millis() - TEXT_DISPLAY_TIME_MS)
