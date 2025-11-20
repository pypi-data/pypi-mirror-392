from rynput.validators import Option
from typing import Optional

class Bool(Option):
    def __init__(self):
        self.options = ["true", "false"]

    def validate(self, string: str) -> Optional[bool]:
        if string.lower() in self.options:
            return string == "true"
        return None