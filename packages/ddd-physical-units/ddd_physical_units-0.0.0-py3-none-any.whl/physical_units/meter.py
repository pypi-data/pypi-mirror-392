import dataclasses

from .base_physical_unit import BasePhysicalUnit

__all__ = (
    'Meter',
    'm',
    'meter',
)


@dataclasses.dataclass(eq=False)
class Meter(BasePhysicalUnit):
    """The unit of length measurement"""
    label: str = 'm'


m = meter = Meter(value=1)
