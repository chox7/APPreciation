import numpy as np
from collections import deque
from scipy.signal import find_peaks
from scipy import interpolate
from scipy.signal import windows

class HRVProcessor:
    def __init__(self, sampling_rate=500, window_size=5, find_peaks_setting=None):
        if find_peaks_setting is None:
            self.find_peaks_setting = {
                'promience': 500,
                'width': [10,100]
            }
        else:
            self.find_peaks_setting = find_peaks_setting

        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.buffor_size = self.sampling_rate * self.window_size
        self.data_buffer = deque(maxlen=self.buffor_size)
        self.time_buffer = np.linspace(0, window_size, self.buffor_size)
        self.last_peak_index = -1 # index of the last peak in the data_buffer in seconds

        self.bmp_size = 100
        self.rr_intervals = deque(maxlen=self.bmp_size-1) 
        self.peaks_time = deque(maxlen=self.bmp_size)
        self.peaks_prominence = deque(maxlen=self.bmp_size)
        self.bpm_list = deque(maxlen=self.bmp_size)
        self.frequencies_list = None
        self.power_list = None

    def add_data(self, new_data):
        self.data_buffer.extend(new_data)
        if len(self.data_buffer) >= self.sampling_rate * self.window_size:
            self.time_buffer += len(new_data) / self.sampling_rate
        self.update_peaks()
        
    def get_data(self):
        return np.array(self.data_buffer), self.time_buffer
    
    def update_peaks(self):
        data = np.array(self.data_buffer)
        if data.size == 0:
            return
        
        peaks, properties = find_peaks(data, 
                                       prominence=self.find_peaks_setting['promience'], 
                                       width=self.find_peaks_setting['width'])
        peaks = np.array(self.time_buffer[peaks])

        if self.last_peak_index >= 0:
            peaks = peaks[peaks > self.last_peak_index + 0.1]
        
        if peaks.size == 0:
            return
        
        if self.peaks_time:
            new_peaks = np.concatenate(([self.peaks_time[-1]], peaks))
        else:
            new_peaks = peaks

        new_rr_intervals = np.diff(new_peaks)
        
        if new_rr_intervals.size > 0:
            self.calculate_bpm(new_rr_intervals)
            self.rr_intervals.extend(new_rr_intervals)

        self.peaks_time.extend(peaks)
        self.peaks_prominence.extend(properties['prominences'])
        self.last_peak_index = peaks[-1]
        self.calculate_hrv()


    def get_peaks(self):    
        return self.peaks_time, self.peaks_prominence
    
    def calculate_bpm(self, new_rr_intervals):
        bpm = 60.0 / new_rr_intervals
        self.bpm_list.extend(bpm)

    def get_bpm(self):
        return np.array(self.bpm_list)
    
    def periodogram(self, s, okno , Fs):
        okno = okno / np.linalg.norm(okno)
        s = s * okno
        N_fft = len(s)
        S = np.fft.rfft(s, N_fft)
        P = S * S.conj()
        P = P.real / Fs
        F = np.fft.rfftfreq(N_fft, 1 / Fs)
        if len(s) % 2 == 0:
            P[1:-1] *= 2
        else:
            P[1:] *= 2
        return (F, P)
        
    def calculate_hrv(self):
        if len(self.rr_intervals) < 10:
            return
        
        peaks = np.array(self.peaks_time)
        RR = np.array(self.rr_intervals) * self.sampling_rate
        RR_new = interpolate.interp1d(peaks[:-1], 1/RR, kind='linear')


        Fs_2 = self.sampling_rate
        t2 = np.arange(self.peaks_time[0], self.peaks_time[-2], 1/Fs_2)
        p = np.polyfit(t2, RR_new(t2), deg=3)
        f = np.polyval(p, t2)
        sig = RR_new(t2) - f
        okno = windows.hann(len(t2))
        F, P = self.periodogram(sig, okno, Fs_2)   
        self.frequencies_list = F
        self.power_list = P

    def get_frequencies(self):
        return np.array(self.frequencies_list)
        
    def get_power(self):
        return np.array(self.power_list)