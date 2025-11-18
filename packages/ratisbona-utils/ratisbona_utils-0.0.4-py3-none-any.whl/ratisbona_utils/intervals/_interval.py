from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T", bound="Comparable")


@dataclass(frozen=True)
class Interval:
    start: T
    end: T

    def contains(self, item: T) -> bool:
        return self.start <= item <= self.end

    def intersect(self, other: Interval) -> tuple[Interval, Interval, Interval]:

        # Part of other that is before self
        before_part = (
            Interval(other.start, min(other.end, self.start))
            if other.start < self.start
            else None
        )

        # Part of other that intersects with self
        intersection_start = max(self.start, other.start)
        intersection_end = min(self.end, other.end)
        intersection = (
            Interval(intersection_start, intersection_end)
            if intersection_start < intersection_end
            else None
        )

        # Part of other that is after self
        after_part = (
            Interval(max(other.start, self.end), other.end)
            if other.end > self.end
            else None
        )
        return before_part, intersection, after_part
