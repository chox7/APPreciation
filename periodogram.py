import numpy as np
def periodogram(s, okno , Fs):
    okno = okno / np.linalg.norm(okno)
    s = s * okno
    N_fft = len(s)
    S = np.fft.rfft(s, N_fft)
    P = S * S.conj()
    P = P.real / Fs
    F = np.fft.rfftfreq(N_fft, 1 / Fs)
    if len(s) % 2 == 0:
        P[1:-1] *= 2
    else:
        P[1:] *= 2
    return (F, P)