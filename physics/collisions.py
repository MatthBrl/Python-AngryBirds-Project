import sys

from physics.bodys import *
from physics.vector import *

def intersectBoundingBox(bounding_box_a, bounding_box_b):
    if bounding_box_a[1].x <= bounding_box_b[0].x or bounding_box_b[1].x <= bounding_box_a[0].x or \
       bounding_box_a[1].y <= bounding_box_b[0].y or bounding_box_b[1].y <= bounding_box_a[0].y:
        return False
    return True

def Collide(body_a, body_b):
        collision = False
        normal = Vector(0, 0)
        depth = 0

        if body_a.shape_type == Shape.BOX:

            if body_b.shape_type == Shape.BOX:
                collision, normal, depth = intersectPolygons(body_a.trans_vertices, body_b.trans_vertices)

            elif body_b.shape_type == Shape.CIRCLE:
                collision, normal, depth = intersectPolygonAndCircle(body_b.position, body_b.radius, 
                                                                     body_a.trans_vertices)
                if collision:
                    return (collision, -normal, depth)
            
        elif body_a.shape_type == Shape.CIRCLE:

            if body_b.shape_type == Shape.CIRCLE:
                collision, normal, depth = intersectCircles(body_a.position, body_a.radius, 
                                                            body_b.position, body_b.radius)

            elif body_b.shape_type == Shape.BOX:
                collision, normal, depth = intersectPolygonAndCircle(body_a.position, body_a.radius, 
                                                                     body_b.trans_vertices)
        
        return (collision, normal, depth)

def getContactPoints(body_a : Body, body_b : Body):
    point_1 = Vector(0, 0)
    point_2 = Vector(0, 0)
    nb_point = 0
    
    if body_a.shape_type == Shape.BOX:

        if body_b.shape_type == Shape.BOX:
            point_1, point_2, nb_point = contactPointPolygons(body_a.trans_vertices, body_b.trans_vertices)

        elif body_b.shape_type == Shape.CIRCLE:
            point_1 = contactPointCircleAndPolygon(body_b.position, body_b.radius, body_a.trans_vertices)
            nb_point = 1

    elif body_a.shape_type == Shape.CIRCLE:

        if body_b.shape_type == Shape.CIRCLE:
            point_1 = contactPointCircles(body_a.position, body_a.radius, body_b.position)
            nb_point = 1
        elif body_b.shape_type == Shape.BOX:
            point_1 = contactPointCircleAndPolygon(body_a.position, body_a.radius, body_b.trans_vertices)
            nb_point = 1
        
    return (point_1, point_2, nb_point)

def contactPointPolygons(poly_vertices_a : list[Vector], poly_vertices_b : list[Vector]):
    contact_point_1 = Vector(0, 0)
    contact_point_2 = Vector(0, 0)
    nb_point = 0

    min_distance_square = sys.float_info.max

    for i in range(len(poly_vertices_a)):

        point_a = poly_vertices_a[i]

        for j in range(len(poly_vertices_b)):
            vert_a = poly_vertices_b[j]
            vert_b = poly_vertices_b[(j + 1) % len(poly_vertices_b)]

            distance_square, contact = pointSegmentDistance(point_a, vert_a, vert_b)

            if nearEqual(distance_square, min_distance_square):
                
                if not nearEqualVect(contact, contact_point_1):
                    contact_point_2 = contact
                    nb_point = 2

            elif distance_square < min_distance_square:
                min_distance_square = distance_square
                contact_point_1 = contact
                nb_point = 1
        
    for i in range(len(poly_vertices_b)):

        point_b = poly_vertices_b[i]

        for j in range(len(poly_vertices_a)):
            vert_a = poly_vertices_a[j]
            vert_b = poly_vertices_a[(j + 1) % len(poly_vertices_a)]

            distance_square, contact = pointSegmentDistance(point_b, vert_a, vert_b)

            if nearEqual(distance_square, min_distance_square):
                
                if not nearEqualVect(contact, contact_point_1):
                    contact_point_2 = contact
                    nb_point = 2

            elif distance_square < min_distance_square:
                min_distance_square = distance_square
                contact_point_1 = contact
                nb_point = 1
        
    return (contact_point_1, contact_point_2, nb_point)
            



def contactPointCircles(center_a : Vector, radius_a : float, 
                        center_b : Vector):
    
    vect_AB = center_b - center_a
    normal = Normalize(vect_AB)
    contact_point = center_a + normal * radius_a
    return contact_point

def contactPointCircleAndPolygon(circle_center : Vector, circle_radius : float,
                                 poly_vertices : list[Vector]):
    
    poly_center = getCenter(poly_vertices)

    min_distance_square = sys.float_info.max
    contact_point = Vector(0, 0)

    for i in range(len(poly_vertices)):
        vertice_a = poly_vertices[i]
        vertice_b = poly_vertices[(i + 1) % len(poly_vertices)]

        distance_squared, contact = pointSegmentDistance(circle_center, vertice_a, vertice_b)

        if distance_squared < min_distance_square:
            min_distance_square =distance_squared
            contact_point = contact

    return contact_point

def pointSegmentDistance(point : Vector, line_a : Vector, line_b : Vector):
    contact = Vector(0, 0)

    vect_AB = line_b - line_a
    vect_AP = point - line_a

    proj = Dot(vect_AP, vect_AB)
    lenght_square_AB = getLengthSquared(vect_AB)
    d = proj / lenght_square_AB

    if d <= 0:
        contact = line_a
    elif d >= 1:
        contact = line_b
    else:
        contact = line_a + vect_AB * d

    distance_square = getDistanceSquared(point, contact)
    return distance_square, contact

    

def intersectPolygonAndCircle(circle_center : Vector, circle_radius : float, 
                              poly_vertices : list[Vector]):
    
    normal = Vector(0, 0)
    depth = sys.float_info.max

    # For all vertices of polygon
    for i in range(len(poly_vertices)):
        vect_a = poly_vertices[i]
        vect_b = poly_vertices[(i + 1) % len(poly_vertices)]

        edge = vect_b - vect_a
        axis = Vector(- edge.y, edge.x) #axis that test for separation
        axis = Normalize(axis)

        min_a, max_a = projectVertices(poly_vertices, axis)
        min_b, max_b = projectCircle(circle_center, circle_radius, axis)

        if min_a >= max_b or min_b >= max_a:
            return (False, None, None)
        
        min_depth = min(max_b - min_a, max_a - min_b)
        if min_depth < depth:
            depth = min_depth
            normal = axis
    
    point_index = getClosestPointPolygon(circle_center, poly_vertices)
    
    axis = poly_vertices[point_index] - circle_center
    axis = Normalize(axis)

    min_a, max_a = projectVertices(poly_vertices, axis)
    min_b, max_b = projectCircle(circle_center, circle_radius, axis)

    if min_a >= max_b or min_b >= max_a:
        return (False, None, None)
    
    min_depth = min(max_b - min_a, max_a - min_b)
    if min_depth < depth:
        depth = min_depth
        normal = axis

    #normal correction when body collide from top or left
    poly_center = getCenter(poly_vertices)

    direction_vect = poly_center - circle_center

    #check if we are pointing opposite direction
    if Dot(direction_vect, normal) < 0:
        normal = - normal

    return (True, normal, depth)

def projectCircle(center : Vector, radius : float, axis : Vector):

    direction = Normalize(axis)
    dir_and_rad = direction * radius

    left_point = center - dir_and_rad
    right_point = center + dir_and_rad

    min_projection = Dot(left_point, axis)
    max_projection = Dot(right_point, axis)

    return min_projection, max_projection

def getClosestPointPolygon(circle_center : Vector, poly_vertices : list[Vector]):
    """Return the index of the closest vertices to the circle"""
    result = None
    min_distance = sys.float_info.max

    i = 0
    for vertice in poly_vertices:
        distance = getDistance(vertice, circle_center)

        if distance < min_distance:
            min_distance = distance
            result = i
        
        i += 1
    
    return result

def intersectCircles(center_a : Vector, radius_a : float, 
                     center_b : Vector, radius_b : float):
    
    normal = Vector(0, 0)
    depth = 0

    distance = getDistance(center_a, center_b)
    radius_sum = radius_a + radius_b

    if distance >= radius_sum:
        return (False, None, None)
    
    normal = Normalize(center_b - center_a)
    depth = radius_sum - distance

    return (True, normal, depth)

#Return True if 2 polygons intersects and also return normal and depth of the movement needed
def intersectPolygons(vertices_a : list[Vector], vertices_b : list[Vector]):
    
    normal = Vector(0, 0)
    depth = sys.float_info.max

    # For all vertices of A
    for i in range(len(vertices_a)):
        vect_a = vertices_a[i]
        vect_b = vertices_a[(i + 1) % len(vertices_a)]

        edge = vect_b - vect_a
        axis = Vector(- edge.y, edge.x) #axis that test for separation
        axis = Normalize(axis)

        min_a, max_a = projectVertices(vertices_a, axis)
        min_b, max_b = projectVertices(vertices_b, axis)

        if min_a >= max_b or min_b >= max_a:
            return (False, None, None)
        
        min_depth = min(max_b - min_a, max_a - min_b)
        if min_depth < depth:
            depth = min_depth
            normal = axis
        
    #For all vertices of B
    for i in range(len(vertices_b)):
        vect_a = vertices_b[i]
        vect_b = vertices_b[(i + 1) % len(vertices_b)]

        edge = vect_b - vect_a
        axis = Vector(- edge.y, edge.x) #axis that test for separation
        axis = Normalize(axis)

        min_a, max_a = projectVertices(vertices_a, axis)
        min_b, max_b = projectVertices(vertices_b, axis)

        if min_a >= max_b or min_b >= max_a:
            return (False, None, None)
        
        min_depth = min(max_b - min_a, max_a - min_b)
        if min_depth < depth:
            depth = min_depth
            normal = axis

    #normal correction when body collide from top or left
    center_a = getCenter(vertices_a)
    center_b = getCenter(vertices_b)

    direction_vect = center_b - center_a

    #check if we are pointing opposite direction
    if Dot(direction_vect, normal) < 0:
        normal = - normal

    return (True, normal, depth)

def getCenter(vertices : list[Vector]):
    sum_x = 0
    sum_y = 0

    for vertice in vertices:
        sum_x += vertice.x
        sum_y += vertice.y

    return Vector(sum_x / len(vertices), sum_y / len(vertices))


# Check if 2 vertices collide or not 
def projectVertices(vertices : list[Vector], axis : Vector):

    min_projection = sys.float_info.max
    max_projection = sys.float_info.min

    for vertice in vertices:
        projection = Dot(vertice, axis)
    
        if projection < min_projection:
            min_projection = projection
        if projection > max_projection:
            max_projection = projection
    
    return min_projection, max_projection




