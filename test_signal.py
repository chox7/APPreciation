import numpy as np
import time

def signal_generator(s):
    for i in range(0, len(s[:,0]), 16):
        time.sleep(0.05)
        yield s[i:i+16, :]

def test_signal(s_path, n_ch, Fs):
    s = np.fromfile(s_path, dtype='<f')
    s = s * 0.0715
    s = np.reshape(s, (len(s)//n_ch, n_ch))
    return signal_generator(s)