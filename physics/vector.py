import math
import pygame

class Vector():
    def __init__(self, x : float, y : float) -> None:
        self.x = x
        self.y = y

    #Operator Overload
    def __add__(self, vect : "Vector") -> "Vector":
        return Vector(self.x + vect.x, self.y + vect.y)
    
    def __iadd__(self, vect : "Vector") -> "Vector":
        if isinstance(vect, Vector):
            return Vector(self.x + vect.x, self.y + vect.y)
        return Vector(self.x + vect, self.y + vect)
    
    def __sub__(self, vect : "Vector") -> "Vector":
        if isinstance(vect, Vector):
            return Vector(self.x - vect.x, self.y - vect.y)
        return Vector(self.x - vect, self.y - vect)
    
    def __isub__(self, vect : "Vector") -> "Vector":
        if isinstance(vect, Vector):
            return Vector(self.x - vect.x, self.y - vect.y)
        return Vector(self.x - vect, self.y - vect)
    
    def __mul__(self, val : float) -> "Vector":
        if isinstance(val, Vector):
            return Vector(self.x * val.x, self.y * val.y)
        return Vector(self.x * val, self.y * val)
    
    def __truediv__(self, val) -> "Vector":
        if isinstance(val, Vector):
            return Vector(self.x / val.x, self.y / val.y)
        return Vector(self.x / val, self.y / val)
    
    def __eq__(self, vect : "Vector") -> bool:
        if self.x == vect.x and self.y == vect.y:
            return True
        return False
    
    def __neg__(self) -> "Vector":
        return Vector(-self.x,  -self.y)
    

def toCoord(vect : Vector) -> tuple:
        return (vect.x, vect.y)
    
def toString(vect : Vector) -> str:
    return f"({vect.x}, {vect.y})"

def getLengthSquared(vect : Vector) -> float:
    return vect.x**2 + vect.y**2

def getLength(vect : Vector) -> float:
    return math.sqrt(vect.x**2 + vect.y**2)

def getDistanceSquared(vect1 : Vector, vect2 : Vector) -> float:
    dx = vect1.x - vect2.x
    dy = vect1.y - vect2.y
    return dx**2 + dy**2

def getDistance(vect1 : Vector, vect2 : Vector) -> float:
    dx = vect1.x - vect2.x
    dy = vect1.y - vect2.y
    return math.sqrt(dx**2 + dy**2)

def Normalize(vect : Vector) -> Vector:
    length = getLength(vect)
    x = vect.x / length
    y = vect.y / length
    return Vector(x, y)

def Transform(vect1 : Vector, vect2 : Vector, angle) -> Vector:

    # Formule de rotation d'un vecteur
    rotate_x = math.cos(angle) * vect1.x - math.sin(angle) * vect1.y
    rotate_y = math.sin(angle) * vect1.x + math.cos(angle) * vect1.y

    transform_x = rotate_x + vect2.x
    transform_y = rotate_y + vect2.y

    return Vector(transform_x, transform_y)


def Dot(vect1 : Vector, vect2 : Vector) -> float:
    return vect1.x * vect2.x + vect1.y * vect2.y

def Cross(vect1: Vector, vect2: Vector) -> Vector:
    return vect1.x * vect2.y - vect1.y * vect2.x

def nearEqualVect(vect1 : Vector, vect2 : Vector) -> bool:
    
    return nearEqual(vect1.x, vect2.x) and nearEqual(vect1.y, vect2.y)

def nearEqual(a : float, b : float) -> bool:
    
    diff = abs(a - b)

    return diff < 0.0005