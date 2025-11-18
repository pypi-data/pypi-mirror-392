import dataclasses

from .base_physical_unit import BasePhysicalUnit

__all__ = (
    'Second',
    's',
    'second',
)


@dataclasses.dataclass(eq=False)
class Second(BasePhysicalUnit):
    """The unit of time measurement"""
    label: str = 's'


s = second = Second(value=1)
