class TimestampHandler:
    def __init__(self):
        self.last_timestamp = 0

    def is_new(self, imu_data):
        current_timestamp = imu_data.timestamp.get_microseconds()
        if current_timestamp != self.last_timestamp:
            self.last_timestamp = current_timestamp
            return True
        return False

