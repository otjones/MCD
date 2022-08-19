from sys import exit
from os import listdir, path, mkdir
from scipy.io import wavfile
from numpy import array, transpose, sqrt, mean, square, pad, append, power, ones, convolve
from scipy.signal import fftconvolve as conv
from matplotlib import pyplot as plt
import numpy as np

def getFPoint(freq, audio_path):

    fs, aud = wavfile.read(audio_path)
    f = freq
    duration = 1/f
    max_length = 30*fs

    samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

    if aud.ndim == 1:
        con = np.convolve(aud[:max_length], samples)
    elif aud.ndim == 2:
        con = np.convolve(aud[:max_length,1], samples)

    window_size = 1000
    window = ones(window_size)/float(window_size)
    con_2 = power(con,2)
    con_rms = sqrt(convolve(con_2, window, 'valid'))

    return np.argmax(con_rms)/fs

rec_point = getFPoint(100, '/Users/oscarjones/Documents/Greenwich/Field_Test/Great_Hall_Setup_2/01-em32_Great_Hall_Balcony_1746.wav')
src_point = getFPoint(100, '/Users/oscarjones/Documents/Greenwich/Field_Test/sweep-22.wav')

print(rec_point, src_point)

delta = rec_point - src_point

print(f'Delay: {delta}')