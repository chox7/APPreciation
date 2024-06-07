import numpy as np
from collections import deque
from scipy.signal import find_peaks


class HRVProcessor:
    def __init__(self, sampling_rate=500, window_size=5):
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.data_buffer = deque(maxlen=sampling_rate * window_size)
        self.rr_intervals = deque(maxlen=5) # 5 last rr intervals
        self.time_buffer = np.linspace(0, window_size, sampling_rate * window_size)
        self.last_peak_index = -1 # index of the last peak in the data_buffer in seconds
        self.peaks_time = deque(maxlen=5)
        self.peaks_prominence = deque(maxlen=5)
        self.bpm_list = deque(maxlen=10)

    def add_data(self, new_data):
        self.data_buffer.extend(new_data)
        if len(self.data_buffer) >= self.sampling_rate * self.window_size:
            self.time_buffer += len(new_data) / self.sampling_rate

        self.peaks()
        
    def get_data(self):
        return np.array(self.data_buffer), self.time_buffer
    
    def get_peaks(self):    
        return self.peaks_time, self.peaks_prominence
    
    def peaks(self):
        data = np.array(self.data_buffer)
        if len(data) > 0:
            peaks, properties = find_peaks(data, prominence=500, width=[10,100])
            peaks = self.time_buffer[peaks]
            if self.last_peak_index >= 0:
                peaks = peaks[peaks > self.last_peak_index]
            
            if peaks.size > 0:
                self.peaks_time.extend(peaks)
                self.peaks_prominence.extend(properties['prominences'])
                self.last_peak_index = peaks[-1]
                rr_interval = np.diff(self.peaks_time)
                self.rr_intervals.extend(rr_interval)
                self.calculate_bpm()
                
    def calculate_bpm(self):
        if len(self.rr_intervals) < 5:
            return
    
        avg_rr_interval = np.mean(self.rr_intervals)
        bpm = int(60.0 / avg_rr_interval)
        self.bpm_list.extend([bpm])
    
    def get_bpm(self):
        return np.array(self.bpm_list)