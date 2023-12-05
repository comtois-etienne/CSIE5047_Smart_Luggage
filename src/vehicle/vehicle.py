from src.point import Point, normalize_angle
import numpy as np
import math


follow_distance = 1000
sharp_distance = 600
fov_reduction = 10


class Vehicle:
    def __init__(self, max_turn_angle, axle_len, max_speed, camera, center=Point(0,0,0)):
        self.max_turn_angle = np.radians(max_turn_angle)
        self.axle_len = axle_len
        self.max_speed = max_speed

        self.speed = 0
        self.wheel_angle = 0  # Radians
        self.north_angle = 0  # Radians
        self.fov = camera.h_fov

        self.center = center - Point(self.axle_len / 2, 0, 0)
        self.update_axle_positions()

    def set_speed(self, speed):
        self.speed = min(speed, self.max_speed)

    def set_wheel_angle(self, angle):
        self.wheel_angle = np.radians(max(min(angle, np.degrees(self.max_turn_angle)), -np.degrees(self.max_turn_angle)))

    def get_wheel_angle(self):
        return normalize_angle(np.degrees(self.wheel_angle))

    def set_wheel_left(self):
        self.set_wheel_angle(- np.degrees(self.max_turn_angle))

    def set_wheel_right(self):
        self.set_wheel_angle(np.degrees(self.max_turn_angle))

    def stop(self):
        self.set_speed(0)
        self.set_wheel_angle(0)

    def has_stopped(self):
        return self.speed == 0

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
    
    def sees(self, point):
        return point.is_visible(self.get_front(), fov=self.fov - fov_reduction)

    def update_axle_positions(self):
        half_axle_length = self.axle_len / 2
        self.front = Point(self.center.x + half_axle_length * math.cos(self.north_angle),
                           self.center.y + half_axle_length * math.sin(self.north_angle))
        self.rear = Point(self.center.x - half_axle_length * math.cos(self.north_angle),
                          self.center.y - half_axle_length * math.sin(self.north_angle))

    def rotate_point_around_pivot(self, point, pivot, angle):
        return pivot.rotates(angle, point)

    def update_position(self, time):
        old_front = self.get_front()
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

        new_front = self.get_front()
        return new_front - old_front

    def get_positions(self):
        return self.rear, self.front, self.center, self.north_angle
    
    def can_move(self, last_seen, has_seen=True):
        angle = self.angle_to_point(last_seen)
        distance = self.distance_to_point(last_seen)

        # modify the distance according to the spline ?
        if distance > follow_distance:
            return True
        if (distance > sharp_distance and (abs(angle) > self.fov // 4 or not has_seen)) :
            return True
        return False

    def look_around(self, speed=None, time=1):
        if speed is None:
            speed = self.max_speed
        if self.get_wheel_angle() >= 0:
            self.set_wheel_right()
        else:
            self.set_wheel_left()
        self.set_speed(speed)
        self.update_position(time)

    def follow_target(self, target, speed_ratio=0.25, time=1, has_seen=True):
        if self.can_move(target, target):
            self.set_speed(self.distance_to_point(target) * speed_ratio)
            self.set_wheel_angle(self.angle_to_point(target))
        else:
            self.stop()
        self.update_position(time)
        return self.has_stopped()
    
    def plot(self, ax):
        self.front.scatter(ax, color='b', size=20, label='front')
        self.rear.scatter(ax, color='c', size=20, label='rear')
        ax.plot([self.rear.y, self.front.y], [self.rear.x, self.front.x], color='c')
        fov = self.front.copy()
        fov.a = np.rad2deg(self.north_angle)
        fov.plot(ax, color='y', fov=self.fov - fov_reduction, fov_len=20000, linestyle='--', label='fov')
        ax.text(self.rear.y, self.rear.x, f'a: {self.get_wheel_angle():.2f}°\ns: {self.speed:.2f}mm/s', fontsize=12)
