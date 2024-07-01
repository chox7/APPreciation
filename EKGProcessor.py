import numpy as np
from collections import deque
from scipy.signal import find_peaks
from scipy import interpolate
from scipy.signal import windows
from scipy import integrate
import threading
import time

class HRVProcessor:
    def __init__(self, sampling_rate=500, window_size=5, find_peaks_setting=None):
        if find_peaks_setting is None:
            self.find_peaks_setting = {
                'prominence': 500,
                'width': [10,100]
            }
        else:
            self.find_peaks_setting = find_peaks_setting

        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.buffor_size = self.sampling_rate * self.window_size
        self.data_buffer = deque(maxlen=self.buffor_size)
        self.time_buffer = deque(maxlen=self.buffor_size)
        self.current_time = 0
        self.last_peak_index = -1 # index of the last peak in the data_buffer in seconds

        self.bmp_size = 300
        self.rr_intervals = deque(maxlen=self.bmp_size-1) 
        self.peaks_time = deque(maxlen=self.bmp_size)
        self.peaks_prominence = deque(maxlen=self.bmp_size)
        self.bpm_list = deque(maxlen=self.bmp_size)
        self.frequencies = None
        self.power = None
        self.coherence = deque(maxlen=1000)
        self.x_coherence = np.linspace(-4, 4, 1000)

        # Synchronization
        self.data_lock = threading.Lock()
        self.peaks_lock = threading.Lock()
        self.bpm_lock = threading.Lock()
        self.hrv_lock = threading.Lock()
        self.coh_lock = threading.Lock()

        # Threads
        self.running = True
        self.peaks_thread = threading.Thread(target=self.update_peaks_thread)
        self.bpm_thread = threading.Thread(target=self.calculate_bpm_thread)
        self.hrv_thread = threading.Thread(target=self.calculate_hrv_thread)
        self.coh_thread = threading.Thread(target=self.calculate_coherence_thread)

        self.peaks_thread.start()
        self.bpm_thread.start()
        self.hrv_thread.start()
        self.coh_thread.start()

    def add_data(self, new_data):
        with self.data_lock:
            self.data_buffer.extend(new_data)
            for _ in range(len(new_data)):
                self.current_time += 1 / self.sampling_rate
                self.time_buffer.append(self.current_time)
        
    def get_data(self):
        with self.data_lock:
            return np.array(self.data_buffer), np.array(self.time_buffer)

    def update_peaks_thread(self):
        while self.running:
            self.update_peaks()
            time.sleep(1)   

    def update_peaks(self):
        with self.data_lock:
            data = np.array(self.data_buffer)
            time_buffer = np.array(self.time_buffer)

        if data.size == 0:
            return
        
        if self.last_peak_index >= 0:
            valid_mask = time_buffer > self.last_peak_index + 0.1
            data = data[valid_mask]
            time_buffer = time_buffer[valid_mask]

        if data.size == 0:
            return
        
        peaks, properties = find_peaks(data, 
                                       prominence=self.find_peaks_setting['prominence'], 
                                       width=self.find_peaks_setting['width'])
        
        if peaks.size == 0:
            return 
        
        peaks = time_buffer[peaks]

        with self.peaks_lock:
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

    def get_peaks(self):   
        with self.peaks_lock: 
            return self.peaks_time, self.peaks_prominence
    
    def calculate_bpm_thread(self):
        while self.running:
            with self.peaks_lock:
                new_rr_intervals = list(self.rr_intervals)[-5:]
            self.calculate_bpm(new_rr_intervals)
            time.sleep(1)

    def calculate_bpm(self, new_rr_intervals):
        if not len(new_rr_intervals):
            return
        bpm = 60.0 / np.array(new_rr_intervals)
        with self.bpm_lock:
            self.bpm_list.extend(bpm)

    def get_bpm(self):
        with self.bpm_lock:
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
    
    def calculate_hrv_thread(self):
        while self.running:
            self.calculate_hrv()
            time.sleep(5)

    def calculate_hrv(self):
        with self.peaks_lock:
            if len(self.rr_intervals) < 10:
                return
            peaks = np.array(self.peaks_time)
            RR = np.array(self.rr_intervals) * self.sampling_rate
            RR_new = interpolate.interp1d(peaks[:-1], 1/RR, kind='linear')

        Fs_2 = 1
        t2 = np.arange(self.peaks_time[0], self.peaks_time[-2], 1/Fs_2)
        p = np.polyfit(t2, RR_new(t2), deg=2)
        f = np.polyval(p, t2)
        sig = RR_new(t2) - f
        okno = windows.hann(len(t2))
        F, P = self.periodogram(sig, okno, Fs_2)   
        with self.hrv_lock:
            self.frequencies = F
            self.power = P  

    def get_frequencies(self):
        with self.hrv_lock: 
            return np.array(self.frequencies)
        
    def get_power(self):
        with self.hrv_lock: 
            return np.array(self.power)
    

    def calculate_coherence_thread(self):
        while self.running:
            self.calculate_coherence()
            time.sleep(5)

    def calculate_coherence(self):
        with self.coh_lock:
            if self.frequencies is None:
                return
            F = self.get_frequencies()
            P = self.get_power()

            mask1 = (F > 0.04) & (F < 0.26)
            F1 = F[mask1]
            P1 = P[mask1]
            highest_peak_index = np.argmax(P1)
            highest_peak_frame = [P1[highest_peak_index] - 0.015, P1[highest_peak_index] + 0.015]
            highest_peak_arr = (P1 > highest_peak_frame[0]) & (P1 < highest_peak_frame[1])
            peak_power = integrate.simps(P1[highest_peak_arr], F1[highest_peak_arr])

            mask2 = (F > 0.0033) & (F < 0.4)
            F2 = F[mask2]
            P2 = P[mask2]
            total_power = integrate.simps(P2, F2)           
            coherence_value  = (peak_power/(total_power-peak_power))**2
            self.coherence = ((1 / (np.sqrt(2 * np.pi))) * np.exp(-(self.x_coherence**2) / 2))
            self.coherence /= np.max(self.coherence)
            self.coherence *= coherence_value

    def get_coherence(self):
        with self.coh_lock:
            return (np.array(self.x_coherence), np.array(self.coherence))

    def stop(self):
        self.running = False
        self.peaks_thread.join()
        self.bpm_thread.join()
        self.hrv_thread.join()
        self.coh_thread.join()