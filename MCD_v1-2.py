## Initialisation

print('')
print('-------------------------------')
print('Multi-Channel Deconvolver V 1.2')
print('-------------------------------')
print('')
print('Initialising...', end=' ')

from sys import exit
from os import listdir, path, mkdir
from scipy.io import wavfile
from numpy import array, transpose, sqrt, mean, square, pad, append, power, ones, convolve
from scipy.signal import fftconvolve as conv
from matplotlib import pyplot as plt

print('done')
print('')

target_folder = input('Full path of folder to process: ')
root_name = 'impulse'

print('')

if not target_folder:
    print('Folder required, closing...')
    exit()

print(f'Scanning "{target_folder}" for .wav files...', end=' ')

files = [f for f in listdir(target_folder) if path.isfile(path.join(target_folder, f))]
listing = []

for file in files:
    if '.wav' in file:
        if 'inv.wav' != file:
            listing.append(file)

number_files = len(listing)
print(f'{number_files} found')

print('Checking output directory...', end=' ')

if path.exists(path.join(target_folder, 'output')):
    print('already exits')
else:
    print('not found, creating...', end=' ')
    mkdir(path.join(target_folder, 'output'))
    print('done')

print('Running pre-checks...', end=' ')
number_channels = [0]*number_files

try:
    invFs, inv = wavfile.read(path.join(target_folder, 'inv.wav'))
except FileNotFoundError:
    print('Failed')
    print('ERROR: Inverse sweep not found! Please add inv.wav to this folder')
    exit()


for file in range(number_files):

    filename = listing[file]
    filename_strip = filename.split('.')[0]

    recFs, rec = wavfile.read(path.join(target_folder, filename))
    invFs, inv = wavfile.read(path.join(target_folder, 'inv.wav'))

    if len(rec.shape) == 1:
        rec = transpose(array([rec]))
    
    if recFs == invFs:
        Fs = recFs
    else:
        print("Failed")
        print("ERROR: Sample rate of inverse sweep and recording do not match")
        print(filename)
        exit()
    
    if rec.shape[0] >= inv.shape[0]:
        pass
    else:
        print("Failed")
        print("Length of inverse sweep is shorter than recording")
        print(filename)
        exit()

    channels = rec.shape[1]
    number_channels[file] = channels

print("OK")
print(" ")
print("Process details:")
print(" ")

for file in range(number_files):
    filename = listing[file]
    print(f'- Filename: {filename}')
    print(f'- Channels: {number_channels[file]}')
    print(" ")

print("")
progress = input("Process following files? (n)-Cancel | (Any Key)-Continue... ")
print('')

if progress == "n":
    print("Exit")
    exit()
else:
    print("Starting...")

## Start Processing

master_scales = {}
prog_tally = 0

for file in range(number_files):

    filename = listing[file]
    filename_strip = filename.split('.')[0]
    out_dir = path.join(path.join(target_folder, "output/"), filename_strip)

    master_scales[out_dir] = []

    length_name_string = len(str("Processing " + filename))

    title_padding = "-"*length_name_string

    print(" ")
    print(title_padding)
    print("Processing " + filename)
    print(title_padding)
    print(" ")

    print(f'Checking destination "{out_dir}"...', end=' ')
    
    if path.exists(out_dir):
        print("already exists")
    else:
        print("not found, creating...", end=' ')
        mkdir(out_dir)
        print("done")

    recFs, rec = wavfile.read(path.join(target_folder, filename))
    invFs, inv = wavfile.read(path.join(target_folder, 'inv.wav'))

    if len(rec.shape) == 1:
        rec = transpose(array([rec]))

    if rec.shape[0] >= inv.shape[0]:
        rec_length = rec.shape[0]
        pad_length = ( rec.shape[0] - inv.shape[0] )

        if pad_length % 2 == 0:
            inv = pad(inv, int(pad_length/2), 'empty')
        else:
            inv = pad(inv, int( (pad_length-1)/2 ), 'empty' )
            inv = append(inv, 0)
    
    Fs = recFs
    channels = rec.shape[1]
    
    for ch in range(channels):
        print(" ")
        progress = ( prog_tally ) / ( number_files*channels ) * 100
        print(f'Processing {filename_strip} Channel {ch} ({progress:.2f}%)')

        ## deconvolution

        resp = conv(rec[:,ch], inv)

        factors = [ max(resp), min(resp)*-1 ]

        factor = max(factors)
        resp = resp/factor

        master_scales[out_dir].append(factor)
        
        window_size = 512
        threashold = 0.001
        len_resp = resp.shape[0]
        len_resp_search = len_resp - window_size
        buffer = [0]*len_resp_search

        resp_2 = power(resp,2)
        window = ones(window_size)/float(window_size)
        buffer = sqrt(convolve(resp_2, window, 'valid'))

        imp_start = 0
        imp_end = 0

        mid = int(len(resp) / 2)
        search_start = mid - (3*Fs)

        for i in range(search_start,len_resp):
            if abs(resp[i]) > 0.5:
                imp_start = int(i-(0.1*Fs))
                break

        for i in range(imp_start+int((Fs*1)), len_resp_search):
            if buffer[i] < threashold:
                imp_end = i
                break
            
        resp_tailed = resp[imp_start:imp_end]

        time = len(resp_tailed)/Fs

        print(f'Trimmed to {time:.4f} s')

        wavfile.write(path.join(out_dir, f'{root_name}-{ch}.wav'), Fs, resp_tailed)
        print("Saving result... ", end=' ')
        print("OK")
        prog_tally += 1

print(" ")

print('Rescaling impulse responses')

max_scale_global = 0

for source in master_scales:
    max_scale = max(master_scales[source])

    if max_scale > max_scale_global:
        max_scale_global = max_scale
    else:
        pass

for source in master_scales:
    for i, channel_scale in enumerate(master_scales[source]):

        rescale = channel_scale / max_scale_global

        print(f'Source {source} Channel {i} Scaled {rescale}')

        recFs, rec = wavfile.read(path.join(source, f'impulse-{i}.wav'))

        rec_scaled = rec*rescale

        wavfile.write(path.join(source, f'impulse-{i}.wav'), recFs, rec_scaled)

print("Jobs completed")
