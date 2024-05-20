import pygame

from physics.vector import *
from physics.bodys import *
from physics.space import *
from gamemode.level_creator import *
from utils.game import *
from gamemode.play import *

import utils.menus as menus

#Some constant used for the game
WIDTH = 1300
HEIGHT = 700
FPS = 144

def set_level_maker_mode(game : Game):
    game.set_gamemode(LevelMakerMode(game))
    game.add_menu(menus.EditMenu(game))

def set_play_mode(game : Game):
    game.clear_menu()
    game.set_gamemode(PlayMode(game))

def menu_loop(game):
    background = pygame.image.load("resources/textures/background.png")
    game.screen.blit(background, (0, 0))

    return True




if __name__ == "__main__":
    run = True

    on_main_menu = False

    game = Game(WIDTH, HEIGHT, FPS)

    #set_level_maker_mode(game)
    set_play_mode(game)
    game_mode = game.active_gamemode

    game.draw_walls()
    

    #main loop for pygame
    while run:
        if on_main_menu:
            on_main_menu = menu_loop(game)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
        else:
            #draw game and update gamemode modification on screen
            game.draw()
            game_mode.update()
        
            #event handler for pygame
            for event in pygame.event.get():
    
                if event.type == pygame.QUIT:
                    run = False
                else:
                    mouse_pos = pygame.mouse.get_pos()
                    game.check_event()
                    game_mode.event_handler(event)

        pygame.display.flip()
    pygame.quit()