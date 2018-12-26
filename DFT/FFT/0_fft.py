# -*- coding:utf-8 -*- 
# @Time		:2018/12/20 5:05 PM
# @Author	:Coast Cao
import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack

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
ax.set_title("spectrum")
ax.set_xlabel('Frequency in Herz [Hz]')
ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
ax.set_xlim(-f_s / 2, f_s / 2)
ax.set_ylim(-5, 10)

x_ = fftpack.ifft(X)
fig, ax = plt.subplots()
ax.plot(t,x_)
ax.set_title("reconstructed signal")
ax.set_xlabel('Time [s]')
ax.set_ylabel('Signal amplitude')


'''
np_X = np.fft.fft(x)
np_freqs = np.fft.fftfreq(len(x)) * f_s
print(np_X)
print(abs(np_X))
np_fig, np_ax = plt.subplots()

np_ax.stem(np_freqs, np.abs(np_X))
np_ax.set_xlabel('Frequency in Herz [Hz] np')
np_ax.set_ylabel('Frequency Domain (Spectrum) Magnitude np')
np_ax.set_xlim(-f_s / 2, f_s / 2)
np_ax.set_ylim(-5, 110)
'''
plt.show()
