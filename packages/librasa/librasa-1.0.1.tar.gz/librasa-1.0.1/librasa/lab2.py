import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from scipy.signal import lfilter
from scipy.signal.windows import hamming  # FIXED IMPORT
from numpy.linalg import lstsq
from .utils import load_audio, plot_waveform

def analyze_speech_lab2(filename):
    """
    Perform comprehensive speech analysis for Lab 2
    """
    # Load audio
    y, sr = load_audio(filename, sr=None)
    
    # Plot waveform
    plot_waveform(y, sr, "Speech Waveform")
    
    # Compute STFT spectrogram
    D = librosa.stft(y, n_fft=1024, hop_length=256)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    # Plot linear-frequency spectrogram
    plt.figure(figsize=(10, 6))
    librosa.display.specshow(S_db, sr=sr, hop_length=256, x_axis='time', y_axis='linear')
    plt.colorbar(label="Magnitude (dB)")
    plt.title("Linear-Frequency Spectrogram (STFT)")
    plt.ylim(0, 5000)
    plt.tight_layout()
    plt.show()
    
    # Pitch tracking
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_values = pitches[magnitudes > np.median(magnitudes)]
    
    # Plot pitch histogram
    plt.figure(figsize=(8, 4))
    plt.hist(pitch_values, bins=90, color='teal', alpha=0.7)
    plt.title("Estimated Fundamental Frequencies (Pitch Histogram)")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Count")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    print(f"Median Pitch: {np.median(pitch_values):.1f} Hz")
    
    # Mel spectrogram
    S_mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, fmax=8000)
    S_mel_db = librosa.power_to_db(S_mel, ref=np.max)
    
    plt.figure(figsize=(10, 6))
    librosa.display.specshow(S_mel_db, x_axis='time', y_axis='mel', sr=sr, fmax=8000)
    plt.colorbar(label='dB')
    plt.title('Log-Mel Spectrogram')
    plt.tight_layout()
    plt.show()
    
    return {
        'signal': y,
        'sr': sr,
        'spectrogram': S_db,
        'mel_spectrogram': S_mel_db,
        'pitches': pitch_values
    }

def lpc_formants(sig, sr, order=10):
    """
    Estimate formant frequencies using LPC
    """
    sig = sig * hamming(len(sig))
    A = np.zeros((len(sig) - order, order))
    for i in range(order):
        A[:, i] = sig[order - i - 1:len(sig) - i - 1]
    y_vec = sig[order:]
    a_, _, _, _ = lstsq(A, y_vec, rcond=None)
    roots = np.roots(np.concatenate(([1], -a_)))
    roots = [r for r in roots if np.imag(r) >= 0]
    angles = np.arctan2(np.imag(roots), np.real(roots))
    formants = sorted(angles * (sr / (2 * np.pi)))
    return formants[:3]