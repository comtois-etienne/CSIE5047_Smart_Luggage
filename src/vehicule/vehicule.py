from src.point import Point
import numpy as np
import math

follow_distance = 1200
sharp_distance = 600
follow_angle = 30


class Vehicule:
    def __init__(self, max_turn_angle, axle_len, max_speed, camera, center=Point(0,0,0)):
        self.max_turn_angle = np.radians(max_turn_angle)
        self.axle_len = axle_len
        self.max_speed = max_speed

        self.speed = 0
        self.wheel_angle = 0  # Radians
        self.north_angle = 0  # Radians
        self.fov = camera.h_fov

        self.center = center - Point(0, self.axle_len / 2, 0)
        self.update_axle_positions()

    def set_speed(self, speed):
        self.speed = min(speed, self.max_speed)

    def set_wheel_angle(self, angle):
        self.wheel_angle = np.radians(max(min(angle, np.degrees(self.max_turn_angle)), -np.degrees(self.max_turn_angle)))

    def set_wheel_left(self):
        self.set_wheel_angle(- np.degrees(self.max_turn_angle))

    def set_wheel_right(self):
        self.set_wheel_angle(np.degrees(self.max_turn_angle))

    def stop(self):
        self.set_speed(0)
        self.set_wheel_angle(0)

    def update_axle_positions(self):
        half_axle_length = self.axle_len / 2
        self.front = Point(self.center.x + half_axle_length * math.cos(self.north_angle),
                           self.center.y + half_axle_length * math.sin(self.north_angle))
        self.rear = Point(self.center.x - half_axle_length * math.cos(self.north_angle),
                          self.center.y - half_axle_length * math.sin(self.north_angle))

    def rotate_point_around_pivot(self, point, pivot, angle):
        return pivot.rotates(angle, point)

    def update_position(self, time):
        # Calculate the new front wheel position
        if self.wheel_angle != 0:
            turn_radius = self.axle_len / np.tan(self.wheel_angle)
            angle_change = self.speed / turn_radius * time
        else:
            angle_change = 0

        # Update north_angle (radians) and move the vehicle forward
        self.north_angle = (self.north_angle + angle_change) % (2 * np.pi)
        move_direction = (self.north_angle + self.wheel_angle) % (2 * np.pi)
        self.center.x += self.speed * math.cos(move_direction) * time
        self.center.y += self.speed * math.sin(move_direction) * time

        # Update the rear wheel position
        self.rear.x = self.center.x - (self.axle_len / 2) * math.cos(self.north_angle)
        self.rear.y = self.center.y - (self.axle_len / 2) * math.sin(self.north_angle)

        # Update the front wheel position
        self.front.x = self.center.x + (self.axle_len / 2) * math.cos(self.north_angle)
        self.front.y = self.center.y + (self.axle_len / 2) * math.sin(self.north_angle)

    def get_positions(self):
        return self.rear, self.front, self.center, self.north_angle
    
    def get_front(self):
        front = self.front.copy()
        front.a = np.degrees(self.north_angle)
        return front
    
    def angle_to_point(self, point):
        camera = self.get_front()
        angle = camera.direction(point)
        return angle
    
    def distance_to_point(self, point):
        return self.front.distance(point)
    
    def can_move(self, last_seen, new_seen):
        angle = self.angle_to_point(last_seen)
        distance = self.distance_to_point(last_seen)

        # modify the distance according to the spline ?
        if distance > follow_distance:
            return True
        if (distance > sharp_distance and (abs(angle) > follow_angle or new_seen is None)) :
            return True
        return False

