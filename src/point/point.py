# todo type conversion

from dataclasses import dataclass
import numpy as np
import pandas as pd
import math

NORTH = 0
EAST = 90
SOUTH = 180
WEST = -90


def normalize_angle(angle):
    return (angle + 180) % 360 - 180


@dataclass
class Point:
    x: int = 0
    y: int = 0
    a: float = None

    def astype(self, astype=int):
        return Point(astype(self.x), astype(self.y), self.a)

    def copy(self):
        return Point(self.x, self.y, self.a)
    
    def round(self, increment=10):
        x = int(self.x // increment * increment)
        y = int(self.y // increment * increment)
        return Point(x, y, self.a)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        if self.a is not None and other.a is not None:
            a = normalize_angle(self.a + other.a)
            return Point(x, y, a)
        return Point(x, y)
    
    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        if self.a is not None and other.a is not None:
            a = normalize_angle(self.a - other.a)
            return Point(x, y, a)
        return Point(x, y)
    
    def __mul__(self, other):
        x = self.x * other
        y = self.y * other
        return Point(x, y)
    
    def __pow__(self, exp):
        x = self.x ** exp
        y = self.y ** exp
        return Point(x, y)
    
    def __sqrt__(self):
        x = np.sqrt(self.x)
        y = np.sqrt(self.y)
        return Point(x, y)
    
    def euclidean_distance(self, other, astype=int):
        dt = self - other
        dt = dt ** 2
        dt = dt.x + dt.y
        return astype(np.sqrt(dt))
    
    def manhattan_distance(self, other, astype=int):
        dt = self - other
        dt = np.abs(dt.x) + np.abs(dt.y)
        return astype(dt)

    def distance(self, other, astype=int):
        return self.euclidean_distance(other, astype)
    
    def y_distance(self, other):
        return self.y - other.y
    
    def x_distance(self, other):
        return self.x - other.x
    
    def between(self, other, ratio=0.5):
        x = self.x + (other.x - self.x) * ratio
        y = self.y + (other.y - self.y) * ratio
        return Point(x, y)
    
    def middle(self, other):
        return self.between(other, 0.5)

    def is_inside(self, other):
        return self.x >= 0 and self.x < other.x and self.y >= 0 and self.y < other.y
    
    def angle(self, other):
        return np.degrees(np.arctan2(other.y - self.y, other.x - self.x))
    
    def direction(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        angle_to_other = math.degrees(math.atan2(dy, dx))
        angle_difference = angle_to_other - self.a
        if angle_difference > 180:
            angle_difference -= 360
        elif angle_difference < -180:
            angle_difference += 360
        return angle_difference

    def rotates(self, angle, other, recenter=False):
        angle_rad = math.radians(angle)
        rotated_x = self.x + (other.x - self.x) * math.cos(angle_rad) - (other.y - self.y) * math.sin(angle_rad)
        rotated_y = self.y + (other.x - self.x) * math.sin(angle_rad) + (other.y - self.y) * math.cos(angle_rad)
        rotated_point = Point(rotated_x, rotated_y)
        if other.a is not None:
            rotated_point.a = (other.a + angle) % 360
        if recenter:
            rotated_point = rotated_point - self
        return rotated_point
    
    def center_df(self, others: pd.DataFrame):
        others = others.copy()
        others.x -= self.x
        others.y -= self.y
        return others
    
    def rotate_df(self, angle, others: pd.DataFrame, recenter=False):
        others = self.center_df(others)
        angle = np.radians(angle)
        rot = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        others.x, others.y = np.dot(others[['x', 'y']], rot).T
        # if recenter:
        #     others += self
        return others
    
    def to_df(self):
        return pd.DataFrame({'x': [self.x], 'y': [self.y]})
    
    def scatter(self, ax, color='r', marker=None, size=10, label=None):
        if marker is None:
            ax.scatter(self.y, self.x, c=color, s=size, label=label)
        else:
            ax.scatter(self.y, self.x, marker, c=color, s=size, label=label)
    
    def plot(self, ax, color='r', label=None, linestyle='--', fov=0, fov_len=1000):
        if self.a is None:
            self.a = 0
        pt_len = Point(fov_len, 0) + self
        pt_l = self.rotates(fov//2 + self.a, pt_len)
        pt_r = self.rotates(-(fov//2) + self.a, pt_len)
        ax.plot([self.y, pt_l.y], [self.x, pt_l.x], color=color, linestyle=linestyle, label=label)
        ax.plot([self.y, pt_r.y], [self.x, pt_r.x], color=color, linestyle=linestyle)

    def is_visible(self, viewer, fov=60, verbose=False):
        angle_to_point = normalize_angle(viewer.angle(self))
        hfov = fov / 2
        lower_bound = normalize_angle(viewer.a - hfov)
        upper_bound = normalize_angle(viewer.a + hfov)

        if verbose:
            print(lower_bound, upper_bound, angle_to_point)

        if lower_bound > upper_bound:
            return angle_to_point > lower_bound or angle_to_point < upper_bound
        return lower_bound < angle_to_point and angle_to_point < upper_bound

    @staticmethod
    def origin():
        return Point()
    
    @staticmethod
    def from_df(df: pd.DataFrame):
        return Point(df['x'], df['y'])
    
    @staticmethod
    def from_tuple(tup):
        return Point(tup[0], tup[1])

