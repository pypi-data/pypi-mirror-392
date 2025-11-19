# expli/main.pyi
import sys
from typing import Any, TypeVar, Callable, overload, Type

if sys.version_info >= (3, 11):
    from typing import dataclass_transform
else:
    from typing_extensions import dataclass_transform

_T = TypeVar('_T')

# --- Stubs for your other functions ---
def to_dict(obj: Any) -> dict: ...
def from_dict(cls: Type[_T], data: dict) -> _T: ...
easdict: Callable[[Any], dict]
efromdict: Callable[[Type[_T], dict], _T]


# --- Correct stubs for edataclass ---
# This is what tells PyCharm your decorator
# generates an __init__ method.

@dataclass_transform()
@overload
def edataclass(cls: Type[_T]) -> Type[_T]: ...

@dataclass_transform()
@overload
def edataclass(
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
) -> Callable[[Type[_T]], Type[_T]]: ...