## Initialisation

print('')
print('-------------------------------')
print('Multi-Channel Deconvolver V 1.0')
print('-------------------------------')
print('')
print('Initialising...', end=' ')

from sys import exit
from os import listdir, path, mkdir
from scipy.io import wavfile
from numpy import array, transpose, sqrt, mean, square
from scipy.signal import fftconvolve as conv

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
    
    if rec.shape[0] == inv.shape[0]:
        channels = rec.shape[1]
    else:
        print("Failed")
        print("Length of inverse sweep and recording do not match")
        print(filename)
        exit()

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

for file in range(number_files):

    filename = listing[file]
    filename_strip = filename.split('.')[0]
    out_dir = path.join(path.join(target_folder, "output/"), filename_strip)

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
    
    Fs = recFs
    channels = rec.shape[1]
    magnitudes = [0] * channels
    
    for ch in range(channels):
        print(" ")
        print(f'Processing Channel {ch}')

        ## deconvolution

        resp = conv(rec[:,ch], inv)

        factors = [ max(resp), min(resp)*-1 ]
        factor = max(factors)
        resp = resp/factor

        ## head trim to centre

        mid = int(len(resp) / 2)
        resp = resp[mid:]

        ## tail trimming forward window
        
        window = 512
        threashold = 0.0001
        len_resp = resp.shape[0]
        len_resp_search = len_resp - window
        buffer = [0]*len_resp_search
        
        for i in range(len_resp_search):
            val = sqrt( mean( square( resp[i:i+window] ) ) )
            buffer[i] = val
        
        imp_start = 0
        imp_end = 0
        
        for i in range(len_resp_search):
            if buffer[i] > threashold*100:
                imp_start = i
                break
    
        for i in range(imp_start, len_resp_search):
            if buffer[i] < threashold:
                imp_end = i
                break
        
        resp_tailed = resp[1:imp_end]

        time = len(resp_tailed)/Fs

        print(f'Trimmed to {time:.4f} s')

        wavfile.write(path.join(out_dir, f'{root_name}-{ch}.wav'), Fs, resp_tailed)
        print("Saving result... ", end=' ')
        print("OK")

print(" ")
print("Jobs completed")
