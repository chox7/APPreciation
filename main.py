import lsl_perun32 as lsl
import EKGProcessor as ekgp
import EKGapp as ekgapp
import threading
import test_signal as ts

def main():
    inlet = lsl.start_stream('stream_1', 500)
    Fs = 500

    processor = ekgp.SignalProcessor(sampling_rate=Fs, buffor_size_seconds=5)
    peaks_detector =  ekgp.PeaksDetector(processor)
    hrv_analyzer = ekgp.HRVAnalyzer(peaks_detector)

    data_thread = threading.Thread(target=ekgapp.add_data_continuously, args=(inlet, 500, processor))
    data_thread.start()

    ekgapp.run_dash_app_thread(processor, peaks_detector, hrv_analyzer)

if __name__ == '__main__':
    main()