import numpy as np
import pygame
import scipy
from numpy import random
from ratisbona_utils.colors.good_palettes import FIRE_PALETTE
from ratisbona_utils.colors.palette import linear_interpolate

from scipy.signal import convolve2d

from ratisbona_pygames.gameutils import GameElement, Game, FPSCounter, Background, Debounce


def rgb_convolve2d(image, kernel):
    red = convolve2d(image[:, :, 0], kernel, 'valid')
    green = convolve2d(image[:, :, 1], kernel, 'valid')
    blue = convolve2d(image[:, :, 2], kernel, 'valid')
    return np.stack([red, green, blue], axis=2)


class Fire(GameElement):

    def __init__(self, game, zoom, rect):
        self.game = game
        self.palette = linear_interpolate(FIRE_PALETTE.colors, rect.height // zoom)
        self.zoom = zoom
        self.rect = rect
        self.matrix = np.zeros((rect.width // zoom, rect.height // zoom), dtype=np.uint8)
        self.frame_counter = 0
        n = 1 / 12.5
        self.kernel = np.array(
            [[0, 0, 0],
             [n, 0, n],
             [n, 8*n, n]])
        self.kernel = np.flipud(self.kernel)
        #self.kernel = np.fliplr(self.kernel)
        self.kernel = self.kernel.T

    def render(self):
        for y in range(self.matrix.shape[1]):
            for x in range(self.matrix.shape[0]):
                value = int(self.matrix[x, y])
                value = max(0, min(value, len(self.palette)-1))

                pygame.draw.rect(
                    self.game.screen,
                    self.palette[value],
                    (self.rect.x + x*self.zoom, self.rect.y + y*self.zoom, self.zoom, self.zoom))

    def update_fuel(self):
        for x in range(self.matrix.shape[0]):
            self.matrix[x, self.matrix.shape[1] - 1] = (random.randint(0, 10) < 5) * (len(self.palette) - 1)

    def update_fire_scipy(self):
        self.matrix = scipy.signal.convolve2d(self.matrix, self.kernel, mode='same', boundary='fill', fillvalue=0)

    def update_fire(self):
        for y in range(self.matrix.shape[1] - 1):
            for x in range(1, self.matrix.shape[0]):
                tmatrix = self.matrix[x - 1:x + 2, y:y + 3]
                tmean = np.mean(tmatrix)
                #tmean = math.pow(np.mean(tmatrix**1.8), 1/1.8)
                self.matrix[x, y] = int(tmean)

    def tick(self):
        #self.update_fire_scipy()
        self.update_fire()
        self.update_fuel()


def firedemo():
    game = Game((1920,1080))
    pygame.display.toggle_fullscreen()
    background = Background(game, (0, 0, 0x11))
    game.renderers.append(background.render)

    toggle_fullscreen = Debounce(game, pygame.K_F10, pygame.display.toggle_fullscreen)
    game.tickers.append(toggle_fullscreen.tick)

    fps = FPSCounter(game, pygame.font.SysFont("Noto sans", 20))
    game.tickers.append(fps.tick)
    game.renderers.append(fps.render)

    zoom = 20
    fire_height = game.screen.get_height() - game.screen.get_height() // 10
    burn_area = pygame.Rect(
        0,
        game.screen.get_height() - fire_height,
        game.screen.get_width() - 0,
        fire_height
    )
    fire = Fire(game, zoom, burn_area)
    game.tickers.append(fire.tick)
    game.renderers.append(fire.render)

    game.run()