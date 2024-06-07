import lsl_perun32 as lsl
import EKGProcessor as ekgp
import EKGapp as ekgapp
import threading
import test_signal as ts

def main():
    path = 'dummy_data_120s.hdf'
    processing_chunk_size = 1024
    chosen_channels = [23, 24, 25, 26, 27, 28, 29]
    #data = lsl.simulate_aquisition(path, processing_chunk_size)

    data = ts.test_signal()
    filts = lsl.initialize_filters(500)
    HR = ekgp.HRVProcessor(sampling_rate=2048, window_size=1)

    data_thread = threading.Thread(target=ekgapp.add_data_continuously, args=(HR, data, filts))
    data_thread.start()

    app = ekgapp.run_dash_app(HR)
    app.run_server(debug=True, port=8051)

if __name__ == '__main__':
    main()