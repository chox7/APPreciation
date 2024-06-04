import numpy as np
from collections import deque


class HRProcessor:
    def __init__(self, sampling_rate=500, window_size=5):
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.data_buffer = deque(maxlen=sampling_rate * window_size)  

    def add_data(self, new_data):
        # Zakładam, że:
        # kanał 2 posiada sygnał EKG z lewej nogi
        # kanał 1 posiada sygnał EKG z prawej kończyny górnej (nadgarstek lub ramię)
        # EINTHOVEN II = VF - VR
        #eint_2 = -1 * new_data[:,23]
        eint_2 = new_data[:, 2] - new_data[:, 1]
        self.data_buffer.extend(eint_2)
    
    def get_data(self):
        return np.array(self.data_buffer)
    
    def hr(self):
        
        