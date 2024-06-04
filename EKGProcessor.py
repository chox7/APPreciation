import numpy as np
from collections import deque


class HRProcessor:
    def __init__(self, sampling_rate=500, window_size=5):
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.data_buffer = deque(maxlen=sampling_rate * window_size)  # Buffer to hold last 10 seconds of data

    def add_data(self, new_data):
        eint_1 = new_data[:, 2] - new_data[:, 1]
        self.data_buffer.extend(eint_1)
    
    def get_data(self):
        return np.array(self.data_buffer)