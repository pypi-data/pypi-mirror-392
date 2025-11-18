from dataclasses import dataclass
import random
from functools import partial

import pygame

from ratisbona_pygames.gameutils import Game, FPSCounter, Background, GameElement, Debounce, Popup, PYGAME_KEYCODE
from ratisbona_pygames.gameutils._timeing import FrameBasedTimer, KeyPressBasedTimer


@dataclass
class BallDrawer:
    game: Game
    rect: pygame.Rect
    mode_1_max_num_elements: int = 6
    mode_1_min_num_elements: int = 1
    radius: int = 35
    ballnum: int = 0


    def __post_init__(self):
        self.surface = pygame.Surface(self.rect.size)
        self.surface.set_colorkey("black")


    def create_drawing(self):
        self.surface.fill("black")
        self.ballnum = random.randint(self.min_num_elements, self.max_num_elements)
        for _ in range(self.ballnum):
            x = random.randint(self.radius, self.rect.width - self.radius)
            y = random.randint(self.radius, self.rect.height - self.radius)
            pygame.draw.circle(self.surface, "white", (x, y), self.radius)

    def render(self):
        self.game.screen.blit(self.surface, self.rect.topleft)


def death_by_powerpoint():

    def restart(key: PYGAME_KEYCODE):
        k1.action = trigger_mode_1
        k2.action = trigger_mode_2

    def reveal(key: PYGAME_KEYCODE):
        keypresstimer.then_callback = restart
        keypresstimer.repeat_callback = ball_drawer.render
        keypresstimer.keys = [pygame.K_RETURN]

    def wait_for_reveal():
        keypresstimer.then_callback = reveal
        keypresstimer.repeat_callback = None
        keypresstimer.keys = [pygame.K_RETURN]

    def flash_the_dots():
        print("flashing dots")
        ball_drawer.create_drawing()
        frame_based_timer.repeat(ball_drawer.render, 3, wait_for_reveal)
        return "Done"

    def random_wait():
        nonlocal flash_the_dots

        k1.action = None
        k2.action = None
        num_frames = random.randint(1, 3) * 60

        frame_based_timer.repeat(None, num_frames, flash_the_dots)

    def trigger_mode(mode_num):
        nonlocal random_wait, flash_the_dots
        k1.action = None
        k2.action = None

        ball_drawer.min_num_elements = 1 + (2 - mode_num) * 6
        ball_drawer.max_num_elements = (3-mode_num) * 6

        mode_title = modenum_font.render(f"Mode {mode_num}", True, "white")
        mode_subtitle = mode_subtitle_font.render(f"{ball_drawer.min_num_elements} - {ball_drawer.max_num_elements} Points", True, "white")

        def blit():
            game.screen.blit(mode_title, (game.screen.get_width() // 2 - mode_title.get_width() // 2, 200))
            game.screen.blit(mode_subtitle, (game.screen.get_width() // 2 - mode_subtitle.get_width() // 2, 300))

        frame_based_timer.repeat(blit, 1*60, random_wait)

    game = Game((1920, 1080), "Death by PowerPoint")
    pygame.display.toggle_fullscreen()

    framecounter_font = pygame.font.SysFont("Noto Sans", 18)
    fps = FPSCounter(game, framecounter_font)
    game.tickers.append(fps.tick)
    game.renderers.append(fps.render)

    background = Background(game, "black")
    game.renderers.append(background.render)

    ball_drawer = BallDrawer(game, pygame.Rect(0, 0, game.screen.get_width(), game.screen.get_height()))

    modenum_font = pygame.font.SysFont("Noto Sans", 60)
    mode_subtitle_font = pygame.font.SysFont("Noto Sans", 150)

    keypresstimer = KeyPressBasedTimer(game)
    game.tickers.append(keypresstimer.tick)
    game.renderers.append(keypresstimer.render)

    frame_based_timer = FrameBasedTimer()
    game.tickers.append(frame_based_timer.tick)
    game.renderers.append(frame_based_timer.render)

    trigger_mode_1 = partial(trigger_mode, 1)
    trigger_mode_2 = partial(trigger_mode, 2)

    k1 = Debounce(game, pygame.K_1, trigger_mode_1)
    k2 = Debounce(game, pygame.K_2, trigger_mode_2)

    game.tickers.append(k1.tick)
    game.tickers.append(k2.tick)

    game.run()
