from collections import deque
from scipy import signal, interpolate, integrate
import threading
import numpy as np
import time

class SignalProcessor:
    """Class for processing EKG signal. It filters the signal and stores it in a buffer."""

    def __init__(self, inlet, samps_per_chunk=16, sampling_rate=500, buffor_size_seconds=5, hp_params=None, lp_params=None, notch_params=None, mode='online', channel=23):
        self.inlet = inlet
        self.samps_per_chunk = samps_per_chunk
        self.sampling_rate = sampling_rate
        self.buffor_size = self.sampling_rate * buffor_size_seconds
        self.data_buffer = deque(maxlen=self.buffor_size)
        self.time_buffer = deque(maxlen=self.buffor_size)
        self.current_time = 0
        self.channel = channel
        self.mode = mode

        if self.mode == 'offline':
            print("Running in offline mode")

        else:
            print("Running in online mode")

        # Set filters params
        if hp_params is None:
            self.hp_params = {'order': 3, 'fc': 0.67, 'rp': 0.5, 'rs': 3}
        if lp_params is None:    
            self.lp_params = {'order': 4, 'fc': 150, 'rp': None, 'rs': 3}
        if notch_params is None:    
            self.notch_params = {'f0': 50, 'Q': 10}

        # Initialize filters
        self.update_filters()

        # Synchronization and threading
        self.data_lock = threading.Lock()
        self.running = False

    def update_filters(self):
        # High-pass filter
        self.b_h, self.a_h = signal.iirfilter(self.hp_params['order'], self.hp_params['fc'],
                                          self.hp_params['rp'], self.hp_params['rs'],
                                          btype='highpass', ftype='butter', output='ba', fs=self.sampling_rate)
        self.zi_h = signal.lfilter_zi(self.b_h, self.a_h)

        # Low-pass filter
        self.b_l, self.a_l = signal.iirfilter(self.lp_params['order'], self.lp_params['fc'],
                                          self.lp_params['rp'], rs=self.lp_params['rs'],
                                          btype='lowpass', ftype='butter', output='ba', fs=self.sampling_rate)
        self.zi_l = signal.lfilter_zi(self.b_l, self.a_l)

        # Notch filter
        self.b_n, self.a_n = signal.iirnotch(self.notch_params['f0'], Q=self.notch_params['Q'], fs=self.sampling_rate)
        self.zi_n = signal.lfilter_zi(self.b_n, self.a_n)

    def set_highpass_params(self, order, fc, rp, rs):
        self.hp_params['order'] = order
        self.hp_params['fc'] = fc
        self.hp_params['rp'] = rp
        self.hp_params['rs'] = rs
        self.update_filters()

    def set_lowpass_params(self, order, fc, rp, rs):
        self.lp_params['order'] = order
        self.lp_params['fc'] = fc
        self.lp_params['rp'] = rp
        self.lp_params['rs'] = rs
        self.update_filters()

    def set_notch_params(self, f0, Q):
        self.notch_params['f0'] = f0
        self.notch_params['Q'] = Q
        self.update_filters()

    def add_data_continuously(self):
        while self.running:
            if self.mode == 'online':
                sample, _ = self.inlet.pull_chunk(timeout=1.0, max_samples=self.samps_per_chunk)
                if sample:
                    piece = np.array(sample)[:, self.channel]
            elif self.mode == 'offline':
                piece = np.array(next(self.inlet))
            
            self.add_data(piece)    

    def add_data(self, new_data):
        with self.data_lock:
            filtered_data = self.filter_data(new_data)
            self.data_buffer.extend(filtered_data)
            for _ in range(len(new_data)):
                self.current_time += 1 / self.sampling_rate
                self.time_buffer.append(self.current_time)

    def get_data(self):
        with self.data_lock:
            return np.array(self.data_buffer), np.array(self.time_buffer)
    
    def filter_data(self, new_data):
        filtered_data, self.zi_h = signal.lfilter(self.b_h, self.a_h, new_data, zi=self.zi_h)
        filtered_data, self.zi_l = signal.lfilter(self.b_l, self.a_l, filtered_data, zi=self.zi_l)
        filtered_data, self.zi_n = signal.lfilter(self.b_n, self.a_n, filtered_data, zi=self.zi_n)
        return filtered_data
    
    def reset_buffers(self):
        with self.data_lock:
            self.data_buffer.clear()
            self.time_buffer.clear()
            self.current_time = 0

    def start(self):
        if not self.running:
            self.reset_buffers()
            self.running = True
            self.data_thread = threading.Thread(target=self.add_data_continuously)
            self.data_thread.start()

    def stop(self):
        self.running = False
        self.data_thread.join()

class PeaksDetector:
    def __init__(self, signal_processor, find_peaks_setting=None):
        self.signal_processor = signal_processor
        if find_peaks_setting is None:
            self.find_peaks_setting = {
                'prominence': 1000,
                'width': [10, 100],
                'height': 500,
                'distance': 200
            }
        else:
            self.find_peaks_setting = find_peaks_setting

        self.last_peak_index = -1 # index of the last peak in the data_buffer in seconds
        self.peak_buffor_size = 500
        self.rr_intervals = deque(maxlen=self.peak_buffor_size-1) 
        self.peaks_time = deque(maxlen=self.peak_buffor_size)
        self.peaks_prominence = deque(maxlen=self.peak_buffor_size)
        self.bpm_list = deque(maxlen=self.peak_buffor_size)

        # Synchronization and threading
        self.peaks_lock = threading.Lock()
        self.bpm_lock = threading.Lock()
        self.running = False

    def update_peaks_thread(self):
        while self.running:
            self.update_peaks()
            time.sleep(1)

    def update_peaks(self):
        with self.signal_processor.data_lock:
            data = np.array(self.signal_processor.data_buffer)
            time_buffer = np.array(self.signal_processor.time_buffer)

        if data.size == 0:
            return
        
        if self.last_peak_index >= 0:
            valid_mask = time_buffer > self.last_peak_index + 0.2
            data = data[valid_mask]
            time_buffer = time_buffer[valid_mask]

        if data.size == 0:
            return
        
        peaks, properties = signal.find_peaks(data, 
                                       prominence=self.find_peaks_setting['prominence'], 
                                       width=self.find_peaks_setting['width'],
                                       height=self.find_peaks_setting['height'])
        
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
                self.rr_intervals.extend(new_rr_intervals)

            self.peaks_time.extend(peaks)
            self.peaks_prominence.extend(properties['prominences'])
            self.last_peak_index = peaks[-1]

    def get_peaks(self):   
        with self.peaks_lock: 
            return np.array(self.peaks_time), np.array(self.peaks_prominence)
    
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
            self.bpm_list.extend([np.mean(bpm)])

    def get_bpm(self):
        with self.bpm_lock:
            return np.array(self.bpm_list)
    
    def reset_peaks(self):
        with self.peaks_lock:
            self.peaks_time.clear()
            self.peaks_prominence.clear()
            self.rr_intervals.clear()
            self.bpm_list.clear()
            self.last_peak_index = -1

    def start(self):
        if not self.running:
            self.reset_peaks()
            self.running = True
            self.peaks_thread = threading.Thread(target=self.update_peaks_thread)
            self.bpm_thread = threading.Thread(target=self.calculate_bpm_thread)
            self.peaks_thread.start()
            self.bpm_thread.start()

    def stop(self):
        self.running = False
        self.peaks_thread.join()
        self.bpm_thread.join()


class HRVAnalyzer:
    def __init__(self, peaks_detector):
        self.peaks_detector = peaks_detector
        self.frequencies = None
        self.power = None
        self.coherence = None
        self.x_coherence = np.linspace(-4, 4, 1000)

        # Synchronization and threading
        self.hrv_lock = threading.Lock()
        self.coh_lock = threading.Lock()
        self.running = False

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
            time.sleep(1)

    def calculate_hrv(self):
        with self.peaks_detector.peaks_lock:
            if len(self.peaks_detector.rr_intervals) < 10:
                return
            peaks = np.array(self.peaks_detector.peaks_time)
            RR = np.array(self.peaks_detector.rr_intervals) * self.peaks_detector.signal_processor.sampling_rate
            RR_new = interpolate.interp1d(peaks[:-1], 1/RR, kind='linear')

        Fs_2 = 1
        t2 = np.arange(peaks[0], peaks[-2], 1/Fs_2)
        p = np.polyfit(t2, RR_new(t2), deg=3)
        f = np.polyval(p, t2)
        sig = RR_new(t2) - f
        k = 20
        okno = signal.windows.hann(k *len(t2))

        zero_padding_lenght = k * len(sig)
        sig_padded = np.pad(sig, (0, zero_padding_lenght - len(sig)), 'constant')
        F, P = self.periodogram(sig_padded, okno, Fs_2)   
        
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
            time.sleep(1)

    def calculate_coherence(self):
        with self.hrv_lock:
            if self.frequencies is None:
                return
            F = np.array(self.frequencies)
            P = np.array(self.power)

        mask1 = (F > 0.04) & (F < 0.26)
        F1 = F[mask1]
        P1 = P[mask1]
        highest_peak_index = np.argmax(P1)
        highest_peak_frame = [F1[highest_peak_index] - 0.015, F1[highest_peak_index] + 0.015]
        highest_peak_arr = (F1 > highest_peak_frame[0]) & (F1 < highest_peak_frame[1])
        peak_power = integrate.simps(P1[highest_peak_arr], F1[highest_peak_arr])

        mask2 = (F > 0.0033) & (F < 0.4)
        F2 = F[mask2]
        P2 = P[mask2]
        total_power = integrate.simps(P2, F2)           
        coherence_value  = (peak_power/(total_power - peak_power))**2

        with self.coh_lock:
            self.coherence = ((1 / (np.sqrt(2 * np.pi))) * np.exp(-(self.x_coherence**2) / 2))
            self.coherence /= np.max(self.coherence)
            self.coherence *= coherence_value

    def get_coherence(self):
        with self.coh_lock:
            return (np.array(self.x_coherence), np.array(self.coherence))

    def reset_hrv(self):
        with self.hrv_lock:
            self.frequencies = None
            self.power = None
            self.coherence = None

    def start(self):
        if not self.running:
            self.reset_hrv()
            self.running = True
            self.hrv_thread = threading.Thread(target=self.calculate_hrv_thread)
            self.coh_thread = threading.Thread(target=self.calculate_coherence_thread)
            self.hrv_thread.start()
            self.coh_thread.start()

    def stop(self):
        self.running = False
        self.hrv_thread.join()
        self.coh_thread.join()
        