from rynput.validator import Validator, Optional
from re import fullmatch, Pattern

class RegEx(Validator):
    def __init__(self, regex: Pattern):
        self.regex = regex

    def query_string(self):
        return f"RegEx: {self.regex}"

    def validate(self, string: str) -> Optional[str]:
        if fullmatch(self.regex, string):
            return string
        return None