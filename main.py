import lsl_perun32 as lsl
import EKGProcessor as ekgp
import EKGapp as ekgapp
import threading
import test_signal as ts

def main():
    #path = 'dummy_data_120s.hdf'
    #processing_chunk_size = 256
    #chosen_channels = [23, 24, 25, 26, 27, 28, 29]
    #data = lsl.simulate_aquisition(path, processing_chunk_size)

    data = ts.test_signal()
    Fs = 500
    filts = lsl.initialize_filters(Fs)
    processor = ekgp.SignalProcessor(sampling_rate=Fs, buffor_size_seconds=5)
    peaks_detector =  ekgp.PeaksDetector(processor)
    hrv_analyzer = ekgp.HRVAnalyzer(peaks_detector)

    data_thread = threading.Thread(target=ekgapp.add_data_continuously, args=(processor, data, filts))
    data_thread.start()

    ekgapp.run_dash_app_thread(processor, peaks_detector, hrv_analyzer)

if __name__ == '__main__':
    main()