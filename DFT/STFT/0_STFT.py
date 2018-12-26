# -*- coding:utf-8 -*- 
# @Time		:2018/12/25 8:42 PM
# @Author	:Coast Cao
import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
import librosa

f = 10
f_s = 100

t = np.linspace(0, 2, 2 * f_s, endpoint=False)
x = 3 * np.sin(f * 2 * np.pi * t) + 5 * np.sin(f * 4 * np.pi * t) + 8 * np.cos(f * 5 * np.pi * t)

fig, ax = plt.subplots()
ax.plot(t,x)
ax.set_title("raw signal")
ax.set_xlabel('Time [s]')
ax.set_ylabel('Signal amplitude')

# do fft
X = fftpack.fft(x)
print(X)
print(np.max(X))
print(abs(X))
print(np.angle(X))
print(len(X))
freqs = fftpack.fftfreq(len(x)) * f_s

print(freqs)
print(len(freqs))
fig, ax = plt.subplots()
ax.stem(freqs, np.abs(X) / (2 * f_s))
ax.set_title("spectrum with FFT")
ax.set_xlabel('Frequency in Herz [Hz]')
ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
ax.set_xlim(-f_s / 2, f_s / 2)
ax.set_ylim(-5, 10)

x_ = fftpack.ifft(X)
fig, ax = plt.subplots()
ax.plot(t,x_)
ax.set_title("reconstructed signal with IFFT")
ax.set_xlabel('Time [s]')
ax.set_ylabel('Signal amplitude')

# do stft
X_stft = librosa.stft(x)
print(X_stft)
print(fftpack.ifft(X_stft))
print(fftpack.ifft(X_stft).real)
