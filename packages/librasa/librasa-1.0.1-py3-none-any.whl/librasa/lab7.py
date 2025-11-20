import numpy as np
import librosa
import matplotlib.pyplot as plt
from IPython.display import Audio
from scipy.fftpack import dct
from .utils import pre_emphasis

def generate_phonemes():
    """
    Generate synthetic phoneme sounds
    """
    sr = 8000
    t = np.linspace(0, 1, sr)
    
    # AA sound
    y1 = 0.5 * np.sin(2 * np.pi * 120 * t) + 0.2 * np.sin(2 * np.pi * 800 * t) + 0.1 * np.sin(2 * np.pi * 2400 * t)
    y1 = y1 / np.max(np.abs(y1))
    
    # EE sound
    y2 = 0.5 * np.sin(2 * np.pi * 270 * t) + 0.3 * np.sin(2 * np.pi * 2290 * t) + 0.1 * np.sin(2 * np.pi * 3010 * t)
    y2 = y2 / np.max(np.abs(y2))
    
    # OO sound 1
    y3 = 0.5 * np.sin(2 * np.pi * 120 * t) + 0.2 * np.sin(2 * np.pi * 800 * t) + 0.1 * np.sin(2 * np.pi * 2460 * t)
    y3 = y3 / np.max(np.abs(y3))
    
    # OO sound 2
    y4 = 0.5 * np.sin(2 * np.pi * 120 * t) + 0.2 * np.sin(2 * np.pi * 300 * t) + 0.1 * np.sin(2 * np.pi * 870 * t)
    y4 = y4 / np.max(np.abs(y4))
    
    return {
        'aa': (y1, sr),
        'ee': (y2, sr),
        'oo1': (y3, sr),
        'oo2': (y4, sr)
    }

def hamming_window(M):
    """
    Generate Hamming window
    """
    return 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(M) / (M - 1))

def complete_mfcc_pipeline(signal, sr):
    """
    Complete MFCC pipeline from Lab 7
    """
    # Step 1: Pre-emphasis
    emphasized = pre_emphasis(signal)
    
    print("=== Step 2: Pre-Emphasis ===")
    for i in range(11, 20):
        print(f"Sample {i}: Original = {signal[i]:.8f}, Emphasized = {emphasized[i]:.8f}")
    
    # Plot pre-emphasis effect
    plt.figure(figsize=(10, 4))
    plt.plot(signal[:200], color='blue', label='Original')
    plt.plot(emphasized[:200], color='orange', label='Pre-emphasized')
    plt.title("Pre-emphasis Effect (first 200 samples)")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Step 2: Framing
    frame_size = int(0.025 * sr)  # 25 ms
    frame_shift = int(0.010 * sr)  # 10 ms
    
    frames = []
    for start in range(0, len(emphasized) - frame_size, frame_shift):
        frames.append(emphasized[start:start + frame_size])
    frames = np.array(frames)
    
    print(f"\n=== Step 3: Total Frames == {len(frames)}")
    print(f"Frame length: {frame_size} samples")
    print(f"Frame Shift: {frame_shift}")
    
    # Step 3: Windowing
    window = hamming_window(frame_size)
    windowed_frames = frames * window
    
    # Plot windowing effect
    frame_index = 11
    original_frame = frames[frame_index]
    windowed_frame = windowed_frames[frame_index]
    
    plt.figure(figsize=(10, 4))
    plt.plot(original_frame[:200], color='blue', label='Original Frame')
    plt.plot(windowed_frame[:200], color='orange', label='Windowed Frame')
    plt.title("Hamming Window Effect on First 200 Samples")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Step 4: FFT & Power Spectrum
    NFFT = 512
    
    def power_spectrum(frame, NFFT):
        mag = np.abs(np.fft.rfft(frame, NFFT))   # positive frequency
        power = (1.0 / NFFT) * (mag ** 2)
        return power
    
    power_frames = np.array([power_spectrum(f, NFFT) for f in windowed_frames])
    
    plt.figure(figsize=(10, 4))
    plt.plot(10 * np.log10(power_frames[0]))
    plt.title("Power Spectrum (First Frame, dB Scale)")
    plt.xlabel("Frequency Bins")
    plt.ylabel("Power (dB)")
    plt.show()
    
    return {
        'preemph_signal': emphasized,
        'frames': frames,
        'windowed_frames': windowed_frames,
        'power_spectrum': power_frames,
    }