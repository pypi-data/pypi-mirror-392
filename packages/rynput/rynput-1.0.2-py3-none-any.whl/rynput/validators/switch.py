from rynput.validators import Option
from typing import Optional

class Switch(Option):
    def __init__(self):
        self.options = ["on", "off"]

    def validate(self, string: str) -> Optional[bool]:
        if string.lower() in self.options:
            return string == "on"
        return None