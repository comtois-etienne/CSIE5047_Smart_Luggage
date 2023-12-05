from src.point import Point
from dataclasses import dataclass
import pandas as pd


@dataclass
class FakeSensor:
    positions: pd.DataFrame
    tick: int = 0

    def capture(self, vehicle):
        index = self.tick if self.tick < len(self.positions) else len(self.positions) - 1
        self.tick += 1
        new_seen = Point.from_df(self.positions.iloc[index])
        if not vehicle.sees(new_seen):
            new_seen = None
        return new_seen
    
    def time(self):
        return self.tick
    
    def index(self):
        return min(self.tick, len(self.positions) - 1)
    
    def reset(self):
        self.tick = 0

    def is_done(self):
        return self.tick >= len(self.positions)
    
    def get_host_position(self):
        return Point.from_df(self.positions.iloc[self.index()])
    
    def scatter_host(self, ax, vehicle=None):
        host_position = self.get_host_position()
        host_visible = True if vehicle is None else vehicle.sees(host_position)
        h_color, label = ('g', 'visible') if host_visible else ('r', 'not visible')
        host_position.scatter(ax, color=h_color, size=20, label=label)
