import numpy as np
import time

def signal_generator(s):
    for i in range(0, len(s[:,0]), 16):
        time.sleep(0.005)
        # Zakładam, że:
        # kanał 2 posiada sygnał EKG z lewej nogi
        # kanał 1 posiada sygnał EKG z prawej kończyny górnej (nadgarstek lub ramię)
        # EINTHOVEN II = VF - VR
        #eint_2 = -1 * new_data[:,23]
        eint_2 = s[:, 2] - s[:, 1]
        yield eint_2[i:i+16]

def test_signal():
    n_ch = 3
    s_path = 'wysilek.obci.raw'
    s = np.fromfile(s_path, dtype='<f')
    s = s * 0.0715
    s = np.reshape(s, (len(s)//n_ch, n_ch))
    return signal_generator(s)