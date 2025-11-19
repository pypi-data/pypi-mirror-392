from dataclasses import is_dataclass, asdict, fields, dataclass
from typing import get_origin, get_args
import types
import json
import sys

if sys.version_info >= (3, 11):
    from typing import dataclass_transform
else:
    from typing_extensions import dataclass_transform


VERSION = '0.0.3-alpha2'


def to_dict(obj):
    """
    Recursively convert a dataclass into a dict.
    Supports:
    - Nested dataclasses
    - Optional types (Type | None)
    - Lists of dataclasses (list[DataclassType])
    - Optional lists (list[DataclassType] | None)
    """
    # Handle None
    if obj is None:
        return None
    
    # If not a dataclass, return as-is
    if not is_dataclass(obj):
        return obj
    
    result = {}
    for field in fields(obj):
        value = getattr(obj, field.name)
        
        # Handle None values
        if value is None:
            result[field.name] = None
            continue
        
        # Handle lists
        if isinstance(value, list):
            result[field.name] = [to_dict(item) if is_dataclass(item) else item for item in value]
        # Handle nested dataclasses
        elif is_dataclass(value):
            result[field.name] = to_dict(value)
        # Handle primitive types
        else:
            result[field.name] = value
    
    return result


def from_dict(cls, data):
    """
    Recursively convert a dict into a dataclass of type `cls`.
    Supports:
    - Nested dataclasses
    - Optional types (Type | None)
    - Lists of dataclasses (list[DataclassType])
    - Optional lists (list[DataclassType] | None)
    """
    if not is_dataclass(cls):
        return data
    
    kwargs = {}
    for f in fields(cls):
        value = data.get(f.name)
        
        # Handle None values
        if value is None:
            kwargs[f.name] = None
            continue
        
        field_type = f.type
        origin = get_origin(field_type)
        
        # Handle Union types (e.g., Type | None, which is Union[Type, None])
        if origin is types.UnionType or (hasattr(types, 'UnionType') and origin is getattr(types, 'UnionType', None)):
            # Get the non-None type from the union
            type_args = get_args(field_type)
            non_none_types = [t for t in type_args if t is not type(None)]
            
            if non_none_types:
                field_type = non_none_types[0]
                origin = get_origin(field_type)
        
        # Handle list types
        if origin is list:
            type_args = get_args(field_type)
            if type_args and is_dataclass(type_args[0]):
                # List of dataclasses
                item_type = type_args[0]
                kwargs[f.name] = [from_dict(item_type, item) for item in value]
            else:
                kwargs[f.name] = value
        # Handle dataclass types
        elif is_dataclass(field_type):
            kwargs[f.name] = from_dict(field_type, value)
        else:
            kwargs[f.name] = value
    
    return cls(**kwargs)


@dataclass_transform()
def edataclass(cls=None, **dataclass_kwargs):
    """
    Enhanced dataclass decorator that automatically adds:
    - to_dict() instance method
    - from_dict(data) class method
    - to_json(indent=None) instance method
    - from_json(json_str) class method
    
    Usage:
        @edataclass
        class MyClass:
            field: int
    
    Or with dataclass arguments:
        @edataclass(frozen=True)
        class MyClass:
            field: int
    """
    def wrapper(cls):
        # Apply the standard dataclass decorator
        cls = dataclass(cls, **dataclass_kwargs)
        
        # Add to_dict method
        def _to_dict(self):
            return to_dict(self)
        cls.to_dict = _to_dict
        
        # Add from_dict class method
        @classmethod
        def _from_dict(kls, data: dict):
            return from_dict(kls, data)
        cls.from_dict = _from_dict
        
        # Add to_json method
        def _to_json(self, indent=None):
            return json.dumps(self.to_dict(), indent=indent)
        cls.to_json = _to_json
        
        # Add from_json class method
        @classmethod
        def _from_json(kls, json_str: str):
            data = json.loads(json_str)
            return kls.from_dict(data)
        cls.from_json = _from_json
        
        # Add to_json method
        def _clone(self, indent=None):
            return self.from_json(self.to_json())
        cls.clone = _clone

        return cls
    
    # Handle both @edataclass and @edataclass() syntax
    if cls is None:
        # Called with arguments: @edataclass(frozen=True)
        return wrapper
    else:
        # Called without arguments: @edataclass
        return wrapper(cls)


easdict = to_dict
efromdict = from_dict

