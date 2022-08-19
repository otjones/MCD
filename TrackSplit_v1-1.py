## Initialisation

print('')
print('--------------------')
print('Track Splitter V 1.1')
print('--------------------')
print('')
print('Initialising...', end=' ')

from sys import exit
from os import listdir, path, mkdir
from scipy.io import wavfile
from numpy import array, transpose, sqrt, mean, square, zeros, convolve, argmax, ones, power, sin, pi, arange
from scipy.signal import fftconvolve as conv

import warnings
warnings.filterwarnings("ignore")

print('done')
print('')

target_track = input('Full path of track to process: ')
out_path = target_track.split('.')[0]
print('')

if path.exists(out_path):
    overwrite = input('Track already has an output folder, continue and overwrite-(y) | exit-(any key): ')
    if overwrite == 'y':
        recFs, rec = wavfile.read(target_track)
    else:
        exit()
else:
    recFs, rec = wavfile.read(target_track)
    print('Making output directory...', end='')
    mkdir(out_path)
    print('done')
print('')

source_track = input('Full path of original sweep: ')
print('')

num_signals = int(input('Number of sources in recording: '))
length = int(input('Duration of sweep: ')) #20
gap = int(input('Gap between sweeps: ')) #7
search_length = int(input("Time to search for signal start: "))
interval = length+gap
buffer = int(gap/2)
print('')

# Find true 100Hz
print('Finding recording start point...', end=' ')

f = 100
duration = 1/f
window_size = 1000
window = ones(window_size)/float(window_size)

srcFs, srcAud = wavfile.read(source_track)
max_length = int(30*srcFs)
srcSamples = (sin(2*pi*arange(srcFs*duration)*f/srcFs))
srcCon = convolve(srcAud[:max_length], srcSamples)
srcCon_2 = power(srcCon,2)
srcCon_rms = sqrt(convolve(srcCon_2, window, 'valid'))
src_point = argmax(srcCon_rms)/srcFs

# Find recording 100Hz

max_length = int(search_length*recFs)
recSamples = (sin(2*pi*arange(recFs*duration)*f/recFs))
if rec.ndim == 1:
    recCon = convolve(rec[:max_length], recSamples)
elif rec.ndim == 2:
    recCon = convolve(rec[:max_length,1], recSamples)
recCon_2 = power(recCon,2)
recCon_rms = sqrt(convolve(recCon_2, window, 'valid'))
rec_point = argmax(recCon_rms)/recFs

print('OK')

delta = rec_point - src_point
print(f'Signal start: {delta}')
time_start = delta

print(' ')
continue_process = input('Continue with splitting? Yes-(any key) | No-(n)')

if continue_process == 'n':
    exit()
else:

    sample_start_global = int(time_start) * recFs

    for clip in range(num_signals):

        sample_start = sample_start_global + ( clip * interval * recFs ) - ( buffer * recFs )
        sample_end = sample_start + ( length * recFs ) + 2*( buffer * recFs )

        trimmed = rec[sample_start:sample_end,:]
        
        wavfile.write(path.join(out_path, (f'source_{clip}.wav')), recFs, trimmed)
        print(f'Exported clip {clip}')