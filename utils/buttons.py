import pygame

from physics.bodys import *
from physics.vector import *

class ObjectButton():
    """Create a new button that can spawn items"""
    def __init__(self, game, text, object_settings, pos, image, color = (255, 0, 0), alpha = 255) -> None:
        self.game = game
        self.screen = game.screen
        self.space = game.space
        self.text = text
        self.object_settings = object_settings
        self.pos = pos
        self.image = image
        self.color = color
        self.alpha = alpha
        self.rect = None
        self.cooldown = 0

    def draw(self):
        """Draw a object selector button"""

        #draw image and clickable rect
        image = pygame.image.load(self.image)
        self.rect = pygame.draw.rect(self.screen, self.color, (self.pos[0], self.pos[1], 106, 106))
        self.screen.blit(image, (self.pos[0] + 106 // 2 - image.get_width() // 2, self.pos[1] + 106 // 2 - image.get_height() // 2 ))

        #draw text
        custom_font = self.game.font
        custom_text = custom_font.render(self.text, True, (255, 255, 255))
        self.screen.blit(custom_text, (self.pos[0] + 106//2 - custom_text.get_width() // 2, self.pos[1] + 106))

        if self.cooldown != 0:
            self.cooldown -= 1
    
    def check_clicked(self):
        """Return True if button clicked"""
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and self.cooldown == 0:
            self.cooldown = self.game.fps * 0.5
            return True
        return False
    
    def spawn_object(self):
        obj = None

        density = self.object_settings["density"]
        restitution = self.object_settings["restitution"]
        texture = self.object_settings["texture"]

        if self.object_settings["type"] == "BOX":
            width = self.object_settings["dimension"][0]
            height = self.object_settings["dimension"][1]

            obj = BoxBody(self.screen, Vector(self.screen.get_width() - 100, 100),  density, restitution, width, height, texture)
        else:
            radius = self.object_settings["radius"]

            obj = CircleBody(self.screen, Vector(self.screen.get_width() - 100, 100), density, restitution, radius, texture)

        obj.body.toggle_freeze()
        self.space.add_body(obj)
        return obj
    
class UtilityButton():
    """Create a new button that can do a specific action given in parameter"""
    def __init__(self, name, game, action, pos, image, toggable = True) -> None:
        self.name = name
        self.game = game
        self.screen = game.screen
        self.space = game.space
        self.action = action
        self.pos = pos
        self.image = image
        self.rect = None
        self.selected = False
        self.toggable = toggable
        self.cooldown = 0

    def set_selected(self, x):
        """set selected state"""
        self.selected = x

    def set_pos(self, x, y):
        """Set new pos of the button"""
        self.pos = (x, y)

    def get_pos(self):
        """Return actual pos of the button"""
        return self.pos

    def draw(self):
        """Draw a utility button"""

        image = pygame.image.load(self.image)

        #add a border around the image if it's selected
        if self.selected and self.toggable:
            pygame.draw.rect(self.screen, (255,0, 0), (self.pos[0] - 2, self.pos[1] - 2, image.get_width() + 4, image.get_height() + 4))

        #draw image and clickable rect
        self.rect = pygame.draw.rect(self.screen, (255, 0, 0), (self.pos[0], self.pos[1], image.get_width(), image.get_height()))
        self.screen.blit(image, self.pos)

        if self.cooldown != 0:
            self.cooldown -= 1
    
    def do_action(self):
        """Do the given action of the button"""
        self.action()

    def check_clicked(self):
        """Return True if button clicked"""
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and self.cooldown == 0:
            self.cooldown = self.game.fps * 0.5
            if not self.selected:
                self.selected = True
            self.do_action()
            return True
        return False