import numpy as np
import time

def signal_generator(s, channel, channel_base, fs, chunk_size):
    try:
        for i in range(0, len(s[:]), chunk_size):
            time.sleep(chunk_size / fs)

            if channel_base == -1:
                if channel == 0:
                    syg = s
                else:
                    syg = s[:, channel]
            else:
                syg = s[:, channel] - s[:, channel_base]

            yield syg[i:i+chunk_size]
    except StopIteration:
        print("End of signal reached")

def test_signal(s_path, n_ch=1, dtype='<f', channel=None, channel_base=None, fs=500, chunk_size=16):
    s = np.fromfile(s_path, dtype=dtype)
    s = s * 0.0715
    if n_ch != 1:
        s = np.reshape(s, (len(s)//n_ch, n_ch))
    return signal_generator(s, channel, channel_base, fs, chunk_size)