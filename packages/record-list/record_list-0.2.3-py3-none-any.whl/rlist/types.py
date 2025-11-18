from typing import Protocol, Any, Callable, TypeVar, TypeAlias


R = TypeVar("R")


class SupportsLt(Protocol):
    def __lt__(self, other: R) -> bool: ...


FilterFunc: TypeAlias = Callable[[R], bool]
MapFunc: TypeAlias = Callable[[R], Any]
SortFunc: TypeAlias = Callable[[R], SupportsLt]

ListMultiplier: TypeAlias = int
ListAddend: TypeAlias = list[R]
ListComparand: TypeAlias = list[R]
