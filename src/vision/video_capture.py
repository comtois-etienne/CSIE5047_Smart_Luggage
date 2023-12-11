from dataclasses import dataclass
import cv2


@dataclass
class VideoCapture:
    path: str = 0
    cap: cv2.VideoCapture = None

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def take(self):
        self.release()
        self.cap = cv2.VideoCapture(self.path)

    def __post_init__(self):
        self.take()

    def __del__(self):
        self.release()

    def isOpened(self):
        if self.cap is None:
            return False
        return self.cap.isOpened()
    
    def skip_frames(self, n):
        for _ in range(n):
            if self.cap is not None:
                self.cap.grab()

    def grab_frame(self):
        if self.cap is None:
            return None
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if ret else None
        return frame

