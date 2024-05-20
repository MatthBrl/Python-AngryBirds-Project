import pygame
import json
import time

import gamemode.level_creator as gamemode
import utils.objects as objects

from physics.space import *

class Game():
    def __init__(self, width, height, fps) -> None:
        """Create a new game (pygame screen and space)"""
        #initialize new pygame windows and new pymunk space
        self.fps = fps
        
        pygame.font.init()
        self.font = pygame.font.Font(".\\resources\\angrybirds-regular.ttf", 30)

        pygame.init()
        self.screen = pygame.display.set_mode(size=(width, height))
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.last_time = time.time()

        self.space = Space(self.screen)

        #some useful data for later
        self.active_menus = []
        self.active_gamemode = None

        self.is_running = True

    def set_gamemode(self, gamemode):
        """Set an active gamemode to the game"""
        self.active_gamemode = gamemode
    
    def set_gamemode_mode(self, mode):
        """Set the mode of the active gamemode"""
        self.active_gamemode.set_mode(mode)

    def add_menu(self, menu):
        """Add menu to the active menus list"""
        self.active_menus.append(menu)

    def clear_menu(self):
        """Clear actice menus list"""
        self.active_menus.clear()

    def add_item(self, item):
        """Add an item to the space"""
        self.space.add_body(item)

    def remove_item(self, index):
        """Remove an item from the space"""
        self.space.remove_body(index)
    
    def remove_menu(self, menu_type):
        """Remove menus that are same type as menu_type"""
        index = 0
        for menu in self.active_menus:
            if type(menu) == menu_type:
                self.active_menus.pop(index)
            index += 1

    def clear_items(self):
        """Clear all items from the space except walls"""
        index = 4
        items_number = len(self.space.bodys)
        while index < items_number:
            self.space.remove_body(items_number - 1)
            items_number -=1

    def draw_walls(self):
        self.clear_items()
        walls = [
            BoxBody(self.screen, Vector(-6, self.screen.get_height() / 2), 2.0, 0.5, 10, self.screen.get_height(), None, True), #left
            BoxBody(self.screen, Vector(self.screen.get_width() / 2, -6), 2.0, 0.5, self.screen.get_width(), 10, None, True), #top
            BoxBody(self.screen, Vector(self.screen.get_width() / 2, self.screen.get_height() - 103), 2.0, 0.5, self.screen.get_width(), 205, None, True), #bottom
            BoxBody(self.screen, Vector(self.screen.get_width() + 5, self.screen.get_height() / 2), 2.0, 0.5, 10, self.screen.get_height(), None, True) #right
        ]
        walls[2].body.set_color((163, 181, 50))
        i = 0
        for wall in walls:
            self.space.add_body(wall)
            i += 1

    def save_level(self, dir):
        """Save level in the directory given"""
        json_level = {"items": []}
        #add all items to our list
        for item in self.space.bodys:
            if item.body.is_static:
                continue
            item_info = {
                "type": item.body.shape_type,
                "pos": toCoord(item.body.position),
                "rotation": math.degrees(item.body.angle),
                "density": item.density,
                "restitution": item.body.restitution,
                "texture": item.body.texture_file,
                "color": item.body.color
            }
            if item.body.shape_type == Shape.CIRCLE:
                item_info["radius"] = (item.body.radius)
            else:
                item_info["dimension"] = (item.body.width, item.body.height)

            json_level["items"].append(item_info)

        #save the file of the level
        with open(dir, "w") as outfile:
            outfile.write(json.dumps(json_level, indent=4))
            outfile.close()
        print(len(self.space.bodys))

    def load_level(self, level, clear = False, freezed = False):
        """Load a level from a json file"""
        if clear:
            self.space.clear_space()
            self.draw_walls()

        #open file given
        with open(level, "r") as file:
            json_level = json.loads(file.read())

        #add each item of the file in the space
        for item in json_level["items"]:
            pos = Vector(item["pos"][0], item["pos"][1])
            
            new_item = None
            if item["type"] == Shape.BOX:
                width = item["dimension"][0]
                height = item["dimension"][1]
                new_item = BoxBody(self.screen, pos, item["density"], item["restitution"], width, height, item["texture"])
            else:
                new_item = CircleBody(self.screen, pos, item["density"], item["restitution"], item["radius"], item["texture"])
            new_item.body.set_color(item["color"])
            new_item.body.rotate_degree(item["rotation"])
            self.add_item(new_item)
            if freezed:
                new_item.body.toggle_freeze()

    def draw(self):
        """Draw main windows of the game and menus in active menus list"""
        #self.screen.fill((220, 220, 220))
        background = pygame.image.load("resources/textures/background.png")
        # background = pygame.transform.scale(background, (background.get_width() / 1.2, background.get_height() / 1.2))
        self.screen.blit(background, (0, 0))

        current_time = time.time()
        self.dt = current_time - self.last_time
        self.last_time = current_time
        self.clock.tick(self.fps)
        
        self.space.step(self.dt, 8)
        
        pygame.display.set_caption(f"{self.clock.get_fps()} FPS")

        for menu in self.active_menus:
            menu.draw()
        # self.gamemode.draw()
        # self.active_menu.draw()
    
    def check_event(self):
        """Check event for each menus in the active menus list"""
        for menu in self.active_menus:
            menu.check_event()
