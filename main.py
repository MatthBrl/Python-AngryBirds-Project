import pygame

from gamemode.level_creator import *
from utils.game import *
from gamemode.play import *
from utils.buttons import MenuButton

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

def menu_loop(game : Game):
    background = pygame.image.load("resources/textures/background.png")
    game.screen.blit(background, (0, 0))

    play_button = MenuButton(game, (WIDTH / 2 - 310 / 2, HEIGHT / 2 - 109 / 2), "resources/textures/icons/play_button.png")
    play_button.draw()
    is_clicked = play_button.check_clicked()
    if is_clicked:
        set_play_mode(game)
        return False, game.active_gamemode
    
    create_button = MenuButton(game, (WIDTH / 2 - 310 / 2, HEIGHT / 2 - 109 / 2 + 140), "resources/textures/icons/create_button.png")
    create_button.draw()
    is_clicked = create_button.check_clicked()
    if is_clicked:
        set_level_maker_mode(game)
        return False, game.active_gamemode

    return True, None




if __name__ == "__main__":
    run = True

    on_main_menu = True

    game = Game(WIDTH, HEIGHT, FPS)

    ##################################################
    #EDIT THIS IF U WANT TO LAUNCH LEVEL MAKER MODE

    #set_level_maker_mode(game)
    #set_play_mode(game)

    ####################################################
    game_mode = None
    game.draw_walls()
    
    #main loop for pygame
    while run:
        if on_main_menu:
            on_main_menu, game_mode = menu_loop(game)

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