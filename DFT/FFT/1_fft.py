# -*- coding:utf-8 -*- 
# @Time		:2018/12/21 10:37 AM
# @Author	:Coast Cao

import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from skimage import util
from scipy import signal

# load a wave
rate, audio = wavfile.read("/Users/coast/Downloads/Nightingale-sound/nightbird.wav")
print(audio)
print(audio.shape)

audio = np.mean(audio, axis=1)

print(audio)
print(audio.shape)
print(rate)
N = audio.shape[0]
L = N / rate

print(f'Audio length: {L:.2f} seconds')

# plot the waveform
f, ax = plt.subplots()
ax.plot(np.arange(N) / rate, audio)
ax.set_xlabel('Time [s]')
ax.set_ylabel('Amplitude [unknown]')

M = 1024

# slice the waveform
slices = util.view_as_windows(audio, window_shape=(M,), step=100)
print(f'Audio shape: {audio.shape}, Sliced audio shape: {slices.shape}')

win = np.hanning(M + 1)[:-1]
slices = slices * win

slices = slices.T
print(f'Shape of "slices":{slices.shape}')

# get spectrogram using low-level api
spectrum0 = np.fft.fft(slices, axis=0) #[:M // 2 + 1:-1]
print(len(np.fft.fftfreq()))
spectrum = np.abs(spectrum0[:M // 2 + 1:-1])

print(spectrum.shape)

f, ax = plt.subplots(figsize=(4.8, 2.4))

S = np.abs(spectrum)
S = 20 * np.log10(S / np.max(S))

ax.imshow(S, origin='lower', cmap='viridis', extent=(0, L, 0, rate / 2 / 1000))
ax.axis('tight')
ax.set_ylabel('Frequency [kHz]')
ax.set_xlabel('Time [s]')


# get spectrogram using high-level api
freqs, times, Sx = signal.spectrogram(audio, fs=rate, window='hanning', nperseg=1024, noverlap=M-100,
                                      detrend=False, scaling='spectrum')
f, ax = plt.subplots(figsize=(4.8, 2.4))
print(freqs)
print(len(freqs))
ax.pcolormesh(times, freqs / 1000, 10 * np.log10(Sx), cmap='viridis')
ax.set_ylabel('Frequency [kHz]')
ax.set_xlabel('Time [s]')


# plot a slice of audio
f, ax = plt.subplots()
ax.plot(np.arange(len(slices[:,440])) / rate, slices[:,440])
ax.set_title("raw audio splice")
ax.set_xlabel('Time [s]')
ax.set_ylabel('Amplitude [unknown]')

# recontruct the audio using ifft
syn_audio = np.fft.ifft(spectrum0[:,440])
f, ax = plt.subplots()
ax.plot(np.arange(len(syn_audio)) / rate, syn_audio)
ax.set_title("reconstructed audio splice")
ax.set_xlabel('Time [s]')
ax.set_ylabel('Amplitude [unknown]')
plt.show()

assert slices[:440] == syn_audio




