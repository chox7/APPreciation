import lsl_perun32 as lsl
import EKGProcessor as ekgp
import EKGapp as ekgapp
import threading
import test_signal as ts

def main():
    #path = 'dummy_data_120s.hdf'
    #processing_chunk_size = 1024
    #chosen_channels = [23, 24, 25, 26, 27, 28, 29]
    #data = lsl.simulate_aquisition(path, processing_chunk_size)

    data = ts.test_signal()
    Fs = 2048
    filts = lsl.initialize_filters(Fs)
    HR = ekgp.HRVProcessor(sampling_rate=Fs, window_size=1)

    data_thread = threading.Thread(target=ekgapp.add_data_continuously, args=(HR, data, filts))
    data_thread.setDaemon(True)
    data_thread.start()

    ekgapp.run_dash_app_thread(HR)

if __name__ == '__main__':
    main()