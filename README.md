# MCD
Multi-Channel Deconvolution V1.2

### Download
See /dist for the latest compiled version  
*Currently only compiled for latest macOS*  

### Usage
This tool searches through a specified folder for all .wav files and performs a deconvolution on each channel of each file with the “inv.wav” file (the inverse of the pure sweep used to make the recordings) which must be in the specified folder.

The tool creates an output folder in the specified folder, and creates a folder for each .wav file, copying its name, where each impulse response is saved for each channel of that .wav file
