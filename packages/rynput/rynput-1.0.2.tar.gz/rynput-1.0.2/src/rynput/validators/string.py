from rynput.validator import Validator

class String(Validator):
    def validate(self, string: str) -> str:
        return string