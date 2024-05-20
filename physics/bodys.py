import math
import sys

from physics.vector import *

def rot_center(image, angle, x, y):
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

class Shape(enumerate):
    CIRCLE = 0
    BOX = 1

class Body():
    def __init__(self, screen, position : Vector, mass : float, 
                 restitution : float, radius : float, width : float, 
                 height : float, shape_type : Shape, texture: str, is_static = False) -> None:
        #Screen of the shape
        self.screen = screen

        #All shape elements
        self.radius = radius
        self.width = width
        self.height = height
        self.shape_type = shape_type
        self.color = (255, 0, 0)
        if texture != None:
            self.texture_file = texture
            self.texture = pygame.image.load(texture)
        else:
            self.texture_file = None
            self.texture = None
        self.pygame_shape = None

        #All important value of the shape
        self.mass = mass
        self.restitution = restitution
        self.static_friction = .5
        self.dynamic_friction = .3

        #Everything concerning movement
        self.position = position
        self.linear_velocity = Vector(0, 0)
        self.angle = 0
        self.angular_velocity = 0
        self.force = Vector(0, 0)

        #Everything Shape specific data
        #set vertices only for rectangle
        #set proper inertia for each shape type
        if shape_type == Shape.BOX:
            self.vertices = self.create_vertices()
            self.trans_vertices = self.update_transform()
            self.inertia = (1 / 12) * self.mass * (self.height**2 + self.width**2)
            if self.texture != None:
                self.texture = pygame.transform.scale(self.texture, (self.texture.get_width(), self.texture.get_height()))
        else:
            self.vertices = None
            self.trans_vertices = None
            self.inertia = (1 / 2) * self.mass * self.radius**2
            if self.texture != None:
                self.texture = pygame.transform.scale(self.texture, (self.texture.get_width() / 1.8, self.texture.get_height() / 1.8))


        self.bounding_box = self.update_bounding_box()

        #set inverse mass and inertia based on
        #if body is static or dynamic
        self.is_static = is_static
        if is_static:
            self.inverse_mass = 0
            self.inverse_inertia = 0
        else:
            self.inverse_mass = 1 / mass
            self.inverse_inertia = 1 / self.inertia

        # All variable needed for the game
        self.selected = False
        self.offset = None
        self.freezed = False

    def draw(self):
        if self.shape_type == Shape.CIRCLE:
            self.pygame_shape = pygame.draw.circle(self.screen, self.color, toCoord(self.position), self.radius)
            #Draw texture (static)
            if self.texture != None:
                body_coord = toCoord(self.position)
                self.screen.blit(self.texture, (body_coord[0] - self.radius*1.4, body_coord[1] - self.radius*1.5))

        elif self.shape_type == Shape.BOX:
            self.pygame_shape = pygame.draw.polygon(self.screen, self.color, [toCoord(self.trans_vertices[0]), 
                                                                              toCoord(self.trans_vertices[1]),
                                                                              toCoord(self.trans_vertices[2]),
                                                                              toCoord(self.trans_vertices[3])])
            if self.texture != None:
                texture, rect = rot_center(self.texture, -math.degrees(self.angle), self.position.x, self.position.y)
                self.screen.blit(texture, rect)
                #(body_coord[0] - self.width / 2 - 2, body_coord[1] - self.height / 2 - 2)
        #FOR DEBUG !!!
        #Draw bounding box opposite points
        # pygame.draw.circle(self.screen, (255, 0, 0), toCoord(self.bounding_box[0]), 5)
        # pygame.draw.circle(self.screen, (255, 0, 0), toCoord(self.bounding_box[1]), 5)


    def create_vertices(self):
        left = - self.width / 2
        right = left + self.width
        bottom = - self.height / 2
        top = bottom + self.height

        vertices = [
            Vector(left, top),
            Vector(right, top),
            Vector(right, bottom),
            Vector(left, bottom)
            ]
        
        return vertices
    
    def update_bounding_box(self):
        min = Vector(sys.float_info.max, sys.float_info.max)
        max = Vector(sys.float_info.min, sys.float_info.min)

        if self.shape_type == Shape.BOX:
            for i in range(len(self.trans_vertices)):
                vertice = self.trans_vertices[i]

                if vertice.x < min.x:
                    min.x = vertice.x
                if vertice.x > max.x:
                    max.x = vertice.x
                if vertice.y < min.y:
                    min.y = vertice.y
                if vertice.y > max.y:
                    max.y = vertice.y
        else:
            min.x = self.position.x - self.radius
            min.y = self.position.y - self.radius
            max.x = self.position.x + self.radius
            max.y = self.position.y + self.radius

        self.bounding_box = (min, max)
        
        return self.bounding_box


    def update_transform(self):

        temp_list = []

        for vertice in self.vertices:
            temp_list.append(Transform(vertice, self.position, self.angle))
        
        self.trans_vertices = temp_list
        
        return self.trans_vertices

    def update_pos(self, vect: Vector):
        self.position = self.position + vect
    
    def set_pos(self, vect: Vector):
        self.position = vect

    def set_color(self, color: tuple):
        self.color = color

    def rotate(self, amount):
        self.angle += amount
        if self.shape_type == Shape.BOX:
            self.update_transform()
        self.update_bounding_box()
    
    def rotate_degree(self, amount):
        self.angle += math.radians(amount)
        if self.shape_type == Shape.BOX:
            self.update_transform()
        self.update_bounding_box()

    def add_force(self, amount: Vector):
        self.force = amount

    def step(self, dt, gravity):

        if self.is_static:
            return
        if not self.freezed:
        
            self.linear_velocity += gravity * dt * 80
            
            self.linear_velocity += self.force / self.mass * dt * 80
            self.force = Vector(0, 0)

            self.position += self.linear_velocity * dt
            self.angle += self.angular_velocity * dt

        if self.shape_type == Shape.BOX:
            self.update_transform()
        self.update_bounding_box()

    #################################################
    #All function under here are purely for the game#
    #################################################

    def check_selected(self, mouse_pos):
        """check if the item is selected, if it is, 
        we move it to the mouse cursor"""
        if self.selected:   
            #setting position of the object with mouse pose with the offset added 
            self.position = Vector(mouse_pos[0] + self.offset[0], mouse_pos[1] + self.offset[1])
            self.linear_velocity = Vector(0, 0)
            self.angular_velocity = 0

    def check_clicked(self, mouse_pos):
        if self.pygame_shape.collidepoint(mouse_pos[0], mouse_pos[1]):
            return True
        return False
    
    def toggle_selected(self, mouse_pos = None):
        """toggle selected state (being able to drag the piece or not)"""
        if self.selected:
            self.selected = False
            self.offset = (0, 0)
        else:
            self.selected = True
            actual_pos = toCoord(self.position)
            #set an offset to move the object with cursor exactly where u clicked
            x_offset = actual_pos[0] - mouse_pos[0]
            y_offset = actual_pos[1] - mouse_pos[1]
            self.offset = (x_offset, y_offset)
    
    def toggle_freeze(self):
        if self.freezed:
            self.freezed = False
        else:
            self.freezed = True



class CircleBody():
    def __init__(self, screen, position : Vector, density : float, 
                 restitution : float, radius : float, texture : str, is_static = False) -> None:
        self.density = density

        area = radius**2 * math.pi
        mass = area * density

        self.body = Body(screen, position, mass, restitution, 
                         radius, 0, 0, Shape.CIRCLE, texture, is_static)



class BoxBody():
    def __init__(self, screen, position : Vector, density : float, 
                 restitution : float , width : float, height : float, texture : str, is_static = False) -> None:
        self.density = density
        
        area = width * height
        mass = area * density

        self.body = Body(screen, position, mass, restitution, 
                         0, width, height, Shape.BOX, texture, is_static)

