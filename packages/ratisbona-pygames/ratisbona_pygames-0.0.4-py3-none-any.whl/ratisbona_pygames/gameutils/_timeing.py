import time
from dataclasses import dataclass, Field, field
from typing import Callable

from ratisbona_pygames.gameutils import GameElement, PYGAME_KEYCODE, Game


@dataclass
class KeyPressBasedTimer:
    game: Game
    keys: list[PYGAME_KEYCODE] = field(default_factory=list)
    then_callback: Callable[[PYGAME_KEYCODE], None] | None = None
    repeat_callback: Callable[[], None] | None = None
    dead_time_frames: int = 0

    def tick(self):
        if self.dead_time_frames > 0:
            self.dead_time_frames -= 1
            return

        for key in self.keys:
            if self.game.keys[key]:
                self.repeat_callback = None
                if self.then_callback is not None:
                    self.dead_time_frames = 30
                    self.then_callback(key)
                return


    def render(self):
        if self.repeat_callback is not None:
            self.repeat_callback()



@dataclass
class FrameBasedTimer:
    remaining: int = 0
    repeat_callback: Callable[[], None] | None = None
    then_callback: Callable[[], None] | None = None

    def repeat(
            self,
            repeat: Callable[[], None] | None,
            for_num_frames: int,
            and_then: Callable[[], None] | None = None
    ):
        self.repeat_callback = repeat
        self.then_callback = and_then
        self.remaining = for_num_frames

    def tick(self):
        if self.remaining <= 0:
            return

        self.remaining -= 1
        if self.remaining == 0:
            if self.then_callback is not None:
                self.repeat_callback = None
                self.then_callback()
            return

    def render(self):
        if self.remaining > 0 and self.repeat_callback is not None:
            self.repeat_callback()


def run_precise_millisecond_timer(callback: Callable[[int], None], milliseconds=20):
    """
    Callback will be executed at the start of millisecond, every milliseconds given. So if you specify 1000,
    you should get a callback every second, at the start of the second.

    * For 50 Hz specify 20 milliseconds.
    * For 60 Hz specify 16 milliseconds.

    The callback will be executed as precisely as possible, but the actual timing may vary depending on
    the system load and other factors.

    The routine avoids as much busy-waiting as possible, but it still relies on a polling principle.

    Args:
        callback (Callable[[int], None]): The callback function to be executed. The argument is the time in milliseconds
        the execution was planned. So if you specified 100ms it will be 100, 200, 300, etc. not reflecting the actual
        execution millisecond.

        Use modulo-counting to derive slower clock rates. So if you specify 100ms and you want to get a callback every 1000ms,
        you can do `if milliseconds % 1000 == 0: ...`.

    """
    while True:
        now = time.time()
        next_millisecond = int(now * 1000 / milliseconds) * milliseconds + milliseconds
        sleep_length = next_millisecond / 1000 - now
        if sleep_length > 0:
            time.sleep(sleep_length)
        callback(next_millisecond)