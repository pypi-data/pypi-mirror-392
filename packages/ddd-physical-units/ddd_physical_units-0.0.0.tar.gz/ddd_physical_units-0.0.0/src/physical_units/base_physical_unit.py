import dataclasses

__all__ = (
    'BasePhysicalUnit',
)


@dataclasses.dataclass(eq=False)
class BasePhysicalUnit:
    """Base for physical units"""
    value: int | float | complex
    """the value of a physical quantity"""
    label: str
    """The abbreviated name of a physical quantity, for example, "m" for meters, "s" for seconds."""

    def __str__(self) -> str:
        return f'{self.value!r}{self.label}'

    def __eq__(self, value: BasePhysicalUnit) -> bool:
        if not isinstance(value, self.__class__):
            raise TypeError(f'unable to compare "{type(value).__name__}" with "{self.__class__.__name__}"')

        if self.value == value.value:
            return True
        
        return False

    def __mul__(self, value: int | float | complex | BasePhysicalUnit) -> BasePhysicalUnit:
        if isinstance(value, (int, float, complex)):
            result: BasePhysicalUnit = self.__class__(value=self.value * value)
            return result
        
        raise TypeError(f'unsupported type "{type(value).__name__}" for __mul__ in "{self.__class__.__name__}"')
    
    def __rmul__(self, value: int | float | complex | BasePhysicalUnit) -> BasePhysicalUnit:
        result = self * value
        return result
