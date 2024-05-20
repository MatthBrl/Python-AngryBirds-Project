from physics.collisions import *

class CollisionObject():
    def __init__(self, body_a : Body, body_b : Body, 
                 normal : Vector, depth : float, 
                 point1 : Vector, point2 : Vector, nb_point : int):
        self.body_a = body_a
        self.body_b = body_b
        self.normal = normal
        self.depth = depth
        self.point1 = point1
        self.point2 = point2
        self.nb_point = nb_point



class Space():
    def __init__(self, screen):
        self.screen = screen
        self.gravity = Vector(0, 9.8)
        self.bodys = []

        self.colliding = []

        self.to_delete = []

    def add_body(self, body):
        self.bodys.append(body)
    
    def remove_body(self, index):
        self.bodys.pop(index)

    def clear_space(self):
        self.bodys.clear()

    def toggle_freeze_space(self):
        for body in self.bodys:
            if not body.body.is_static:
                body.body.toggle_freeze()

    def draw(self):
        for body in self.bodys:
            body.body.draw()

    def step(self, dt, iteration):
        for i in range(iteration):
            for body in self.bodys:
                body.body.step(dt / iteration, self.gravity)
                body.body.draw()

            self.colliding.clear()
            self.check_collision()

            for collision in self.colliding:
                self.handle_collision(collision)
                #FOR DEBUG !!!
                #Draw collision point
                # pygame.draw.circle(self.screen, (255, 0, 0), toCoord(collision.point1), 5)
                # pygame.draw.circle(self.screen, (255, 0, 0), toCoord(collision.point2), 5)
    
    def check_collision(self):
        nb_body = len(self.bodys)
        for i in range(nb_body):

            body_a = self.bodys[i].body

            if body_a.freezed:
                continue

            for j in range(nb_body):
                if j == i:
                    continue

                body_b = self.bodys[j].body

                if body_b.is_static and body_a.is_static:
                    continue

                if not intersectBoundingBox(body_a.bounding_box, body_b.bounding_box):
                    continue

                collision, normal, depth = Collide(body_a, body_b)

                if collision:
                    ###ADDED FOR THE GAME (delete a pig if he collide with a bird or a plank with high velocity)
                    if (body_a.linear_velocity.x >= 10 or body_a.linear_velocity.y >= 10) and \
                    body_a.shape_type == Shape.CIRCLE and body_b.shape_type == Shape.CIRCLE and \
                    body_b.radius == 13:
                        self.to_delete.append(j)
                    elif (body_a.linear_velocity.x >= 200 or body_a.linear_velocity.y >= 200) and \
                    body_a.shape_type == Shape.BOX and body_b.shape_type == Shape.CIRCLE and \
                    body_b.radius != 14:
                        self.to_delete.append(j)

                    if body_a.is_static:
                        body_b.update_pos(normal * depth / 2)
                    elif body_b.is_static:
                        body_a.update_pos( - normal * depth / 2)
                    else:
                        body_a.update_pos( - normal * depth / 2)
                        body_b.update_pos(normal * depth / 2)

                    point_1, point_2, nb_point = getContactPoints(body_a, body_b)
                    colliding_obj = CollisionObject(body_a, body_b, normal, depth, point_1, point_2, nb_point)
                    self.colliding.append(colliding_obj)

                    #self.handle_collision(body_a, body_b, normal, depth)
        for index in self.to_delete:
            self.remove_body(index)
        self.to_delete.clear()

    def handle_collision(self, collision : CollisionObject):
        restitution = min(collision.body_a.restitution, collision.body_b.restitution)
        
        contact_points = [collision.point1, collision.point2]
        d_body_a_list = []
        d_body_b_list = []
        impulse_list = []
        friction_impulse_list = []
        j_list = []

        #calculate impulse of each points
        for i in range(collision.nb_point):
            
            #distance between contact point and center of the object
            d_body_a = contact_points[i] - collision.body_a.position
            d_body_a_list.append(d_body_a)
            d_body_b = contact_points[i] - collision.body_b.position
            d_body_b_list.append(d_body_b)

            #perpendicular vector of distance between contact point and object
            d_body_a_perp = Vector(- d_body_a.y, d_body_a.x)
            d_body_b_perp = Vector(- d_body_b.y, d_body_b.x)

            angular_velocity_a = d_body_a_perp * collision.body_a.angular_velocity
            angular_velocity_b = d_body_b_perp * collision.body_b.angular_velocity

            relative_velocity = (collision.body_b.linear_velocity + angular_velocity_b) - (collision.body_a.linear_velocity + angular_velocity_a)

            #if they are already moving appart
            dot_velocity = Dot(relative_velocity, collision.normal)
            if dot_velocity > 0:
                return
            
            j = (- (1 + restitution) * dot_velocity) / (collision.body_a.inverse_mass + collision.body_b.inverse_mass + 
                                                        (Dot(d_body_a_perp, collision.normal)**2) * collision.body_a.inverse_inertia +
                                                        (Dot(d_body_b_perp, collision.normal)**2) * collision.body_b.inverse_inertia)
            j = j / collision.nb_point
            j_list.append(j)

            impulse = collision.normal * j
            impulse_list.append(impulse)

        #apply impulse
        for i in range(collision.nb_point):
            impulse = impulse_list[i]

            #applying linear velocity
            collision.body_a.linear_velocity -= impulse * collision.body_a.inverse_mass
            collision.body_b.linear_velocity += impulse * collision.body_b.inverse_mass

            #applying angular velocity
            collision.body_a.angular_velocity += Cross(impulse, d_body_a_list[i]) * collision.body_a.inverse_inertia
            collision.body_b.angular_velocity -= Cross(impulse, d_body_b_list[i]) * collision.body_b.inverse_inertia

        d_body_a_list.clear()
        d_body_b_list.clear()

        #calculate friction impulse of each points
        for i in range(collision.nb_point):
            
            #distance between contact point and center of the object
            d_body_a = contact_points[i] - collision.body_a.position
            d_body_a_list.append(d_body_a)
            d_body_b = contact_points[i] - collision.body_b.position
            d_body_b_list.append(d_body_b)

            #perpendicular vector of distance between contact point and object
            d_body_a_perp = Vector(- d_body_a.y, d_body_a.x)
            d_body_b_perp = Vector(- d_body_b.y, d_body_b.x)

            angular_velocity_a = d_body_a_perp * collision.body_a.angular_velocity
            angular_velocity_b = d_body_b_perp * collision.body_b.angular_velocity

            relative_velocity = (collision.body_b.linear_velocity + angular_velocity_b) - (collision.body_a.linear_velocity + angular_velocity_a)

            tan = relative_velocity - collision.normal * Dot(relative_velocity, collision.normal)
            
            #if tan is less than 0
            if nearEqualVect(tan, Vector(0, 0)):
                return
            
            tan = Normalize(tan)

            j = -Dot(relative_velocity, tan) / (collision.body_a.inverse_mass + collision.body_b.inverse_mass + 
                                                                       (Dot(d_body_a_perp, tan)**2) * collision.body_a.inverse_inertia +
                                                                       (Dot(d_body_b_perp, tan)**2) * collision.body_b.inverse_inertia)
            j = j / collision.nb_point

            friction_impulse = None
            if(abs(j) <= j_list[i] * collision.body_a.static_friction):
                friction_impulse = tan * j
            else:
                friction_impulse = tan * -j_list[i] * collision.body_a.dynamic_friction

            friction_impulse_list.append(friction_impulse)

        #apply friction impulse
        for i in range(collision.nb_point):
            friction_impulse = friction_impulse_list[i]

            #applying linear velocity
            collision.body_a.linear_velocity -= friction_impulse * collision.body_a.inverse_mass
            collision.body_b.linear_velocity += friction_impulse * collision.body_b.inverse_mass

            #applying angular velocity
            collision.body_a.angular_velocity += Cross(friction_impulse, d_body_a_list[i]) * collision.body_a.inverse_inertia
            collision.body_b.angular_velocity -= Cross(friction_impulse, d_body_b_list[i]) * collision.body_b.inverse_inertia





