from pylsl import StreamInlet, resolve_stream
import time
import h5py
import numpy as np
import scipy.signal as ss

# NIE RUSZAĆ!


def start_stream(save_path, stream_name, samps_per_chunk):
    '''
    Rozpoczęcie streamu z Peruna 32.
    :param save_path: Ścieżka zapisu danych
    :param stream_name: Nazwa streamu, taka sama jaką użyto w svarog_streamer
    :param samps_per_chunk: Liczba próbek na odebrany chunk.
    :return:
    '''
    # znajdujemy streamy
    print("Looking for Perun32 streams...")
    streams = resolve_stream('type', 'EEG')

    selected_stream = None
    for stream in streams:
        if stream.name() in stream_name:
            selected_stream = stream
            print("Stream has been found")
    if selected_stream is None:
        print("Nie znalesiono streamu", stream_name, "w liście", [i.name() for i in streams])
        exit()

    inlet = StreamInlet(selected_stream)

    # Zapis danych w formacie .hdf
    with h5py.File(save_path, "a") as fil:
        i = 0
        time_beg = time.monotonic()
        while True:
            fil.create_group(str(i))
            # pobieramy próbki (w mikrowoltach)
            sample, timestamp = inlet.pull_chunk(timeout=1.0, max_samples=samps_per_chunk)
            samps = np.array(sample)
            times = np.array(timestamp)
            fil[str(i)].create_dataset('samples', data=samps, dtype=float)
            fil[str(i)].create_dataset('timestamp', data=times, dtype=float)
            print(len(sample), len(timestamp), time.monotonic())
            time_curr = time.monotonic()
            if time_curr-time_beg > 120:
                break
            i += 1


def simulate_aquisition(path, processing_chunk_size):
    with h5py.File(path, "r") as fil:
        processing_chunk = np.zeros((processing_chunk_size, 32))
        print(np.shape(processing_chunk))
        last_n = 0
        raw_chunk_size = 0

        cnt = 0
        for chunk_id in fil.keys():
            if raw_chunk_size == 0:
                raw_chunk_size = len(fil[chunk_id]['samples'][:][:, 1])
                print(fil[chunk_id]['timestamp'][1]-fil[chunk_id]['timestamp'][0])
                # print(raw_chunk_size)
            start, stop = last_n, last_n+raw_chunk_size
            if start < processing_chunk_size-1 and stop <= processing_chunk_size:
                processing_chunk[start:stop, :] = 0.0715 * fil[chunk_id]['samples'][:][:, :]
                last_n = stop
            else:
                time.sleep(0.5)
                yield processing_chunk
                processing_chunk = np.empty((processing_chunk_size, 32), dtype=float)
                last_n = 0
                cnt += 1


def initialize_filters(fs=500):
    # HP
    order = 3
    fc = 0.67
    rp = 0.5
    rs = 3
    hp = ss.iirfilter(order, fc, rp, rs, btype='highpass', ftype='butter', output='ba', fs=fs)
    # LP
    order = 4
    fc = 150
    rs = 3
    lp = ss.iirfilter(order, fc, rs=rs, btype='lowpass', ftype='butter', output='ba', fs=fs)
    # notch
    notch = ss.iirnotch(50, Q=50/5, fs=fs)
    fil = [hp, lp, notch]
    return fil


def filter_chunk(sig, filters):
    for params in filters:
        b, a = params
        sig = ss.filtfilt(b, a, sig, axis=0)
    return sig
