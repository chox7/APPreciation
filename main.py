import lsl_perun32 as lsl
import h5py
import numpy as np
import matplotlib.pyplot as plt

path = 'dummy_data_120s.hdf'
processing_chunk_size = 1024
chosen_channels = [23, 24, 25, 26, 27, 28, 29]


data = lsl.simulate_aquisition(path, processing_chunk_size)
filts = lsl.initialize_filters(500)

while 1:
    piece = next(data)
    chunk_filtered = lsl.filter_chunk(piece, filts)
    # TUTAJ MOŻESZ KODOWAĆ DALEJ, RESZTY POSTARAJ SIĘ NIE DOTYKAĆ

    '''
    Chunk filtered posiada np.array o kształcie: (processing_chunk_size, liczba_kanałów=32)
    Jest już przefiltrowany
    lsl.simulate_aqusition zwraca generator, za każdym razem jak zadziałasz na niego funkcją next(), dostaniesz kolejny
    chunk danych
    '''