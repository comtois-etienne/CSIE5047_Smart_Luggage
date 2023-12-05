from .point import Point
from .point import normalize_angle

from IPython.display import clear_output
import matplotlib.pyplot as plt


def create_map(center=Point(0,0), size=5000, figsize=6):
    x, y = center.x, center.y
    hs = size // 2
    clear_output(wait=True)
    fig, ax = plt.subplots()
    ax.set_ylim([y - hs, y + hs])
    ax.set_xlim([x - hs, x + hs])
    fig.set_figheight(figsize)
    fig.set_figwidth(figsize)
    return fig, ax


__all__ = [
    'Point',
    'normalize_angle',
    'create_map'
]

