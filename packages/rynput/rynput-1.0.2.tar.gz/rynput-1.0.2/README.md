# Rynput
Python tools for strongly typed input validation.

## Description
Rynput is focused on validating strings and converting them to a specific type, if possible.
It is particularily effective when configuring a large list of properties which may have
very different requirements for their values.

## Installation
Run `pip install rynput`.

## Usage
It is recommended to use the following import statement:
```python
from rynput import Property, PropertyGroup, validators
```
From there, create the list of properties to validate.
The constructor for `Property` takes a name (`str`), type (`Validator`), and
optionally a default value and description. Omitting a default value means
that the property is marked as "required," and thus cannot be omitted by
the input method.
```python
properties = PropertyGroup([
    Property("Option", validators.Option(["Foo", "Bar", "Baz"]), "Foo"), # Default value provided
    Property("Integer", validators.Integer(4, 8)), # Required
    ...
])
```
The input strings may come from anywhere. However, typical examples may include a user configuration wizard
(see `examples/input_example.py`) or from a config file (`examples/json_example.py`).
