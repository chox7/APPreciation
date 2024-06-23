import numpy as np
from collections import deque
from scipy.signal import find_peaks
from scipy import interpolate
from periodogram import periodogram
from scipy.signal import windows
from scipy import integrate

class HRVProcessor:
    def __init__(self, sampling_rate=500, window_size=5):
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.data_buffer = deque(maxlen=sampling_rate * window_size)
        self.rr_intervals = deque(maxlen=20) # 5 last rr intervals
        self.time_buffer = np.linspace(0, window_size, sampling_rate * window_size)
        self.last_peak_index = -1 # index of the last peak in the data_buffer in seconds
        self.peaks_time = deque(maxlen=21)
        self.peaks_prominence = deque(maxlen=10)
        self.bpm_list = deque(maxlen=20)
        self.time_list = deque(maxlen=20)
        self.frequencies = deque(maxlen=20)
        self.power = deque(maxlen=20)
        self.coherence = deque(maxlen=1000)

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
                self.calculate_hrv()
                self.calculate_coherence()
                
    def calculate_bpm(self):
        if len(self.rr_intervals) < 1:
            return
    
        avg_rr_interval = np.mean(self.rr_intervals)
        bpm = int(60.0 / avg_rr_interval)
        self.bpm_list.extend([bpm])

        #hrv
        time = [self.peaks_time[i]/500 for i in range(len(self.peaks_time)-1)]
        self.time_list = time

    def get_bpm(self):
        return np.array(self.bpm_list)
    
    def calculate_hrv(self):
        if len(self.rr_intervals) < 5:
            return
        bpm = self.bpm_list
        time = self.time_list
        RR_new = interpolate.interp1d(time, bpm, kind='linear')
        sig = RR_new(time)

        # tutaj trzeba odjąć wielomian...
        '''T = ?
        t2 = np.arange(1,T,1)
        p = np.polyfit(t2, RR_new(t2), 2)
        f = np.polyval(p,t2)
        sig = RR_new(t2) - f'''

        # odejmę stałą, bo wielomian mi nie wychodzi
        sig = sig - np.mean(sig)

        okno = windows.hann(len(time))
        (F, P) = periodogram(sig, okno, 1)    
        self.frequencies = F
        self.power = P

    def get_frequencies(self):
        return np.array(self.frequencies)
        
    def get_power(self):
        return np.array(self.power)
    

    ''' frequencies: [0.   0.05 0.1  0.15 0.2  0.25 0.3  0.35 0.4  0.45 0.5 ] '''
    
    def calculate_coherence(self):
        if len(self.frequencies) < 9:
            return
        
        total_power = integrate.simps(self.frequencies[1:-2])
        highest_peak_index = np.argmax(self.frequencies[1:6])
        peak_power = integrate.simps(self.frequencies[(highest_peak_index-1):(highest_peak_index+1)])
        coherence_value  = (peak_power/(total_power-peak_power))**2
        sigma = 1
        mu=0
        x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        self.coherence = ((1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-((x - mu)**2) / (2 * sigma**2)))/0.4*coherence_value

    def get_coherence(self):
        return np.array(self.coherence)