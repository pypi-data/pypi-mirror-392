import librosa  
import numpy as np  
import matplotlib.pyplot as plt  
from scipy.signal import lfilter  
from scipy.signal.windows import hamming  # FIXED IMPORT
from scipy.fft import fft, fftfreq  
from librosa.core import lpc  
from .utils import load_audio, pre_emphasis

def analyze_audio_lab4(audio_filename):
    """
    Perform audio analysis for Lab 4 tasks
    """
    # Load and preprocess audio
    y, sr = load_audio(audio_filename, sr=16000, mono=True)
    
    # Apply pre-emphasis filter
    y_preemph = pre_emphasis(y, coeff=0.97)
    print(f"Audio loaded and preprocessed: Sampling Rate = {sr} Hz, Duration = {len(y)/sr:.2f} seconds")
    
    # Spectral Analysis (FFT)
    n = len(y_preemph)
    Y = np.abs(fft(y_preemph))[:n//2]  # Magnitude spectrum
    freq = fftfreq(n, 1/sr)[:n//2]  # Frequency bins
    
    # Plot frequency spectrum
    plt.figure(figsize=(12, 6))
    plt.plot(freq, Y)
    plt.title('Frequency Spectrum (FFT)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim(0, sr/2)  # Limit to Nyquist frequency
    plt.grid(True)
    plt.show()
    
    # Estimate fundamental frequency (pitch)
    f0s, voiced_flag, voiced_probs = librosa.pyin(y, fmin=50, fmax=400, sr=sr)
    f0_median = np.nanmedian(f0s) if np.nanmedian(f0s) else 0
    
    print(f"Estimated Fundamental Frequency (f0): {f0_median:.2f} Hz")
    
    # Estimate formant frequencies using LPC
    order = int(sr / 1000) + 2
    
    # Use a stable vowel segment
    segment_start = len(y_preemph) // 4
    segment_end = 3 * len(y_preemph) // 4
    segment = y_preemph[segment_start:segment_end]
    
    # Apply windowing to a shorter segment
    window_size = min(int(0.025 * sr), len(segment))  # 25ms window
    segment = segment[:window_size]
    
    # Librosa's lpc returns coefficients directly
    a = librosa.lpc(segment, order=order)
    
    # Find roots of the LPC polynomial
    roots = np.roots(a)
    roots = [r for r in roots if np.imag(r) >= 0]
    
    # Calculate angles and convert to Hz
    angles = np.arctan2(np.imag(roots), np.real(roots))
    formant_freqs = sorted(angles * (sr / (2 * np.pi)))
    
    # Filter unrealistic formant frequencies
    formant_freqs = [f for f in formant_freqs if 200 < f < 4000]
    print(f"Estimated Formant Frequencies: {formant_freqs[:5]}")
    
    # Plot with estimated frequencies
    plt.figure(figsize=(12, 6))
    plt.plot(freq, Y)
    plt.title('Frequency Spectrum with Estimated Harmonics and Formants')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim(0, sr/2)
    plt.grid(True)
    
    # Plot harmonic frequencies
    if f0_median > 0:
        harmonic_freqs = np.arange(f0_median, sr/2, f0_median)
        plt.vlines(harmonic_freqs, 0, np.max(Y), color='r', linestyle='--', 
                  label='Harmonics (estimated f0)', alpha=0.5)
    
    # Plot formant frequencies
    if formant_freqs:
        plt.vlines(formant_freqs[:5], 0, np.max(Y), color='g', linestyle='--', 
                  linewidth=2, label='Formants (estimated)')
    
    # Label the first three formants
    labeled_formants = 0
    for f in formant_freqs:
        if labeled_formants < 3 and f > 50:
            plt.text(f, np.max(Y) * 0.95, f'F{labeled_formants+1}', 
                    color='g', fontsize=12, ha='center')
            labeled_formants += 1
        if labeled_formants >= 3:
            break
    
    plt.legend()
    plt.show()
    
    return {
        'signal': y,
        'preemph_signal': y_preemph,
        'sr': sr,
        'f0': f0_median,
        'formants': formant_freqs[:3],
        'spectrum': (freq, Y)
    }