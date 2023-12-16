from src.sensor import Camera
from src.sensor import mba_photo_camera
from src.sensor import mba_video_camera
from src.sensor import zed_two_camera
from src.sensor import yt_video_camera

import matplotlib.pyplot as plt
from src.vehicle import Vehicle
from src.vehicle import VehicleMover
from src.vehicle import reset_md_file, MD_FILE_PATH
from src.vision import reset_pe_file, PE_FILE_PATH
from src.point import Point
from src.sensor import FakeSensor, Sensor
from src.point import create_map
import pandas as pd
import numpy as np
import time


# RESET FILES
reset_pe_file(PE_FILE_PATH)
reset_md_file(MD_FILE_PATH)


# SENSOR
# sensor_data = pd.read_csv('csv/dist_2fps.csv', header=None)
# sensor_data.columns = ['t', 'x', 'y']
# sensor_data['t'] = sensor_data['t'].astype(float)
# sensor = FakeSensor(sensor_data, to_recenter=True)
sensor = Sensor(PE_FILE_PATH, refresh_rate=1)


# VEHICLE
verbose = False
vehicle = Vehicle(
    max_turn_angle=30, 
    axle_len=265, 
    max_speed=2000, 
    camera=zed_two_camera,
    center=Point(0, 0)
)


# VEHICLE MOVER
vehicle_mover = VehicleMover(
    vehicle, 
    sensor, 
    MD_FILE_PATH, 
    frame_rate=4, 
    follow_distance=1200,
    turn_distance=600,
)


while not vehicle_mover.is_done():
    start = time.time()
    incoming, passed, last_seen, target = vehicle_mover.step()

    if verbose:
        fig, ax = create_map(Point(0, 0), 10000, 6)
        ax.scatter(target.y, target.x, marker='x', color='b')
        ax.plot(incoming['y'], incoming['x'], label='Spline')
        ax.plot(passed['y'], passed['x'], label='Passed')
        Point(0, 0).scatter(ax, color='r', size=20)
        for x in range(len(vehicle_mover.seen)):
            Point.from_df(vehicle_mover.seen.iloc[x]).scatter(ax, color='k', size=20)

        a_north = np.degrees(vehicle.relative_angle)
        pt_direction = Point.origin().rotates(a_north, Point(1000, 0))
        # line from origin to pt_direction
        ax.plot([0, pt_direction.y], [0, pt_direction.x], color='r', label=f'North {a_north:.1f}')

        ax.plot(vehicle_mover.actual_path['y'], vehicle_mover.actual_path['x'], label='Actual Path')

        sensor.scatter_host(ax, vehicle)
        vehicle.plot(ax)
        ax.legend()
        plt.show()

    delta = time.time() - start
    wait_time = vehicle_mover.frame_time() - delta
    if wait_time > 0: time.sleep(wait_time)
    else: print(f'No time to wait')

