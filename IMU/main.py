import matplotlib.pyplot as plt
import pyzed.sl as sl

from .timestamp_handler import TimestampHandler
from .zed_camera import ZedCamera
from .imu_capture import IMUCapture


ts_handler = TimestampHandler()
zed_camera = ZedCamera(sl.Camera())
exit(1) if not zed_camera.open() else None
zed_camera.print_info()
imu_cap = IMUCapture(ts_handler, zed_camera, alpha=0.1, save_history=True)

imu_cap.capture() # Read initial orientation and set initial yaw angle to 0
while True:
    yaw_angle, filtered_yaw_angle = imu_cap.capture()
    if yaw_angle is not None and filtered_yaw_angle is not None:
        print("Raw Yaw Angle: {:.2f} degrees, Filtered Yaw Angle: {:.2f} degrees".format(yaw_angle, filtered_yaw_angle))
zed_camera.close()

plt.plot(imu_cap.timestamps, imu_cap.yaw_angles, label="Raw Yaw Angle")
plt.plot(imu_cap.timestamps, imu_cap.filtered_yaw_angles, label="Filtered Yaw Angle")
plt.xlabel("Time (seconds)")
plt.ylabel("Yaw Angle (degrees)")
plt.title("Yaw Angle Over Time with Low-Pass Filtering")
plt.legend()
plt.show()

