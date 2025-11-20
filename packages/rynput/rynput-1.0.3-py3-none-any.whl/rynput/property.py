from .validator import Validator, Optional

class Property:
    def __init__(self, name: str, type: Validator, default_value: Optional[any] = None, desc: Optional[str] = None):
        self.name = name
        self.type = type
        self.default_value = default_value
        self.desc = desc
    
    def validate(self, value: any) -> any:
        return self.type.validate(str(value))
    
    def validate_or_default(self, value: any) -> any:
        result = self.validate(str(value))
        if result is None:
            if self.default_value is None:
                raise TypeError(f"\"{value}\" is not valid for property \"{self.name}\" and no default value is supplied")
            return self.default_value
        return result
    
    def prompt(self, message: Optional[str] = None) -> any:
        result = None
        
        if self.default_value is None:
            while result is None:
                response = input(message or f"Choose a value for {self.name} [{self.type.query_string()}] (required): ")
                result = self.validate(response)
        else:
            while result is None:
                response = input(message or f"Choose a value for {self.name} [{self.type.query_string()}] ({self.default_value}): ")
                if not response:
                    result = self.default_value
                    break
                result = self.validate(response)
        return result