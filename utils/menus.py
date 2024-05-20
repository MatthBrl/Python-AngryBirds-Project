import pygame
import json
import os

import utils.buttons as buttons

from tkinter import filedialog

def load_game_level(game):
    filepath = filedialog.askopenfile(initialdir=".\\saved_level", filetypes=[("Json File", "*.json")])
    if filepath is not None:
        game.load_level(filepath.name, clear = True, freezed=True)

def save_game_level(game):
    filepath = filedialog.asksaveasfile(initialdir=".\\saved_level", filetypes=[("Json File", "*.json")],
                                        defaultextension=".json", initialfile="level.json")
    if filepath is not None:
        game.save_level(filepath.name)

def set_move_mode(game):
    game.set_gamemode_mode("move")
    game.remove_menu(PlaceMenu)
    game.draw()

def set_place_mode(game):
    if game.active_gamemode.mode != "place":
        game.add_menu(PlaceMenu(game))
    game.set_gamemode_mode("place")
    game.draw()

def set_delete_mode(game):
    game.set_gamemode_mode("delete")
    game.remove_menu(PlaceMenu)
    game.draw()

class EditMenu():
    """Create a menu with utility button as place, delete, clear, load, save"""
    def __init__(self, game) -> None:
        self.game = game
        self.screen = game.screen
        self.space = game.space

        #adding buttons to the menu
        y_coord = (self.screen.get_height() - 7 * 32 - 6 * 20) // 2
        self.buttons = [
            buttons.UtilityButton("freeze", self.game, lambda: self.space.toggle_freeze_space(), (self.screen.get_width() - 52, y_coord), 
                                  "resources/textures/icons/freeze_icon.png"),

            buttons.UtilityButton("move", self.game, lambda: set_move_mode(self.game), (self.screen.get_width() - 52, y_coord + 32 + 20), 
                                  "resources/textures/icons/move_icon.png"),

            buttons.UtilityButton("place", self.game, lambda: set_place_mode(self.game), (self.screen.get_width() - 52, y_coord + 32 * 2 + 20 * 2), 
                                  "resources/textures/icons/place_icon.png"),

            buttons.UtilityButton("delete", self.game, lambda: set_delete_mode(self.game), (self.screen.get_width() - 52, y_coord + 32 * 3 + 20 * 3), 
                                  "resources/textures/icons/delete_icon.png"),

            buttons.UtilityButton("clear", self.game, lambda: self.game.clear_items(), (self.screen.get_width() - 52, y_coord + 32 * 4 + 20 * 4), 
                                  "resources/textures/icons/clear_icon.png", toggable=False),

            buttons.UtilityButton("load", self.game, lambda: load_game_level(self.game), (self.screen.get_width() - 52, y_coord + 32 * 5 + 20 * 5), 
                                  "resources/textures/icons/load_icon.png", toggable=False),

            buttons.UtilityButton("save", self.game, lambda: save_game_level(self.game), (self.screen.get_width() - 52, y_coord + 32 * 6 + 20 * 6), 
                                  "resources/textures/icons/save_icon.png", toggable=False)
        ]
        self.buttons[1].set_selected(True)

    def draw(self):
        """Draw all buttons from the menu"""
        for button in self.buttons:
            button.draw()
    
    def check_event(self):
        """Check event for each buttons"""
        for button in self.buttons:
            check = button.check_clicked()
            #if button clicked
            if check:
                if button.name == "place":
                    self.buttons[3].set_selected(False)
                    self.buttons[1].set_selected(False)
                elif button.name == "delete":
                    self.buttons[1].set_selected(False)
                    self.buttons[2].set_selected(False)
                elif button.name == "move":
                    self.buttons[2].set_selected(False)
                    self.buttons[3].set_selected(False)

                return button
        return False

class PlaceMenu():
    """Create a place menu, purpose of this menu is to place new item on the level"""
    def __init__(self, game) -> None:
        self.game = game
        self.screen = game.screen
        self.space = game.space
        self.buttons = []

        self.toggle_button = buttons.UtilityButton("toggle_menu", self.game, lambda: self.toggle_menu(), (530, self.screen.get_height() // 2 - 64 // 2), 
                                                   ".\\resources\\textures\\icons\\menu_side_button.png", toggable= False)
        self.opened = True

        line = 0
        column = 0
        pos_x = 25
        pos_y = 25

        #create a button for each file in "objects/"
        for file in os.listdir("objects/"):
            print(file)
            opened_file = open(f"objects/{file}", encoding="utf-8")
            content_json = json.loads(opened_file.read())
            print(content_json)

            obj_button = buttons.ObjectButton(self.game, content_json["name"], content_json, (pos_x, pos_y), content_json["texture"], (42, 42, 42), 150)
            self.buttons.append(obj_button)
            column += 1
            pos_x += 106 + 17

            if column == 4:
                pos_y += 150
                pos_x = 25
                line += 1
                column = 0

    def toggle_menu(self):
        """Toggle the place menu"""
        actual_pos = self.toggle_button.get_pos()
        if self.opened:
            self.opened = False
            self.toggle_button.set_pos(0, actual_pos[1])
        else:
            self.opened = True
            self.toggle_button.set_pos(530, actual_pos[1])

    def draw(self):
        """Draw the place menu (buttons, background)"""
        if self.opened:
            image = pygame.image.load("resources/textures/menus/item_selector_background.png")
            self.screen.blit(image, (0, 0))

            for button in self.buttons:
                button.draw()
        self.toggle_button.draw()
        
    
    def check_event(self):
        """Check event of all the buttons of the menu"""
        if self.opened:
            for button in self.buttons:
                check = button.check_clicked()
                if check:
                    obj = button.spawn_object()
                    return obj
        self.toggle_button.check_clicked()
        return False