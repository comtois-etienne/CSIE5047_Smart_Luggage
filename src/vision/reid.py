import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import math


def to_hsl(array):
    array = array.astype(np.float32)
    array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    array = cv2.cvtColor(array, cv2.COLOR_BGR2HLS)
    # hls to hsl
    h_layer = array[:, :, 0]
    l_layer = array[:, :, 1]
    s_layer = array[:, :, 2]
    hsl = np.vstack((h_layer, s_layer, l_layer))
    return hsl


def _transform(frame, box, size):
    # base crop of the person
    crop = frame[box['ymin']:box['ymax'], box['xmin']:box['xmax']]

    # get vertical center of the crop
    # width = crop.shape[1]
    # crop = crop[:, width // 4 : width // 4 * 3]

    # line average
    r = cv2.resize(np.mean(crop[:, :, 0], axis=1), (1, size))
    g = cv2.resize(np.mean(crop[:, :, 1], axis=1), (1, size))
    b = cv2.resize(np.mean(crop[:, :, 2], axis=1), (1, size))
    avg = np.array([r, g, b]).T

    # normalize between 0 and 1 with min and max
    avg = (avg - avg.min()) / (avg.max() - avg.min())

    return avg

# root mean square error
def _rmse(truth, test):
    mse = np.square(np.subtract(truth, test)).mean() 
    rmse = math.sqrt(mse)
    return rmse

def _rmse_rgb(truth, reid_vector):
    rmse_red = _rmse(truth[:, 0], reid_vector[:, 0])
    rmse_green = _rmse(truth[:, 1], reid_vector[:, 1])
    rmse_blue = _rmse(truth[:, 2], reid_vector[:, 2])
    total = rmse_red + rmse_green + rmse_blue
    return total / 3

def hue_difference(hue1, hue2):
    diff = np.abs(hue1 - hue2)
    return np.minimum(diff, 360 - diff)

def normalized_rmse(truth, test, scale=360):
    # Normalize Saturation and Lightness
    truth_normalized = truth / scale
    test_normalized = test / scale
    mse = np.square(np.subtract(truth_normalized, test_normalized)).mean() 
    return math.sqrt(mse)

def rmse_hsl(truth, test):
    # Calculate RMSE for Hue with circular consideration
    rmse_hue = math.sqrt(np.square(hue_difference(truth[0], test[0])).mean())
    
    # Calculate RMSE for Saturation and Lightness with normalization
    rmse_saturation = normalized_rmse(truth[1], test[1])
    rmse_lightness = normalized_rmse(truth[2], test[2])

    # Combine the RMSEs (You might want to weigh them differently)
    return rmse_hue + rmse_saturation + rmse_lightness


class ReID:
    truth: np.ndarray
    frame: np.ndarray
    box: pd.DataFrame
    size: int

    def _set_truth(self):
        self.truth = _transform(self.frame, self.box, self.size)

    def __init__(self, frame, box, size):
        self.truth = np.zeros((size, 3))
        self.frame = frame
        self.box = box
        self.size = size
        self._set_truth()

    def reid_score(self, frame, box):
        reid_vector = _transform(frame, box, self.size)
        hue_test = to_hsl(reid_vector)
        hue_truth = to_hsl(self.truth)
        return rmse_hsl(hue_truth, hue_test)
        # hsl_other = to_hsl(reid_vector)
        # print(hsl_other)
        # hsl_truth = to_hsl(self.truth)
        # return _rmse(hsl_truth[0], hsl_other[0]) + _rmse(hsl_truth[1], hsl_other[1])
        # return _rmse_rgb(self.truth, reid_vector)


    def reid(self, frame, objs):
        if objs.empty:
            return None
        scores = objs.apply(lambda x: self.reid_score(frame, x), axis=1)
        return objs.iloc[scores.idxmin()]

