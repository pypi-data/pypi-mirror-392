from typing import Protocol, TypeVar

T = TypeVar('T', bound='Comparable')


class Comparable(Protocol):
    def __lt__(self: T, other: T) -> bool: ...


class Indexable(Protocol[T]):
    def __getitem__(self, index: int) -> T: ...

    def __len__(self) -> int: ...


def perm_sign(perm: Indexable[T]) -> int:
    """
    Bestimmt das Vorzeichen einer Permutation.

    Args:
        perm (Indexable[T]): Eine beliebige indexierbare Sequenz von vergleichbaren Elementen.

    Returns:
        int: +1 für gerade Permutationen, -1 für ungerade Permutationen.
    """
    inversions = 0
    n = len(perm)
    for i in range(n):
        for j in range(i + 1, n):
            if perm[i] > perm[j]:  # __lt__ wird hier genutzt
                inversions += 1
    return 1 if inversions % 2 == 0 else -1
