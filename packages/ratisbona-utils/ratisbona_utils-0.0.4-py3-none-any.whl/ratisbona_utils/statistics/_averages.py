from dataclasses import dataclass, field
from statistics import mean


@dataclass
class RunningAverage():
    window_size: int
    _samples: list[float] = field(default_factory=list)
    _current_index: int = 0

    def __post_init__(self):
        if self.window_size <= 0:
            raise ValueError("Window size must be positive")
        self._samples = [0.0] * self.window_size

    def add_sample(self, sample: float):
        self._samples[self._current_index] = sample
        self._current_index = (self._current_index + 1) % self.window_size

    def mean(self) -> float:
        return mean(self._samples)

