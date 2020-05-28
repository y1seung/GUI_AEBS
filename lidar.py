
from rplidar import RPLidar
import numpy as np

LIDAR_PORT_NAME = 'COM11'
lidar = RPLidar(LIDAR_PORT_NAME)
iterator = lidar.iter_scans(max_buf_meas=2000, min_len=0)

def get_value_list():

    scan = next(iterator)
    offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])


    return offsets

