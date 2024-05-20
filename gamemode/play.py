import pygame
import os

from physics.vector import *
from physics.bodys import *
from physics.collisions import *

class PlayMode():
    def __init__(self, game) -> None:
        self.game = game
        self.screen = game.screen
        self.space = game.space

        self.font = pygame.font.Font(".\\resources\\angrybirds-regular.ttf", 100)

        self.levels = []
        for filename in os.listdir("levels/"):
            file_dir = os.path.join("levels/", filename)
            # checking if it is a file
            if filename.endswith(".json"):
                self.levels.append(file_dir)
        print(self.levels)

        self.birds_count = 4
        self.birds_index = [0, 1, 2, 3]
        self.pig_index = []
        self.get_pig_index()

        self.default_bird_pos= Vector(0, 0)
        self.spawn_bird()

        self.launching = False
        self.win = False
        self.lose = False

        self.slingshot_coord = (175, 360)
        self.max_sling_radius = 70
        self.slingshot = None
        self.launching_velocity = Vector(0, 0)
        self.max_launching_velocity = Vector(0, 0)
        self.sling_cooldown = 0

        self.last_shot_cooldown = 0
        self.new_level_cooldown = 0
        self.new_level_needed = True

    def draw(self):
        #print(len(self.space.bodys))
        image = pygame.image.load("resources/textures/sling.png").convert_alpha()
        image = pygame.transform.scale(image, (image.get_width() / 1.5, image.get_height() / 1.5))
        self.screen.blit(image, self.slingshot_coord)

        x = 220
        y = 480
        
        if len(self.birds_index) > 0 and self.sling_cooldown == 0:
            for i in range(len(self.birds_index)):
                self.space.bodys[self.birds_index[i]].body.set_pos(Vector(x,y))
                x -= 40

        if self.launching:

            mouse_pos = pygame.mouse.get_pos()
            mouse_vect = Vector(mouse_pos[0], mouse_pos[1])
            sling_center_vect = Vector(180, 378)

            mouse_to_center = sling_center_vect - mouse_vect
            distance = getLength(mouse_to_center)

            if distance >= self.max_sling_radius:
                distance_normal = mouse_to_center / distance
                mouse_pos = toCoord(sling_center_vect - distance_normal * self.max_sling_radius)

            temp_vel = sling_center_vect - Vector(mouse_pos[0], mouse_pos[1])
            self.launching_velocity = Vector(temp_vel.x * 12, temp_vel.y * 12)

            points = [(180, 378), (180, 388), mouse_pos, (mouse_pos[0], mouse_pos[1] - 5)]
            pygame.draw.polygon(self.screen, (48, 22, 8), points)
            points = [(210, 379), (210, 387), mouse_pos, (mouse_pos[0], mouse_pos[1] - 5)]
            pygame.draw.polygon(self.screen, (48, 22, 8), points)
            self.space.bodys[self.birds_index[0]].body.set_pos(Vector(mouse_pos[0] + 15, mouse_pos[1] - 5))

        else:
            if len(self.birds_index) > 0 and self.sling_cooldown == 0:
                self.space.bodys[self.birds_index[0]].body.set_pos(Vector(200, 385))
                self.launching_velocity = Vector(0, 0)
        
        if self.sling_cooldown != 0:
            self.sling_cooldown -= 1

    def check_win(self):
        if self.pig_index == []:
            self.win = True
            self.new_level_cooldown = self.game.fps
            self.new_level_needed = True
            self.levels.pop(0)
        elif self.birds_index == []:
            if self.last_shot_cooldown == 0:
                self.lose = True
                self.new_level_cooldown = self.game.fps
                self.new_level_needed = True
            else:
                self.last_shot_cooldown -= 1
    
    def check_new_level_needed(self):
        if self.new_level_needed:
            if self.new_level_cooldown == 0:
                self.new_level_needed = False
                if self.levels != []:
                    self.load_level(self.levels[0])
            else:
                self.new_level_cooldown -= 1

    def check_collision(self):
        """Check collision between pig and bird"""
        for i in range(4):
            for j in range(len(self.pig_index) - 1):
                collide, normal, depth = Collide(self.space.bodys[self.pig_index[j]].body, self.space.bodys[i].body)
                if collide:
                    print("AHHHHHH")
                    self.space.remove_body(self.pig_index[j])
                    self.pig_index.pop(j)

    def spawn_bird(self):
        for i in range(self.birds_count):
            bird = CircleBody(self.screen, self.default_bird_pos, 2, 0.5, 14, "resources/textures/bird.png")
            bird.body.toggle_freeze()
            self.space.add_body(bird)

    def get_pig_index(self):
        self.pig_index.clear()
        for i in range(4, len(self.space.bodys)):
            if self.space.bodys[i].body.shape_type == Shape.CIRCLE:
                self.pig_index.append(i)

    def load_level(self, level):
        self.space.clear_space()
        self.birds_count = 4
        self.birds_index = [0, 1, 2, 3]
        self.lose = False
        self.win = False
        self.spawn_bird()
        self.game.draw_walls()
        self.game.load_level(level, clear=False)
        self.get_pig_index()


    def check_clicked(self, mouse_pos):
        if mouse_pos[0] > self.slingshot_coord[0] and mouse_pos[0] < self.slingshot_coord[0] + 70 and \
        mouse_pos[1] > self.slingshot_coord[1] and mouse_pos[1] < self.slingshot_coord[1] + 100:
            self.launching = True

    def update(self):
        self.draw()
        self.check_collision()
        self.get_pig_index()
        self.check_new_level_needed()
        if not self.win and not self.lose:
            self.check_win()
        if self.win:
            custom_text = self.font.render("Gagné !", True, (0, 255, 0))
            self.screen.blit(custom_text, (self.screen.get_width() / 2 - custom_text.get_width() / 2 , self.screen.get_height() / 2 - custom_text.get_height() / 2))
        if self.lose:
            custom_text = self.font.render("Perdu !", True, (255, 0, 0))
            self.screen.blit(custom_text, (self.screen.get_width() / 2 - custom_text.get_width() / 2 , self.screen.get_height() / 2 - custom_text.get_height() / 2))
        
    def event_handler(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        #if left mouse button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN: 

            if event.button == 1 and self.birds_count != 0:
                self.check_clicked(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.launching:
                
                index = self.birds_index.pop(0)
                self.birds_count -= 1

                self.space.bodys[index].body.toggle_freeze()
                self.space.bodys[index].body.linear_velocity = self.launching_velocity
                self.sling_cooldown = self.game.fps

                self.launching = False

                if self.birds_count == 0:
                    self.last_shot_cooldown = self.game.fps * 3
        