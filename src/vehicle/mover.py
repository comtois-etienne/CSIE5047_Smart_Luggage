from .vehicle import Vehicle
from src.sensor import FakeSensor, Sensor
from src.point import Point

from scipy.interpolate import LSQUnivariateSpline
from dataclasses import dataclass
import pandas as pd
import numpy as np
import time


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
    sensor: Sensor
    file_path: str
    frame_rate: int = 8
    follow_distance: int = 1000
    turn_distance: int = 600

    # Internal
    _tick: int = 0
    _frame_time: float = 0
    _has_seen: bool = False
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
        self._frame_time = 1 / self.frame_rate

    def frame_time(self):
        return self._frame_time

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

    def write_overwrite(self, angle, speed):
        with open(self.file_path, 'w') as f:
            f.write(f'{format(angle, ".1f")},{speed}')

    def capture(self):
        new_seen = self.sensor.capture(self.vehicle)
        self._has_seen = new_seen is not None
        if self._has_seen:
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
    
    def tick(self):
        self._tick = (self._tick + 1) % self.frame_rate

    def can_move_vehicule(self):
        return self.vehicle.can_move(self.get_last_seen(1).iloc[-1], self.follow_distance , self.turn_distance)

    def step(self):
        if self._tick == 0: self.capture()
        
        last_points = self.get_last_seen(20)
        last_seen = Point.from_df(last_points.iloc[-1])
        incoming, passed = get_incoming(get_spline_df(last_points))
        target = get_target(incoming, last_seen) + Point(self.vehicle.axle_len * 3, 0, 0)
        can_move = self.can_move_vehicule()

        if not can_move:
            a, s = self.vehicle.move(self._frame_time, 0)
            self.write_overwrite(a, s)
        else:
            a, s = self.vehicle.move_to(target, self._frame_time)
            self.write_overwrite(a, s)
        
        # self.vehicle.follow_target(target, last_seen, self._frame_time, self._has_seen)
        self.recenter()
        self.tick()

        return incoming, passed, last_seen, target

