from copy import copy
from datetime import datetime

import click
import pygame

from ratisbona_pygames.gameutils import GameElement, Movement, Game, Debounce, Popup, FPSCounter, Background, Help, KeyHelp, to_helptext


class EtchASketch(GameElement):

    def __init__(self, game, screen, speed=100):
        self.lastpos = None
        self.game = game
        self.screen = screen
        self.erase_mode = False
        self.movement = Movement(
            self.game,
            speed_px_per_second=speed,
            initial_position=(screen.get_width() // 2, screen.get_height() // 2),
            screen_bounds=(0, 0, screen.get_width(), screen.get_height()),
        )

    def render(self):
        self.game.screen.blit(self.screen, (0, 0))
        if self.erase_mode:
            pygame.draw.rect(self.game.screen, "red", pygame.Rect(self.movement.position, (10, 10)))
        else:
            upper = self.movement.position + pygame.Vector2(0, -10)
            lower = self.movement.position + pygame.Vector2(0, 10)
            left = self.movement.position + pygame.Vector2(-10, 0)
            right = self.movement.position + pygame.Vector2(10, 0)
            pygame.draw.line(self.game.screen, "red", upper, lower)
            pygame.draw.line(self.game.screen, "red", left, right)

    def tick(self):
        self.lastpos = copy(self.movement.position)
        self.movement.tick()
        if self.game.keys[pygame.K_SPACE]:
            pygame.draw.line(self.screen, "green", self.lastpos, self.movement.position)
        self.erase_mode = self.game.keys[pygame.K_r]
        if self.erase_mode:
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(self.movement.position, (10, 10)))


@click.command()
def main_game_etch_a_sketch():
    game = Game()
    font = pygame.font.SysFont("Noto sans", 20)
    helptexts = []


    etch = EtchASketch(game, pygame.Surface(game.screen.get_size()), 200)
    etch.screen.set_colorkey((0, 0, 0))

    class Halfspeed:

        def render(self):
            pass

        def tick(self):
            if game.keys[pygame.K_LSHIFT]:
                etch.movement.speed_px_per_second = 100
            elif game.keys[pygame.K_RSHIFT]:
                etch.movement.speed_px_per_second = 50
            else:
                etch.movement.speed_px_per_second = 200

    toggle_fullscreen = Debounce(game, pygame.K_F10, pygame.display.toggle_fullscreen)
    popup = Popup(game, 2, font)

    def save_function():
        filename = "drawing_" + datetime.now().isoformat().replace(':', '-') + ".png"
        pygame.image.save(etch.screen, filename)
        popup.trigger(f'Saved: {filename}')

    save_action = Debounce(game, pygame.K_s, save_function)
    clear_action = Debounce(game, pygame.K_c, lambda: etch.screen.fill((0, 0, 0)))
    fps_counter = FPSCounter(game, font)
    hints= [
        KeyHelp("Arrow Keys", "Move Cursor"),
        KeyHelp("Space", "Draw"),
        KeyHelp("LShift", "Half Speed"),
        KeyHelp("RShift", "Quarter Speed"),
        KeyHelp("S", "Save Drawing"),
        KeyHelp("R", "Rubber"),
        KeyHelp("C", "Clear Drawing"),
        KeyHelp("F1", "This Help"),
        KeyHelp("F10", "Toggle Fullscreen")
    ]

    help = Help(game, font, to_helptext(hints))

    game.game_elements.extend([
        Background(game, "black"),
        help,
        fps_counter,
        Halfspeed(),
        etch,
        popup,
        toggle_fullscreen,
        save_action,
        clear_action,
    ])
    game.run()