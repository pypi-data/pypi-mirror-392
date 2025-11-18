# Example file showing a circle moving on screen
import datetime
import math
import random
from contextlib import AbstractContextManager
from copy import copy
from dataclasses import dataclass
from statistics import mean

import scipy.signal
from scipy.signal import convolve2d

import pygame
from gameutils import Movement

import numpy as np









def main_game_just_move_about():
    game = Game()

    player_movement = Movement(
        game,
        speed_px_per_second=1000,
        initial_position=(game.screen.get_width() // 2, game.screen.get_height() // 2),
        screen_bounds=(0, 0, game.screen.get_width(), game.screen.get_height())
    )

    class Player(GameElement):
        def tick(self):
            player_movement.tick()
        def render(self):
            pygame.draw.circle(game.screen, "cyan", player_movement.position, 3)

    game.game_elements.append(Background(game, "black"))
    game.game_elements.append(Player())
    game.run()




if __name__ == "__main__":
    #main_game_just_move_about()
    #main_game_etch_a_sketch()
    main_game_palette_demo()
    main_fire_demo()