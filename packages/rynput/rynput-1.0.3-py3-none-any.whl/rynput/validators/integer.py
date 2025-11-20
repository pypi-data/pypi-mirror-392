from rynput.validator import Validator, Optional

class Integer(Validator):
    def __init__(self, min: Optional[int] = None, max: Optional[int] = None):
        self.min = min
        self.max = max

    def query_string(self) -> str:
        if self.min is None and (not self.max is None):
            return f"int: x < {self.max}"
        if (not self.min is None) and self.max is None:
            return f"int: x > {self.min}"
        if (not self.min is None) and (not self.max is None):
            return f"int: {self.min} < x < {self.max}"
        return "int"
    
    def validate(self, string: str) -> Optional[int]:
        try:
            value = int(string)
            if (not self.min is None) and value < self.min:
                return None
            if (not self.max is None) and value > self.max:
                return None
            return value
        except:
            return None