from rynput.validator import Validator, Optional

class Float(Validator):
    def __init__(self, min: Optional[float] = None, max: Optional[float] = None):
        self.min = min
        self.max = max

    def query_string(self) -> str:
        if self.min is None and (not self.max is None):
            return f"float: x < {self.max}"
        if (not self.min is None) and self.max is None:
            return f"float: x > {self.min}"
        if (not self.min is None) and (not self.max is None):
            return f"float: {self.min} < x < {self.max}"
        return "float"
    
    def validate(self, string: str) -> Optional[float]:
        try:
            value = float(string)
            if (not self.min is None) and value < self.min:
                return None
            if (not self.max is None) and value > self.max:
                return None
            return value
        except:
            return None