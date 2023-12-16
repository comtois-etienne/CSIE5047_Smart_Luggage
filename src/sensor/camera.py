from dataclasses import dataclass
import math


@ dataclass
class Camera:
    h_fov: float = 0.0 # Horizontal field of view
    v_fov: float = 0.0 # Vertical field of view
    d_fov: float = 0.0 # Diagonal field of view
    h_res: int = 0 # Horizontal resolution
    v_res: int = 0 # Vertical resolution
    is_rgbd: bool = False # Is RGBD camera

    def pixel_to_angle(self, pixel_x):
        return (pixel_x - self.h_res / 2) * self.h_fov / self.h_res
    
    def angle_to_pixel(self, angle):
        return int(angle * self.h_res / self.h_fov + self.h_res / 2)

    def get_distance_angle(self, actual_height, pixel_height, pixel_x):
        h_fov_rad = math.radians(self.h_fov)
        angle = self.pixel_to_angle(pixel_x)
        angle_rad = math.radians(angle)
        effective_pixel_width = pixel_height * math.cos(angle_rad)
        distance = (actual_height * self.h_res) / (effective_pixel_width * 2 * math.tan(h_fov_rad / 2))
        return distance, angle
    
    @staticmethod
    def distance_angle_to_coordinates(distance, angle):
        rad_angle = math.radians(angle)
        x = int(distance * math.cos(rad_angle))
        y = int(distance * math.sin(rad_angle))
        return x, y

