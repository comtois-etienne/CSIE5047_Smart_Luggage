from src.point import Point
from dataclasses import dataclass
import pandas as pd

COLUMNS = ['t', 'x', 'y', 'd', 'a']

@dataclass
class Sensor:
    file_path: str
    refresh_rate: int = 2
    tick: int = 0
    has_seen: bool = False
    positions: pd.DataFrame = pd.DataFrame(columns=COLUMNS)

    def __post_init__(self):
        self.positions = pd.concat([self.positions, pd.DataFrame({
            't': 0, # timestamp
            'x': 0, # x position
            'y': 0, # y position
            'd': 0, # distance
            'a': 0, # angle
        }, index=[len(self.positions)])])

    def read_csv(self):
        point_df = pd.read_csv(self.file_path, header=None)
        point_df.columns = COLUMNS
        if point_df.iloc[-1]['x'] == -100 and point_df.iloc[-1]['y'] == 0:
            self.has_seen = False
        else:
            self.has_seen = True
            self.positions = pd.concat([self.positions, point_df])

    def capture(self, vehicle):
        self.tick += 1
        self.read_csv()
        new_seen = None
        if self.has_seen:
            new_seen = Point.from_df(self.positions.iloc[-1])
        return new_seen
    
    def recenter(self, vehicle):
        front: Point = vehicle.get_front()
        self.positions = front.rotate_df(front.a, self.positions, recenter=True)

    def time(self):
        return self.tick
    
    def index(self):
        return self.tick
    
    def reset(self):
        self.tick = 0

    def is_done(self):
        return False

    def scatter_host(self, ax, vehicle=None):
        host_position = Point.from_df(self.positions.iloc[-1])
        h_color, label = ('g', 'visible') if self.has_seen else ('r', 'position unknown')
        host_position.scatter(ax, color=h_color, size=20, label=label)

