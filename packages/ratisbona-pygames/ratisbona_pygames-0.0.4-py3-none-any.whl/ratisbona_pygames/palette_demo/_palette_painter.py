from functools import partial
from math import floor
from typing import Callable, List, Tuple

import pygame

from ratisbona_pygames.gameutils import GameElement, Game, Background, Debounce
from ratisbona_utils.colors import linear_interpolate
from ratisbona_utils.colors.good_palettes import (
    ULIS_WEBCOLORS_RGB,
    EGA_PALETTE_RGB,
    CGA_PALETTE_RGB,
    AMIGA_PALETTE_RGB,
    SOLARIZED_COLORS_EXTENDED,
    solarized_base03,
)
from ratisbona_utils.colors.palette_generators import (
    cielch_based_rgb_palette,
    hsv_based_rgb_palette, matplotlib_colormap_to_palette
)


class PalettePainter:

    def __init__(self, game, rect, palette, borders=False):
        self.game = game
        self.rect = rect
        self.palette = palette
        self.borders = borders

    def render(self):
        rect_width = self.rect.width
        rect_height = self.rect.height
        color_width = rect_width / len(self.palette)
        for i, color in enumerate(self.palette):
            area = pygame.Rect(
                self.rect.x + round(i * color_width),
                self.rect.y,
                floor(color_width) + 1,
                rect_height,
            )
            pygame.draw.rect(self.game.screen, color, area)
            if self.borders:
                pygame.draw.rect(self.game.screen, "white", area, 1)


def scene1(game: Game, quit_scene_action: Callable):
    game.renderers.clear()
    game.tickers.clear()
    game.event_listeners.clear()

    background = Background(game, solarized_base03)
    game.renderers.append(background.render)

    palettes = [
        linear_interpolate(ULIS_WEBCOLORS_RGB, 32),
        hsv_based_rgb_palette(32, 0.9, 0.85),
        cielch_based_rgb_palette(32, 75, 85),
        matplotlib_colormap_to_palette(32, "terrain"),
        matplotlib_colormap_to_palette(32, "viridis"),
        SOLARIZED_COLORS_EXTENDED,
        EGA_PALETTE_RGB,
        CGA_PALETTE_RGB,
        AMIGA_PALETTE_RGB,
    ]

    rects = [
        pygame.Rect(50, 40 + i * 60, game.screen.get_width() - 100, 40)
        for i in range(len(palettes))
    ]

    painters = [
        PalettePainter(game, rect, palette, True)
        for rect, palette in zip(rects, palettes)
    ]
    for painter in painters:
        game.renderers.append(painter.render)

    ret_key = Debounce(game, pygame.K_RETURN, quit_scene_action, 10)
    game.tickers.append(ret_key.tick)


def palette_scene(
    game: Game,
    palette_generator: Callable[[int, int, int, int], List[Tuple[int, int, int]]],
    next_scene_action: Callable,
):
    game.renderers.clear()
    game.tickers.clear()
    game.event_listeners.clear()

    background = Background(game, (0,0,0))

    game.renderers.append(background.render)

    n_rows = 10
    n_cols = 10
    w = game.screen.get_width()
    h = game.screen.get_height()

    margin_x = 5
    margin_y = 10
    col_width = w // n_cols
    inner_width = col_width - 2 * margin_x
    row_height = h // n_rows
    inner_height = row_height - 2 * margin_y

    for row in range(n_rows):
        for col in range(n_cols):
            palette = palette_generator(row, col, n_rows, n_cols)
            palette_painter = PalettePainter(
                game,
                pygame.Rect(
                    margin_x + col * col_width,
                    margin_y + row * row_height,
                    inner_width,
                    inner_height,
                ),
                palette,
            )
            game.renderers.append(palette_painter.render)

    ret_key = Debounce(game, pygame.K_RETURN, next_scene_action, 10)
    game.tickers.append(ret_key.tick)



def main_game_palette_demo():
    game = Game((1920, 1080))
    pygame.display.toggle_fullscreen()

    max_lightness = 100
    min_lightness = 20
    max_chroma = 200
    min_chroma = 20

    def scene2_palette(row, col, n_rows, n_cols):
        lightness_step = (max_lightness - min_lightness) / n_rows
        chroma_step = (max_chroma - min_chroma) / n_cols
        return cielch_based_rgb_palette(
            32, row * lightness_step + min_lightness, col * chroma_step + min_chroma
        )

    hue_steps = 32
    min_saturation = 0.1
    max_saturation = 1
    min_value = 0.1
    max_value = 1

    def scene3_palette(row, col, n_rows, n_cols):
        saturation_step = (max_saturation - min_saturation) / n_cols
        value_step = (max_value - min_value) / n_rows
        return hsv_based_rgb_palette(
            hue_steps,
            col * saturation_step + min_saturation,
            row * value_step + min_value,
        )

    scene3_command = partial(palette_scene, game, scene3_palette, game.stop)
    scene2_command = partial(palette_scene, game, scene2_palette, scene3_command)

    scene1(game, scene2_command)
    game.run()
