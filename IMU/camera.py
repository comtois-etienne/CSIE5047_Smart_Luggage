import time
import math
import pyzed.sl as sl
import numpy as np
import matplotlib.pyplot as plt

class TimestampHandler:
    def __init__(self):
        self.last_timestamp = 0

    def is_new(self, imu_data):
        current_timestamp = imu_data.timestamp.get_microseconds()
        if current_timestamp != self.last_timestamp:
            self.last_timestamp = current_timestamp
            return True
        return False

def quaternion_rotation_matrix(Q):
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

def low_pass_filter(current_value, previous_value, alpha):
    return alpha * current_value + (1 - alpha) * previous_value

zed = sl.Camera()
init_params = sl.InitParameters()
init_params.depth_mode = sl.DEPTH_MODE.NONE

err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    print(repr(err))
    zed.close()
    exit(1)

cam_info = zed.get_camera_information()
print("Camera Model: " + str(cam_info.camera_model))
print("Serial Number: " + str(cam_info.serial_number))
print("Camera Firmware: " + str(cam_info.camera_configuration.firmware_version))
print("Sensors Firmware: " + str(cam_info.sensors_configuration.firmware_version))

ts_handler = TimestampHandler()
sensors_data = sl.SensorsData()
time_0 = time.time()

timestamps = []
yaw_angles = []
filtered_yaw_angles = []
previous_yaw_angle = 0.0
alpha = 0.1  # Adjust alpha based on the level of filtering desired

# Read initial orientation and set initial yaw angle to 0
if zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS:
    quaternion = sensors_data.get_imu_data().get_pose().get_orientation().get()
    rotation_matrix = quaternion_rotation_matrix(quaternion)
    initial_yaw_angle = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0]) * (180.0 / math.pi)
    # Add a 180-degree offset to set the initial yaw angle to 0
    initial_yaw_angle += 180
    previous_yaw_angle = initial_yaw_angle
p = 0
while time.time() - time_0 < 5:
    if zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS:
        if ts_handler.is_new(sensors_data.get_imu_data()):
            
            quaternion = sensors_data.get_imu_data().get_pose().get_orientation().get()
            rotation_matrix = quaternion_rotation_matrix(quaternion)
            yaw_angle = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0]) * (180.0 / math.pi)

            # Apply the low-pass filter
            filtered_yaw_angle = low_pass_filter(yaw_angle, previous_yaw_angle, alpha)
            previous_yaw_angle = filtered_yaw_angle
            if abs(p - yaw_angle) > 180:
                if yaw_angle > 0:
                    yaw_angle = yaw_angle - 360
                    filtered_yaw_angle = filtered_yaw_angle - 360
                else:
                    yaw_angle = yaw_angle + 360
                    filtered_yaw_angle = filtered_yaw_angle + 360
            timestamps.append(time.time() - time_0)
            yaw_angles.append(yaw_angle)
            filtered_yaw_angles.append(filtered_yaw_angle)
            p = yaw_angle
            print("Raw Yaw Angle: {:.2f} degrees, Filtered Yaw Angle: {:.2f} degrees".format(yaw_angle, filtered_yaw_angle))

zed.close()

plt.plot(timestamps, yaw_angles, label="Raw Yaw Angle")
plt.plot(timestamps, filtered_yaw_angles, label="Filtered Yaw Angle")
plt.xlabel("Time (seconds)")
plt.ylabel("Yaw Angle (degrees)")
plt.title("Yaw Angle Over Time with Low-Pass Filtering")
plt.legend()
plt.show()

#  if abs(p - yaw_angle) > 180:
#                 if yaw_angle > 0:
#                     yaw_angle = yaw_angle - 360
#                     filtered_yaw_angle = filtered_yaw_angle - 360
#                     p = yaw_angle
#                 else:
#                     yaw_angle = yaw_angle + 360
#                     filtered_yaw_angle = filtered_yaw_angle + 360
#                     p = yaw_angle
