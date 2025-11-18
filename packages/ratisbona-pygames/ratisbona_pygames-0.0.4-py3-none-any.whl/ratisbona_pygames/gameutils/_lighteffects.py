from dataclasses import dataclass
from typing import Callable


@dataclass
class LarsonScanner:
    callback: Callable[[int, bool], None] = None
    num_lights: int = 8
    extra_border: int = 2
    trailing_lights: int = 1
    _current_leading_state: int = 0
    _current_trailing_state: int = 0
    _current_direction: int = -1

    def __post_init__(self):
        if self.num_lights <= 2:
            raise ValueError("Number of lights must be greater than two")
        if self.extra_border < 0:
            raise ValueError("Extra border must be non-negative")
        if self.trailing_lights < 0:
            raise ValueError("Trailing lights must be non-negative")
        self._current_trailing_state = self.trailing_lights

    def cycle(self):
        # Mind that internal states have extra borders!
        if 0 <= self._current_leading_state < self.num_lights:
            self.callback(self._current_leading_state, True)
        if 0 <= self._current_trailing_state < self.num_lights:
            self.callback(self._current_trailing_state, False)

        self.step_state()

    def step_state(self):
        if (
                self._current_leading_state <= -self.extra_border
                or (self._current_leading_state >= self.num_lights - 1 + self.extra_border)
        ):  # boundary hit!
            self._current_leading_state, self._current_trailing_state = (
                self._current_trailing_state, self._current_leading_state
            )
            self._current_direction = -self._current_direction
        else:  # no boundary hit...
            self._current_leading_state += self._current_direction
            self._current_trailing_state += self._current_direction
