from abc import ABC, abstractmethod
from typing import Optional

class Validator():
    @abstractmethod
    def validate(self, string: str) -> Optional[any]:
        pass
    
    @abstractmethod
    def query_string(self) -> str:
        return type(self).__name__