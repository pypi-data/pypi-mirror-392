from rynput.validator import Validator, Optional
from typing import List

class Option(Validator):
    def __init__(self, options: List[str]):
        self.options: List[str] = options

    def query_string(self) -> str:
        return ", ".join(self.options)
    
    def validate(self, string: str) -> Optional[str]:
        if string in self.options:
            return string
        return None