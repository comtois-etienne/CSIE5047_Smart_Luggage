from src.point import Point
from src.sensor import Camera
import matplotlib.pyplot as plt
import mediapipe as mp
import numpy as np
import queue
import time


def _landmark_point(landmark, frame_width, frame_height):
    return Point(int(landmark.x * frame_width), int(landmark.y * frame_height))


def _get_torso_properties(mp_pose, results, frame):
    left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

    left_shoulder_point = _landmark_point(left_shoulder, frame.shape[1], frame.shape[0])
    right_shoulder_point = _landmark_point(right_shoulder, frame.shape[1], frame.shape[0])
    left_hip_point = _landmark_point(left_hip, frame.shape[1], frame.shape[0])
    right_hip_point = _landmark_point(right_hip, frame.shape[1], frame.shape[0])

    shoulder_point = left_shoulder_point.middle(right_shoulder_point)
    hip_point = left_hip_point.middle(right_hip_point)
    
    torso_pixel_height = shoulder_point.distance(hip_point)
    shoulder_pixel_width = left_shoulder_point.distance(right_shoulder_point)

    return torso_pixel_height, shoulder_pixel_width, shoulder_point, hip_point


def _unwrap_result(result):
    return result['pose'], result['point'], result['distance'], result['angle']


def _wrap_result(result):
    return {
        'pose': result[0],
        'point': result[1],
        'distance': result[2],
        'angle': result[3]
    }


class PositionEstimator:

    def __init__(self, mp_pose, camera: Camera, obj_height, file_path, queue_size=3, kernel_size=3):
        self.mp_pose = mp_pose
        self.pose = self.mp_pose.Pose(static_image_mode=False)
        self.camera = camera
        self.obj_height = obj_height
        self.file_path = file_path
        self.distance_queue = queue.Queue(maxsize=queue_size)
        self.kernel_size = min(kernel_size, queue_size)

    def _add_distance(self, distance):
        if self.distance_queue.full():
            self.distance_queue.get()
        self.distance_queue.put(distance)

    # distance method 1: median
    def _get_median_distance(self):
        sorted_queue = sorted(self.distance_queue.queue)
        index = round(len(sorted_queue) / 2)
        return sorted_queue[index]
    
    # distance method 2: mean
    def _get_mean_distance(self):
        return np.mean(self.distance_queue.queue)
    
    # distance method 3: kernel
    def _get_kernel_distance(self):
        sorted_queue = sorted(self.distance_queue.queue)
        index = round(len(sorted_queue) / 2)
        k_neg = self.kernel_size // 2
        k_pos = self.kernel_size - k_neg - 1
        return np.mean(sorted_queue[index - k_neg:index + k_pos + 1])
    
    # use one of the distance methods
    def _get_distance(self, distance_method):
        if self.distance_queue.full():
            return distance_method()
        else:
            return self.distance_queue.queue[-1]
        
    def _verbose(self, verbose, image, pose_results):
        if verbose:
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing.draw_landmarks(
                image, 
                pose_results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )

    @staticmethod
    def wrap_result(pose, point, distance, angle):
        return _wrap_result((pose, point, distance, angle))

    @staticmethod
    def unwrap_result(result):
        return _unwrap_result(result)
    
    @staticmethod
    def plot_result(ax, frame, result, camera=None):
        pose, point, distance, angle = _unwrap_result(result)
        if pose.pose_landmarks is not None:
            if camera is not None:
                pixel_angle = camera.angle_to_pixel(angle)
                ax.plot([pixel_angle, pixel_angle], [0, frame.shape[0]], color='c', linewidth=2)
            ax.text(pixel_angle, 0, f'{angle:.1f} deg', color='r', fontsize=12)
            ax.text(pixel_angle, 40, f'{distance} mm', color='r', fontsize=12)
            ax.text(0, 0, f'x: {point.x}', color='r', fontsize=12)
            ax.text(0, 40, f'y: {point.y}', color='r', fontsize=12)

    def get_position(self, image, adjustment_ratio=1.0, verbose=False):
        pose_results = self.pose.process(image)
        if pose_results.pose_landmarks is None: return None
        self._verbose(verbose, image, pose_results)

        res = _get_torso_properties(self.mp_pose, pose_results, image)
        torso_pixel_height, shoulder_pixel_width, shoulder_point, hip_point = res
        middle_point = shoulder_point.middle(hip_point)

        distance, angle = self.camera.get_distance_angle(self.obj_height, torso_pixel_height, middle_point.x)
        distance = int(distance)

        self._add_distance(distance)
        distance = self._get_distance(self._get_kernel_distance)

        angle = round(angle, 1)
        distance = int(distance // 10 * 10)
        x, y = Camera.distance_angle_to_coordinates(distance, angle)
        point = Point(x, y) * adjustment_ratio
        point = point.round(10)

        return self.wrap_result(pose_results, point, distance, angle)
    
    def write_append(self, point, distance, angle):
        timestamp = round(time.time(), 3)
        with open(self.file_path, 'a') as f:
            f.write(f'{timestamp},{point.x},{point.y},{distance},{angle}\n')

    def write_overwrite(self, point, distance, angle):
        timestamp = round(time.time(), 3)
        with open(self.file_path, 'w') as f:
            f.write(f'{timestamp},{point.x},{point.y},{distance},{angle}')
    
    def save_blank(self, append=False):
        point, distance, angle = Point(-100, 0), 0, 0
        if append: self.write_append(point, distance, angle)
        else: self.write_overwrite(point, distance, angle)

    def save_position(self, image, adjustment_ratio=1.0, append=False, verbose=False):
        result = self.get_position(image, adjustment_ratio, verbose)
        
        point, distance, angle = Point(-100, 0), 0, 0
        if result is not None: 
            pose, point, distance, angle = self.unwrap_result(result)

        if append: self.write_append(point, distance, angle)
        else: self.write_overwrite(point, distance, angle)

        return result

