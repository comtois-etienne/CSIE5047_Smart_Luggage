from .vehicle import Vehicle
from src.vision import FakeSensor

from dataclasses import dataclass


follow_distance = 1200
sharp_distance = 800

@dataclass
class VehicleMover:
    vehicule: Vehicle
    sensor: FakeSensor

    

    
