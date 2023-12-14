from src.point import Point
from src.point import normalize_angle as na
import numpy as np
import math


follow_distance = 1200
sharp_distance = 800
fov_reduction = 10


class Vehicle:
    def __init__(self, max_turn_angle, axle_len, max_speed, camera, center=Point(0,0,0)):
        self.max_turn_angle = np.radians(max_turn_angle)
        self.axle_len = axle_len
        self.max_speed = max_speed

        self.lost_time = 0
        self.is_sharp_turn = False

        self.speed = 0
        self.wheel_angle = 0  # Radians
        self.north_angle = 0  # Radians
        self.fov = camera.h_fov

        self.last_movement = Point(0, 0, 0)
        self.center = center - Point(self.axle_len / 2, 0, 0)
        self.update_axle_positions()

    def set_speed(self, speed):
        sign = 1 if speed >= 0 else -1
        self.speed = min(abs(speed), self.max_speed) * sign

    def set_wheel_angle(self, angle):
        self.wheel_angle = np.radians(max(min(angle, np.degrees(self.max_turn_angle)), -np.degrees(self.max_turn_angle)))

    def is_max_turn_angle(self):
        return abs(np.degrees(self.wheel_angle)) == abs(np.degrees(self.max_turn_angle))

    def get_wheel_angle(self):
        return na(np.degrees(self.wheel_angle))

    def set_wheel_left(self):
        self.set_wheel_angle(- na(np.degrees(self.max_turn_angle)))

    def set_wheel_right(self):
        self.set_wheel_angle(na(np.degrees(self.max_turn_angle)))

    def stop(self):
        self.set_speed(0)

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
    
    def vehicle_angle(self):
        return na(self.rear.angle(self.front))
    
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

    def recenter(self):
        self.north_angle = 0
        self.center = Point(- self.axle_len / 2, 0, 0)
        self.update_axle_positions()

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
        self.last_movement = new_front - old_front

    def get_positions(self):
        return self.rear, self.front, self.center, self.north_angle
    
    def can_move(self, last_seen):
        angle = self.angle_to_point(last_seen)
        distance = self.distance_to_point(last_seen)

        # modify the distance according to the spline ?
        if self.lost_time > 2:
            return True
        if distance > follow_distance:
            return True
        if (distance > sharp_distance and (abs(angle) > self.fov // 4)) :
            return True
        return False

    def look_around(self, target=None, speed=None):
        if speed is None:
            speed = self.max_speed // 4

        angle = self.get_wheel_angle() if target is None else self.angle_to_point(target)
        self.set_wheel_right() if angle >= 0 else self.set_wheel_left()
        self.set_speed(speed)

    def sharp_turn(self, angle, speed):
        if not self.is_sharp_turn:
            self.set_wheel_left() if angle >= 0 else self.set_wheel_right()
            self.set_speed(-speed)
        self.is_sharp_turn = True
        # turn half of the angle by going backward

    def start_self_turn(self, desired_angle, max_distance, speed):
        self.desired_angle = desired_angle
        self.max_distance = max_distance
        self.set_speed(speed)
        self.turn_base_point = self.center.copy()
        self.turn_initial_angle = self.get_front().a
        self.turn_time = max_distance / speed
        self.turn_direction = 1 if desired_angle > 0 else -1

    def follow_target(self, target, host, time=1, has_seen=True, speed_ratio=0.25):
        self.lost_time = 0 if has_seen else self.lost_time + 1
        angle = self.angle_to_point(target)
        print(angle)
        can_move = self.can_move(host)
        # if self.lost_time > 5 and target == host:
            # self.look_around()
        if not can_move:
            self.stop()
        elif (abs(angle) > self.max_turn_angle and self.lost_time > 4) or self.lost_time > 4:
            self.sharp_turn(angle, self.max_speed // 8)
        else:
            target = target + Point(self.axle_len * 2, 0, 0)
            # todo account for the host angle for distance
            self.set_speed(self.distance_to_point(host) * speed_ratio)
            self.set_wheel_angle(angle)

        self.update_position(time)
        return self.has_stopped()
    
    def follow_host(self, host, time=1, has_seen=True, speed_ratio=0.25):
        self.lost_time = 0 if has_seen else self.lost_time + 1
        if self.can_move(host):
            self.set_speed(self.distance_to_point(host) * speed_ratio)
            self.set_wheel_angle(self.angle_to_point(host))
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

