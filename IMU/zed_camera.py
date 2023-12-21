import pyzed.sl as sl


class ZedCamera:
    def __init__(self, zed_camera):
        self.zed = zed_camera
    
    def open(self):
        init_params = sl.InitParameters()
        init_params.depth_mode = sl.DEPTH_MODE.NONE
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print(repr(err))
            self.zed.close()
            return False
        else:
            self.sensors_data = sl.SensorsData()
        return True

    def close(self):
        self.zed.close()

    def get_sensors_data(self):
        return self.zed.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS
    
    def get_imu_data(self):
        return self.sensors_data.get_imu_data()

    def get_quaternion(self):
        return self.sensors_data.get_imu_data().get_pose().get_orientation().get()

    def get_camera_information(self):
        return self.zed.get_camera_information()

    def print_info(self):
        cam_info = self.get_camera_information()
        print("Camera Model: " + str(cam_info.camera_model))
        print("Serial Number: " + str(cam_info.serial_number))
        print("Camera Firmware: " + str(cam_info.camera_configuration.firmware_version))
        print("Sensors Firmware: " + str(cam_info.sensors_configuration.firmware_version))

