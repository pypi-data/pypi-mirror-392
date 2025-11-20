import numpy as np
import librosa
import matplotlib.pyplot as plt
from scipy.signal import lfilter
from scipy.signal.windows import hamming
from scipy.fft import fft, fftfreq
import librosa.display

def load_audio(filename, sr=16000, mono=True):
    """
    Load audio file with error handling
    """
    try:
        y, sr = librosa.load(filename, sr=sr, mono=mono)
        print(f"Loaded {filename} successfully")
        print(f"Duration: {len(y)/sr:.2f} seconds, Sampling rate: {sr} Hz")
        return y, sr
    except FileNotFoundError:
        print(f"Error: Audio file not found at {filename}")
        sr = 16000
        y = np.random.randn(sr * 2)
        print("Using dummy audio for now.")
        return y, sr

def pre_emphasis(signal, coeff=0.97):
    """
    Apply pre-emphasis filter to boost high frequencies
    """
    return np.append(signal[0], signal[1:] - coeff * signal[:-1])

def plot_waveform(y, sr, title="Waveform"):
    """
    Plot audio waveform
    """
    plt.figure(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr)
    plt.title(title)
    plt.xlabel("Time [s]")
    plt.ylabel('Amplitude')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()