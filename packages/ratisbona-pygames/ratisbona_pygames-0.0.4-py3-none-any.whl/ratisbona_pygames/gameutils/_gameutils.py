from contextlib import AbstractContextManager
from dataclasses import dataclass
from statistics import mean
from typing import Callable

import pygame
from pygame import K_UP, K_LEFT, K_DOWN, K_RIGHT, Vector2, Surface
from pygame.draw import rect
from pygame.font import Font
from pygame.pixelcopy import surface_to_array

PYGAME_KEYCODE = int


class GameElement:

    def tick(self):
        pass

    def render(self):
        pass


@dataclass
class Game:
    screen: pygame.Surface
    keys: pygame.key
    clock: pygame.time.Clock
    running: bool
    dt: float
    fps: int
    renderers: list[Callable[[], None]]
    tickers: list[Callable[[], None]]
    event_listeners: list[Callable[[pygame.event.Event], None]]

    def __init__(self, resolution=(1280, 960), caption="Game", fps=60):
        pygame.init()
        self.screen = pygame.display.set_mode(resolution)
        pygame.display.set_caption(caption)
        self.keys = pygame.key.get_pressed()
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.0
        self.fps = fps
        self.renderers = []
        self.tickers = []
        self.event_listeners = []


    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                for event_listener in self.event_listeners:
                    event_listener(event)

            for client in self.renderers:
                client()

            self.keys = pygame.key.get_pressed()
            if self.keys[pygame.K_ESCAPE]:
                self.running = False

            for client in self.tickers:
                client()

            pygame.display.flip()
            self.dt = self.clock.tick(self.fps) / 1000

        pygame.quit()


class Movement:

    def __init__(
        self,
        game,
        arrow_keys_wasd: list[PYGAME_KEYCODE] = [K_UP, K_LEFT, K_DOWN, K_RIGHT],
        speed_px_per_second: int = 300,
        initial_position: tuple[int, int] = (0, 0),
        screen_bounds: tuple[int, int, int, int] = None,
    ):
        self.game = game
        self.arrow_keys_wasd = arrow_keys_wasd
        self.actions = [self.up, self.left, self.down, self.right]
        self.speed_px_per_second = speed_px_per_second
        self.position = pygame.Vector2(initial_position)
        self.screen_bounds = screen_bounds

    def up(self, dt):
        self.position[1] -= self.speed_px_per_second * dt
        if self.screen_bounds is not None:
            self.position[1] = max(self.screen_bounds[1], self.position[1])

    def down(self, dt):
        self.position[1] += self.speed_px_per_second * dt
        if self.screen_bounds is not None:
            self.position[1] = min(self.screen_bounds[3], self.position[1])

    def left(self, dt):
        self.position[0] -= self.speed_px_per_second * dt
        if self.screen_bounds is not None:
            self.position[0] = max(self.screen_bounds[0], self.position[0])

    def right(self, dt):
        self.position[0] += self.speed_px_per_second * dt
        if self.screen_bounds is not None:
            self.position[0] = min(self.screen_bounds[2], self.position[0])

    def tick(self):
        for keypress, action in zip(self.arrow_keys_wasd, self.actions):
            if self.game.keys[keypress]:
                action(self.game.dt)


class Background:
    def __init__(self, game, color):
        self.game = game
        self.color = color

    def render(self):
        self.game.screen.fill(self.color)


class Popup(GameElement):

    def __init__(self, game, visible_secs, font):
        self.game = game
        self.visible_secs = visible_secs
        self.remaining_secs = 0.0
        self.font = font
        self.label = None

    def trigger(self, text):
        self.remaining_secs = self.visible_secs
        self.label = self.font.render(text, True, "white")

    def tick(self):
        self.remaining_secs = max(self.remaining_secs - self.game.dt, 0)

    def render(self):
        if not self.label:
            return
        if not self.remaining_secs > 0:
            return
        self.game.screen.blit(
            self.label,
            (
                self.game.screen.get_width() // 2 - self.label.get_width() // 2,
                self.game.screen.get_height() // 2,
            ),
        )


class FPSCounter:
    def __init__(self, game, font):
        self.game = game
        self.fps = [0] * 100
        self.idx = 0
        self.font = font
        text = self.font.render(f"FPS: {60.8:2.1f}", True, "white")
        self.pos = (self.game.screen.get_width() - text.get_width() - 10, 10)

    def tick(self):
        self.fps[self.idx] = int(1 / max(self.game.dt, 0.001))
        self.idx = (self.idx + 1) % len(self.fps)

    def render(self):
        text = self.font.render(f"FPS: {mean(self.fps):03.1f}", True, "white")
        self.game.screen.blit(text, self.pos)


@dataclass
class Debounce:
    """
    Debounces a key, connecting it with an action, that is executed, as soon as the debounced key
    is pressed.

    Fields:
        game: Game: The game that the element is part of
        key: PYGAME_KEYCODE: The key that is debounced
        action: Callable[[], None]: The action that is executed, as soon as the key is pressed
        block_number_frames: int: The number of frames that the key is blocked after being pressed
    """

    game: Game
    key: PYGAME_KEYCODE
    action: Callable[[], None] | None
    block_number_frames: int = 10
    _block_for_another_n_frames: int = block_number_frames

    def tick(self):
        if (
            self.action is not None
            and self.game.keys[self.key]
            and self._block_for_another_n_frames == 0
        ):
            self.action()
            self._block_for_another_n_frames = self.block_number_frames
        else:
            self._block_for_another_n_frames = max(
                0, self._block_for_another_n_frames - 1
            )


@dataclass
class SetReleaseDebounce:
    on_set_function: Callable[[], None]
    _is_set = False

    def set(self):
        if self._is_set:
            return
        self.on_set_function()
        self._is_set = True

    def release(self):
        self._is_set = False


@dataclass
class KeySetReleaseDebounce:
    game: Game
    set_release_debounce: SetReleaseDebounce
    key: PYGAME_KEYCODE

    def receive_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == self.key:
            self.set_release_debounce.set()
        elif event.type == pygame.KEYUP and event.key == self.key:
            self.set_release_debounce.release()


@dataclass
class Help(GameElement):
    """
    Displays a help text in the game.

    Fields:
        game: Game: The game that the element is part of
        font: pygame.font.Font: The font that is used for the help text
        text: str: The text that is displayed
        position: Vector2: The position of the help text
    """

    game: Game
    font: pygame.font.Font
    _text: str
    position: Vector2
    margins: int
    size: tuple[int, int]

    def __init__(self, game, font, text, position=Vector2(100, 100)):
        """
        Initializes the Help element.

        Args:
            game: Game: The game that the element is part of
            font: pygame.font.Font: The font that is used for the help text
            text: str: The text that is displayed
        """
        self.game = game
        self.font = font
        self.position = position
        self.margins = 20
        self._rendered_text = font.render("", True, "black")
        self._text = ""
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self._rendered_text = render_multiline_text(self.font, value, "black", "white")
        self.size = tuple[int, int](
            self._rendered_text.get_size() + Vector2(2 * self.margins, 2 * self.margins)
        )

    def render(self):
        if not self.game.keys[pygame.K_F1]:
            return

        rect(self.game.screen, "white", (*self.position, *self.size))
        self.game.screen.blit(
            self._rendered_text, (self.margins, self.margins) + self.position
        )


@dataclass(frozen=True)
class KeyHelp:
    key: str
    description: str


def to_helptext(keyhelps: list[KeyHelp]) -> str:
    """
    Converts a list of KeyHelps to a help text.

    Args:
        keyhelps: list[KeyHelp]: The list of KeyHelps to convert to a help text.

    Returns:
        str: The help text.
    """
    return "\n".join(f"{keyhelp.key:<5}: {keyhelp.description}" for keyhelp in keyhelps)


def render_multiline_text(
    font: Font, text: str, foreground, background=None
) -> Surface:
    linesize = font.get_linesize()

    width = max(font.size(line)[0] for line in text.splitlines())
    height = len(text.splitlines()) * linesize

    surface = pygame.Surface((width, height))
    surface.set_colorkey(background)
    surface.fill(background)
    pos = Vector2(0, 0)
    for line in text.splitlines():
        rendered_line = font.render(line, True, foreground, background)
        surface.blit(rendered_line, pos)
        pos += Vector2(0, linesize)
    return surface
