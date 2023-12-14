from .vehicle import Vehicle
from src.vision import FakeSensor
from src.point import Point

from scipy.interpolate import LSQUnivariateSpline
from dataclasses import dataclass
import pandas as pd
import numpy as np
import time


follow_distance = 1200
sharp_distance = 800


def get_spline(last_points):

    if len(last_points) < 6:
        return [Point.from_df(last_points.iloc[-1])]
    
    ti = np.array(last_points.index, dtype=float)
    num_knots = max(1, len(last_points) // 8)
    t_knots = np.linspace(ti.min(), ti.max(), num_knots)[1:-1]
    spline_x = LSQUnivariateSpline(ti, last_points['x'], t_knots)
    spline_y = LSQUnivariateSpline(ti, last_points['y'], t_knots)

    min_distance = 300
    sampled_points = []
    last_point = None
    
    # Iterate over the spline
    for ti in np.linspace(ti.min(), ti.max(), 100):
        current_point = Point(spline_x(ti), spline_y(ti), 0)

        if last_point is None:
            # First point
            sampled_points.append(current_point)
            last_point = current_point
        else:
            # Check distance
            if current_point.distance(last_point) >= min_distance:
                sampled_points.append(current_point)
                last_point = current_point

    return sampled_points


def get_spline_df(points):
    spline = get_spline(points)
    return pd.DataFrame({
        'x': [p.x for p in spline],
        'y': [p.y for p in spline],
    })


def get_target(df_spline_incoming, last_seen):
    if len(df_spline_incoming) == 0:
        return last_seen
    else:
        return Point.from_df(df_spline_incoming.iloc[0])


def get_incoming(df_points, min_distance=300):
    return df_points[df_points['x'] > min_distance], df_points[df_points['x'] <= min_distance]


@dataclass
class VehicleMover:
    # Parameters
    vehicle: Vehicle
    sensor: FakeSensor
    smoothing: int = 4

    # Internal
    tick: int = 0
    capture_time: float = 0
    has_seen: bool = False
    seen: pd.DataFrame = pd.DataFrame(columns=['t', 'x', 'y'])
    actual_path: pd.DataFrame = pd.DataFrame(columns=['x', 'y'])

    def __post_init__(self):
        self.seen = pd.concat([self.seen, pd.DataFrame({
            't': 0, # timestamp
            'x': 0, # x position
            'y': 0, # y position
        }, index=[len(self.seen)])])
        self.actual_path = pd.concat([self.actual_path, pd.DataFrame({
            'x': 0, # x position
            'y': 0, # y position
        }, index=[len(self.actual_path)])])

    def recenter(self):
        front = self.vehicle.get_front()
        self.seen = front.rotate_df(front.a, self.seen, recenter=True)

        self.actual_path = front.rotate_df(front.a, self.actual_path, recenter=True)
        self.actual_path = pd.concat([self.actual_path, pd.DataFrame({
            'x': 0, # x position
            'y': 0, # y position
        }, index=[len(self.actual_path)])])

        self.sensor.recenter(self.vehicle)
        self.vehicle.recenter()

    def capture(self):
        new_seen = self.sensor.capture(self.vehicle)
        self.has_seen = new_seen is not None
        if self.has_seen:
            self.seen = pd.concat([self.seen, pd.DataFrame({
                't': [self.sensor.time()],
                'x': [new_seen.x],
                'y': [new_seen.y]
            }, index=[len(self.seen)])])

    def get_last_seen(self, count=1):
        count = min(count, len(self.seen))
        return self.seen.iloc[-count:]
    
    def is_done(self):
        return self.sensor.is_done() and self.vehicle.has_stopped()

    def step(self):
        time_smoothing = 1 / self.smoothing

        if self.tick == 0:
            t_a = time.time()
            self.capture()
            self.capture_time = time.time() - t_a
            print(f'Capture time: {self.capture_time}')
        
        last_points = self.get_last_seen(25)
        last_seen = Point.from_df(last_points.iloc[-1])
        incoming, passed = get_incoming(get_spline_df(last_points))
        target = get_target(incoming, last_seen)

        self.vehicle.follow_target(target, last_seen, time_smoothing, self.has_seen)
        self.recenter()

        self.tick = (self.tick + 1) % self.smoothing

        return incoming, passed, last_seen, target

