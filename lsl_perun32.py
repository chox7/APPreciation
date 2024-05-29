from pylsl import StreamInlet, resolve_stream
import time
import h5py
import numpy as np


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


def load_data(path):
    '''
    Bardzo proste otwieranie danych.
    :param path: Wczytywana ścieżka.
    :return:
    '''
    with h5py.File(path, "r") as fil:
        for chunk_id in fil.keys():
            samps = fil[chunk_id]['samples'][:]
            times = fil[chunk_id]['timestamp'][:]

            print(np.shape(samps), np.shape(times))

