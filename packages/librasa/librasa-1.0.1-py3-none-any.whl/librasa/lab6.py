import os
import librosa
import librosa.display
import soundfile as sf
import matplotlib.pyplot as plt
import IPython.display as ipd
import numpy as np
from sklearn.metrics import mean_squared_error
from scipy.fftpack import dct
from .utils import pre_emphasis

def hamming_window(M):
    """
    Generate Hamming window
    """
    return 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(M) / (M - 1))

def framing(signal, sr, frame_size=0.025, frame_stride=0.010):
    """
    Frame the signal into overlapping frames
    """
    frame_length = int(frame_size * sr)
    frame_step = int(frame_stride * sr)
    signal_length = len(signal)
    num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step))

    pad_signal_length = num_frames * frame_step + frame_length
    z = np.zeros((pad_signal_length - signal_length))
    pad_signal = np.append(signal, z)

    indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + \
              np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
    frames = pad_signal[indices.astype(np.int32, copy=False)]
    return frames

def apply_window(frames):
    """
    Apply Hamming window to frames
    """
    window = hamming_window(frames.shape[1])
    return frames * window

def power_spectrum(frames, NFFT=512):
    """
    Compute power spectrum of frames
    """
    mag_frames = np.absolute(np.fft.rfft(frames, NFFT))
    pow_frames = ((1.0 / NFFT) * (mag_frames ** 2))
    return pow_frames

def hz_to_mel(hz):
    """Convert Hz to Mel scale"""
    return 2595 * np.log10(1 + hz / 700)

def mel_to_hz(mel):
    """Convert Mel to Hz scale"""
    return 700 * (10**(mel / 2595) - 1)

def mel_filterbank(pow_frames, sr, NFFT=512, nfilt=26):
    """
    Apply Mel filterbank to power spectrum
    """
    low_mel = hz_to_mel(0)
    high_mel = hz_to_mel(sr / 2)
    mel_points = np.linspace(low_mel, high_mel, nfilt + 2)
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((NFFT + 1) * hz_points / sr).astype(int)

    fbank = np.zeros((nfilt, int(NFFT / 2 + 1)))
    for m in range(1, nfilt + 1):
        f_m_minus = bin_points[m - 1]
        f_m = bin_points[m]
        f_m_plus = bin_points[m + 1]

        for k in range(f_m_minus, f_m):
            fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
        for k in range(f_m, f_m_plus):
            fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

    filter_banks = np.dot(pow_frames, fbank.T)
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
    return np.log(filter_banks)

def compute_mfcc(log_energies, num_ceps=13):
    """
    Compute MFCC from log filterbank energies
    """
    mfcc = np.array([dct(f, type=2, norm='ortho')[:num_ceps] for f in log_energies])
    mfcc -= (np.mean(mfcc, axis=0) + 1e-8)
    return mfcc

def mfcc_from_scratch(signal, sr):
    """
    Compute MFCC from scratch
    """
    emphasized = pre_emphasis(signal)
    frames = framing(emphasized, sr)
    windowed_frames = apply_window(frames)
    pow_frames = power_spectrum(windowed_frames)
    log_energies = mel_filterbank(pow_frames, sr)
    mfcc = compute_mfcc(log_energies)
    return mfcc

def compare_mfcc_implementations(signal, sr):
    """
    Compare custom MFCC implementation with librosa
    """
    # Custom MFCC
    mfcc_manual = mfcc_from_scratch(signal, sr)
    
    # Librosa MFCC (reference)
    mfcc_librosa = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
    
    print("Manual MFCC shape:", mfcc_manual.shape)
    print("Librosa MFCC shape:", mfcc_librosa.T.shape)
    
    # Align shapes
    min_frames = min(mfcc_manual.shape[0], mfcc_librosa.shape[1])
    mfcc_manual = mfcc_manual[:min_frames]
    mfcc_librosa = mfcc_librosa[:, :min_frames].T
    
    # Mean Squared Error (MSE)
    mse = mean_squared_error(mfcc_manual.flatten(), mfcc_librosa.flatten())
    
    # Signal-to-Noise Ratio (SNR)
    signal_power = np.mean(mfcc_librosa ** 2)
    noise_power = np.mean((mfcc_librosa - mfcc_manual) ** 2)
    snr = 10 * np.log10(signal_power / noise_power)
    
    print(f"MSE: {mse:.6f}")
    print(f"SNR: {snr:.2f} dB")
    
    # Visualize results
    plt.figure(figsize=(14, 5))
    plt.subplot(1, 2, 1)
    librosa.display.specshow(mfcc_manual.T, sr=sr, x_axis='time')
    plt.title("MFCC (from Scratch)")
    plt.colorbar()
    
    plt.subplot(1, 2, 2)
    librosa.display.specshow(mfcc_librosa.T, sr=sr, x_axis='time')
    plt.title("MFCC (Librosa)")
    plt.colorbar()
    plt.show()
    
    return {
        'mfcc_manual': mfcc_manual,
        'mfcc_librosa': mfcc_librosa,
        'mse': mse,
        'snr': snr
    }