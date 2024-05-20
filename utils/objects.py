import pymunk
import math

class DynamicSquareObject():
    def __init__(self, screen, space, pos, dimension, mass, elasticity, friction, color) -> None:
        self.screen = screen
        self.space = space
        self.pos = pos
        self.dimension = dimension
        self.elasticity = elasticity
        self.friction = friction
        self.mass = mass
        self.color = color
        self.selected = False
        self.offset = (0, 0)
        self.freezed = False
        self.disable = False

        #initialize the object in the space
        self.body = pymunk.Body()
        self.body.position = self.pos
        shape = pymunk.Poly.create_box(self.body, self.dimension)
        shape.mass = self.mass
        shape.friction = self.friction
        shape.elasticity = self.elasticity
        shape.color = self.color
        self.shape = shape

    def draw(self):
        self.space.add(self.body, self.shape)
        return self.shape

    def set_speed(self, x, y):
        """set speed of the object in x and y direction"""
        self.body.velocity = (x, y)

    def check_selected(self, mouse_pos):
        """check if the item is selected, if it is, 
        we move it to the mouse cursor"""
        if self.selected:   
            #setting position of the object with mouse pose with the offset added 
            self.body.position = (mouse_pos[0] + self.offset[0], mouse_pos[1] + self.offset[1])
            self.body.velocity = (0, 0)
    
    def rotate(self, degree):
        """rotate the object with the angle gived"""
        self.body.angle += math.radians(degree)

    def toggle_freeze(self):
        """toggle freeze state (affected by gravity or not)"""
        if self.freezed:
            self.body.body_type = pymunk.Body.DYNAMIC
            self.freezed = False
        else:
            self.body.body_type = pymunk.Body.STATIC
            self.freezed = True

    def toggle_selected(self, mouse_pos = None):
        """toggle selected state (being able to drag the piece or not)"""
        if self.selected:
            self.selected = False
            self.offset = (0, 0)
        else:
            self.selected = True
            actual_pos = self.body.position
            #set an offset to move the object with cursor exactly where u clicked
            x_offset = actual_pos[0] - mouse_pos[0]
            y_offset = actual_pos[1] - mouse_pos[1]
            self.offset = (x_offset, y_offset)
        
    def get_speed(self):
        """return speed of the item (x and y axis)"""
        return self.body.velocity
    
    def get_pos(self):
        """return actual position of the item"""
        return self.body.position
    
    def get_rotation(self):
        """return actual rotation of the item (in degree)"""
        return math.degrees(self.body.angle)
    
    def get_dimension(self):
        """return dimension of the item"""
        return self.dimension
    
    def get_mass(self):
        """return mass of the item"""
        return self.mass

    def get_elasticity(self):
        """return elasticity of the item"""
        return self.elasticity
    
    def get_friction(self):
        """return friction of the item"""
        return self.friction
    
    def get_color(self):
        """return color of the item"""
        return self.color

class StaticSquareObject():
    def __init__(self, screen, space, pos, dimension, elasticity, friction, color) -> None:
        self.screen = screen
        self.space = space
        self.pos = pos
        self.dimension = dimension
        self.x_pos = self.pos[0]
        self.y_pos = self.pos[1]
        self.width = self.dimension[0]
        self.height = self.dimension[0]
        self.elasticity = elasticity
        self.friction = friction
        self.color = color
        self.selected = False

    def draw(self):
        """spawn the object in its self space"""
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = self.pos
        shape = pymunk.Poly.create_box(body, self.dimension)
        shape.color = (0, 0, 255, 100)
        shape.elasticity = self.elasticity
        shape.friction = self.friction
        self.space.add(body, shape)
        return shape