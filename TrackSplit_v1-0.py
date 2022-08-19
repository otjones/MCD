## Initialisation

print('')
print('--------------------')
print('Track Splitter V 1.0')
print('--------------------')
print('')
print('Initialising...', end=' ')

from sys import exit
from os import listdir, path, mkdir
from scipy.io import wavfile
from numpy import array, transpose, sqrt, mean, square, zeros
from scipy.signal import fftconvolve as conv

print('done')
print('')

target_track = input('Full path of track to process: ')
out_path = target_track.split('.')[0]
print('')

if path.exists(out_path):
    overwrite = input('Track already has an output folder, continue and overwrite-(y) | exit-(any key): ')
    if overwrite == 'y':
        print('')
        recFs, rec = wavfile.read(target_track)
    else:
        exit()
else:
    recFs, rec = wavfile.read(target_track)
    print('Making output directory...', end='')
    mkdir(out_path)
    print('done')
print('')

num_signals = int(input('Number of sources in recording: ')) #20
time_start = int(input('Time of first signal start: ')) #26
length = int(input('Duration of sweep: ')) #20
gap = int(input('Gap between sweeps: ')) #7
interval = length+gap
buffer = int(gap/2)
print(' ')

sample_start_global = time_start * recFs

for clip in range(num_signals):

    sample_start = sample_start_global + ( clip * interval * recFs ) - ( buffer * recFs )
    sample_end = sample_start + ( length * recFs ) + 2*( buffer * recFs )

    trimmed = rec[sample_start:sample_end,:]
    
    wavfile.write(path.join(out_path, (f'source_{clip}.wav')), recFs, trimmed)
    print(f'Exported clip {clip}')