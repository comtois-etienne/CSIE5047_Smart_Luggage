import time
import math
import numpy as np
from .zed_camera import ZedCamera
from .timestamp_handler import TimestampHandler


class IMUCapture:
    def __init__(self, ts_handler: TimestampHandler, zed_camera: ZedCamera, alpha=0.1, save_history=False):
        self.timestamps = []
        self.yaw_angles = []
        self.filtered_yaw_angles = []

        self.prev_filtered_yaw_angle = None
        self.prev_yaw_angle = None
        self._has_cap = False

        self.ts_handler = ts_handler
        self.zed = zed_camera
        self.alpha = alpha
        self.save_history = save_history
        self.time_0 = time.time()

    def _has_captured(self):
        return self._has_cap
    
    @staticmethod
    def _quaternion_rotation_matrix(Q):
        q0, q1, q2, q3 = Q
        r00 = 1 - 2 * (q0 * q0 + q1 * q1)
        r01 = 2 * (q1 * q2 - q0 * q3)
        r02 = 2 * (q1 * q3 + q0 * q2)
        r10 = 2 * (q1 * q2 + q0 * q3)
        r11 = 1 - 2 * (q0 * q0 + q2 * q2)
        r12 = 2 * (q2 * q3 - q0 * q1)
        r20 = 2 * (q1 * q3 - q0 * q2)
        r21 = 2 * (q2 * q3 + q0 * q1)
        r22 = 1 - 2 * (q0 * q0 + q3 * q3)
        return np.array([[r00, r01, r02], [r10, r11, r12], [r20, r21, r22]])
    
    @staticmethod
    def _get_yaw_angle(rotation_matrix):
        return math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0]) * (180.0 / math.pi)

    @staticmethod
    def _low_pass_filter(current_value, previous_value, alpha):
        return alpha * current_value + (1 - alpha) * previous_value

    def _filter_yaw_angle(self, yaw_angle):
        filtered_yaw_angle = self._low_pass_filter(yaw_angle, self.prev_filtered_yaw_angle, self.alpha)
        if abs(self.prev_yaw_angle - yaw_angle) > 180:
            if yaw_angle > 0:
                yaw_angle = yaw_angle - 360
                filtered_yaw_angle = filtered_yaw_angle - 360
            else:
                yaw_angle = yaw_angle + 360
                filtered_yaw_angle = filtered_yaw_angle + 360
        return yaw_angle, filtered_yaw_angle
    
    def _firts_capture(self):
        quaternion = self.zed.get_quaternion()
        rotation_matrix = self._quaternion_rotation_matrix(quaternion)
        self.prev_filtered_yaw_angle = self._get_yaw_angle(rotation_matrix) + 180
        self.prev_yaw_angle = 0.0
        self._has_cap = True

    def _capture(self):
        quaternion = self.zed.get_quaternion()
        rotation_matrix = self._quaternion_rotation_matrix(quaternion)
        yaw_angle = self._get_yaw_angle(rotation_matrix)
        yaw_angle, filtered_yaw_angle = self._filter_yaw_angle(yaw_angle)
        return yaw_angle, filtered_yaw_angle
    
    def _save_history(self):
        self.timestamps.append(time.time() - self.time_0)
        self.yaw_angles.append(self.prev_yaw_angle)
        self.filtered_yaw_angles.append(self.prev_filtered_yaw_angle)

    def get_previous_yaw_angle(self):
        return self.prev_yaw_angle, self.prev_filtered_yaw_angle

    def capture(self):
        if not self._has_captured() and self.zed.get_sensors_data():
            self._firts_capture()
        elif self.zed.get_sensors_data():
            yaw_angle, filtered_yaw_angle = self._capture()
            self.prev_filtered_yaw_angle = filtered_yaw_angle
            self.prev_yaw_angle = yaw_angle
            self._save_history() if self.save_history else None
            return yaw_angle, filtered_yaw_angle
        return None, None

