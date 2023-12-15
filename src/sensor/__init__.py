from .camera import Camera
from .fake_sensor import FakeSensor
from .sensor import Sensor

avg_shoulder_width = 350.0
avg_torso_height = 460.0

mba_video_camera = Camera(
    h_fov=59.0,
    h_res=1080,
    v_res=720,
)

mba_photo_camera = Camera(
    h_fov=67.0,
    h_res=1290,
    v_res=720,
)

yt_video_camera = Camera(
    h_fov=60,
    h_res=1440,
    v_res=962,
)

zed_two_camera = Camera(
    h_fov=110.0,
    v_fov=70.0,
)

__all__ = [
    'Camera',
    'FakeSensor',
    'Sensor',
    'mba_video_camera',
    'mba_photo_camera',
    'yt_video_camera',
    'zed_two_camera',
    'avg_shoulder_width',
    'avg_torso_height',
]