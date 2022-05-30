from random import sample
import myfunc
import ceps

import argparse
import numpy as np
import librosa
from matplotlib import pyplot as plt

def main():
    parser = argparse.ArgumentParser()

    # parser.add_argumentで受け取る引数を追加
    parser.add_argument('filepath', type=str, help='wav file name : ex4.wav')
    parser.add_argument('--shift_size', type=int, default=1024, help='shift size')
    parser.add_argument('--lifter', type=int, default=20, help='cut off freqency by lifter')

    # define numbers
    args = parser.parse_args()
    shift_size = args.shift_size  # Fs
    overlap = shift_size // 2
    f_lifter = args.lifter

    # load file
    data, samplerate = librosa.load(args.filepath)  # samplerate: 48000
    data_size = data.shape[0]  # Fl:Frame length  # len(data) = 301644
    time = float(data_size / samplerate)

    # calculate fundamental frequency (f0) by autocorrelation
    f0_ac = ceps.calc_ac(data, shift_size, samplerate)
    print('f0_ac', f0_ac)
    # calculate fundamental frequency (f0) by cepstrum
    f0_cep = ceps.calc_cep(data, shift_size, samplerate)
    print('f0_cep', f0_cep)
    
    # plot f0 with spectrogram
    plt.figure(figsize=(10,7))
    plt.title('Fundamental Frequency')
    plt.xlabel('Time[s]')
    plt.ylabel('Frequency[Hz]')
    myfunc.myspectrogram(data, shift_size, data_size, overlap, samplerate, 'Spectrogram', 'rainbow')
    plt.plot(np.arange(0, time, time / len(f0_ac)), f0_ac, color = 'deeppink', label='AutoCorrelation', linewidth = 2.0)
    plt.plot(np.arange(0, time, time / len(f0_cep)), f0_cep, color = 'b', label='Cepstrum', linewidth = 2.0)
    plt.legend()
    plt.tight_layout()
    # plt.savefig('f0_piano.png')
    plt.show()
    plt.close()

    # calculate spectral envelope
    start = data_size // 4
    win_data = data[start: start + shift_size] * np.hamming(shift_size)
    fft_data = np.fft.fft(win_data)
    power_spec = 20 * np.log10(np.abs(fft_data))

    fscale = np.fft.fftfreq(shift_size, d=1.0/samplerate)   # frequency scale

    # calculate spectral envelope by cepstrum
    cep = ceps.cepstrum(win_data)  # fft, log, fft
    cep_lifter = np.array(cep)  # lifter
    cep_lifter[f_lifter: len(cep_lifter) - f_lifter + 1] = 0
    env_ceps = 20 * np.fft.fft(cep_lifter, shift_size).real

    # calculate spectral envelope by LPC
    env_lpc = ceps.lpc(win_data, 32, shift_size)
    # plot spectral envelope
    plt.figure(figsize=(10,7))
    plt.title('Spectral Envelope')
    plt.xlabel('Frequency[Hz]')
    plt.ylabel('Log amplitude spectrum [dB]')
    plt.plot(fscale[: shift_size//2], power_spec[: len(power_spec)//2], color = 'deepskyblue', label = 'spectrum', linewidth = 2.0)
    plt.plot(fscale[: shift_size//2], env_ceps[:len(env_ceps)//2], color = 'deeppink', label = 'cepstrum', linewidth = 2.0)
    plt.plot(fscale[: shift_size//2], env_lpc[:len(env_lpc)//2], color = 'purple', label = 'LPC', linewidth = 2.0)
    plt.legend()
    plt.tight_layout()
    # plt.savefig('spectral_piano.png')
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()