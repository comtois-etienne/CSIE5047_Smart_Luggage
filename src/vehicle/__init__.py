from .vehicle import Vehicle
from .mover import VehicleMover


MD_FILE_PATH = 'io/md.csv'

def reset_md_file(file_path):
    md = VehicleMover(None, None, file_path)
    md.write_overwrite(0, 0)


__all__ = [
    'Vehicle', 
    'VehicleMover',
    'reset_md_file',
    'MD_FILE_PATH',
]

