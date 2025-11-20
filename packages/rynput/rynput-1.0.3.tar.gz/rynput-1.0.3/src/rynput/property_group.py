from . import Property
from typing import List

class PropertyGroup:
    def __init__(self, properties: List[Property]):
        self.properties = properties
    
    def values_from_dict(self, source: dict, warnings: bool = True) -> dict:
        result = {}
        for property in self.properties:
            value = None
            # Try to assign value from the source dict
            if property.name in source:
                value = property.validate(source[property.name])
                # If it's not a valid value, use the default if it exists
                if value is None:
                    if property.default_value is None:
                        raise TypeError(f"\"{source[property.name]}\" is not valid for property \"{property.name}\" and no default value is supplied")
                    elif warnings:
                        print(f"Warning: property \"{property.name}\" has an invalid value. Using the default ({property.default_value})...")
            
            # If the value wasn't in the source, use the default value if it exists
            if value is None:
                if property.default_value is None:
                    raise TypeError(f"No value was supplied for \"{property.name}\" and no default value exists")
                value = property.default_value
            result[property.name] = value
        return result

    def values_from_defaults(self) -> dict:
        result = {}
        for property in self.properties:
            result[property.name] = property.default_value
        return result
    

    def values_from_input(self) -> dict:
        result = {}
        for property in self.properties:
            result[property.name] = property.prompt()
        return result