from typing import overload
from sales.models import Deal


@overload
def total_func(value: Deal) -> int: ...
@overload
def total_func(value: list) -> int: ...


def total_func(value):
    if isinstance(value, Deal):
        return value.price
    elif isinstance(value, list):
        pr = 0
        for item in value:
            pr += item.price
        return pr
    else:
        raise TypeError
