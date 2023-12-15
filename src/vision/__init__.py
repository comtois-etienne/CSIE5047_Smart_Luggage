from .position_estimator import PositionEstimator
from .video_capture import VideoCapture
from .object_detector import coco_classes
from .object_detector import ObjectDetector
from .object_detector import plot_obj
from .reid import ReID


def mask_frame(frame, box):
    frame = frame.copy()
    frame[:box['ymin'], :] = 0
    frame[box['ymax']:, :] = 0
    frame[:, :box['xmin']] = 0
    frame[:, box['xmax']:] = 0
    return frame


__all__ = [
    'PositionEstimator',
    'VideoCapture',
    'coco_classes',
    'ObjectDetector',
    'plot_obj',
    'ReID',
    'mask_frame',
]

