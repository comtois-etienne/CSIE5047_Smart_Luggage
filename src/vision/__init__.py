from .position_estimator import PositionEstimator
from .video_capture import VideoCapture
from .object_detector import coco_classes
from .object_detector import ObjectDetector
from .object_detector import plot_obj
from .reid import ReID


PE_FILE_PATH = 'io/pe.csv'


def mask_frame(frame, box):
    frame = frame.copy()
    frame[:box['ymin'], :] = 0
    frame[box['ymax']:, :] = 0
    frame[:, :box['xmin']] = 0
    frame[:, box['xmax']:] = 0
    return frame


def reset_pe_file(file_path):
    pe = PositionEstimator(None, None, None, file_path)
    pe.save_blank()


__all__ = [
    'PositionEstimator',
    'reset_pe_file',
    'PE_FILE_PATH',
    'VideoCapture',
    'coco_classes',
    'ObjectDetector',
    'plot_obj',
    'ReID',
    'mask_frame',
]

