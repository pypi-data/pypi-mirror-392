# expli

**Explicit dataclasses with automatic serialization**

`expli` (short for "explicit") enhances Python dataclasses with automatic dictionary and JSON serialization methods, making it effortless to work with nested dataclasses, optional types, and lists.

## Installation

```bash
pip install expli
```

## Quick Start

```python
from expli import edataclass

@edataclass
class Person:
    name: str
    age: int
    email: str | None = None

# Automatic methods are added!
person = Person("Alice", 30, "alice@example.com")

# Convert to dict
data = person.to_dict()

# Convert to JSON
json_str = person.to_json(indent=2)

# Create from dict
person2 = Person.from_dict(data)

# Create from JSON
person3 = Person.from_json(json_str)
```

## Features

### 🎯 Enhanced Dataclass Decorator

The `@edataclass` decorator automatically adds four methods to your dataclass:

- `to_dict()` - Convert instance to dictionary
- `from_dict(data)` - Create instance from dictionary (class method)
- `to_json(indent=None)` - Convert instance to JSON string
- `from_json(json_str)` - Create instance from JSON string (class method)

### 🔄 Full Recursive Support

`expli` handles complex nested structures automatically:

```python
from expli import edataclass

@edataclass
class Address:
    street: str
    city: str
    country: str

@edataclass
class Company:
    name: str
    address: Address

@edataclass
class Person:
    name: str
    age: int
    company: Company | None
    hobbies: list[str]

person = Person(
    name="Alice",
    age=30,
    company=Company(
        name="Tech Corp",
        address=Address("123 Main St", "Boston", "USA")
    ),
    hobbies=["reading", "coding"]
)

# Everything serializes recursively
data = person.to_dict()
# {
#     "name": "Alice",
#     "age": 30,
#     "company": {
#         "name": "Tech Corp",
#         "address": {
#             "street": "123 Main St",
#             "city": "Boston",
#             "country": "USA"
#         }
#     },
#     "hobbies": ["reading", "coding"]
# }

# And deserializes back perfectly
person2 = Person.from_dict(data)
```

### ✨ Supported Types

- **Primitive types**: `str`, `int`, `float`, `bool`, etc.
- **Optional types**: `Type | None`
- **Lists**: `list[Type]`
- **Nested dataclasses**: Any dataclass as a field
- **Lists of dataclasses**: `list[DataclassType]`
- **Optional lists**: `list[Type] | None`

### 🛠️ Dataclass Parameters

`@edataclass` supports all standard `dataclass` parameters:

```python
from expli import edataclass

@edataclass(frozen=True, order=True)
class Config:
    api_key: str
    timeout: int = 30
```

## API Reference

### `@edataclass`

Enhanced dataclass decorator that adds serialization methods.

**Parameters**: Same as `@dataclass` (frozen, order, etc.)

**Added Methods**:
- `to_dict(self) -> dict` - Convert instance to dictionary
- `from_dict(cls, data: dict) -> Self` - Create instance from dictionary
- `to_json(self, indent=None) -> str` - Convert instance to JSON string
- `from_json(cls, json_str: str) -> Self` - Create instance from JSON string

### `to_dict(obj)` / `easdict(obj)`

Standalone function to convert a dataclass instance to a dictionary.

```python
from expli import to_dict, easdict
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

point = Point(10, 20)
data = to_dict(point)  # or easdict(point)
# {"x": 10, "y": 20}
```

### `from_dict(cls, data)` / `efromdict(cls, data)`

Standalone function to create a dataclass instance from a dictionary.

```python
from expli import from_dict, efromdict
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

data = {"x": 10, "y": 20}
point = from_dict(Point, data)  # or efromdict(Point, data)
```

## Why expli?

Standard dataclasses don't provide built-in serialization for nested structures. While `dataclasses.asdict()` exists, it doesn't handle deserialization, and neither function is added to your class for convenient access.

`expli` solves this by:
- ✅ Adding methods directly to your dataclass
- ✅ Handling nested dataclasses recursively
- ✅ Supporting optional types and lists
- ✅ Providing both dict and JSON serialization
- ✅ Working seamlessly with type hints

## Comparison

**Without expli:**
```python
from dataclasses import dataclass, asdict
import json

@dataclass
class Person:
    name: str
    age: int

person = Person("Alice", 30)

# Manual serialization
data = asdict(person)
json_str = json.dumps(data)

# Manual deserialization (you have to write this!)
def from_dict(data):
    return Person(**data)

person2 = from_dict(json.loads(json_str))
```

**With expli:**
```python
from expli import edataclass

@edataclass
class Person:
    name: str
    age: int

person = Person("Alice", 30)

# Built-in methods
data = person.to_dict()
json_str = person.to_json()
person2 = Person.from_dict(data)
person3 = Person.from_json(json_str)
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.