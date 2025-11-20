import librosa
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import Audio, display
from .utils import load_audio

def analyze_audio_lab1(filename):
    """
    Perform digital audio analysis for Lab 1
    """
    # Load audio with original sampling rate
    waveform, sampling_rate = load_audio(filename, sr=None)
    
    print(f"Loaded '{filename}' successfully!")
    
    # Audio properties
    print("\nAudio Properties")
    print(f"Sampling Rate: {sampling_rate} Hz")
    print(f"Waveform Shape: {waveform.shape}")
    print(f"Data Type: {waveform.dtype}")
    duration = len(waveform) / sampling_rate
    print(f"Duration: {duration:.2f} seconds")
    
    # Handle stereo audio
    if len(waveform.shape) == 2:
        print("Stereo detected -> converting to mono...")
        waveform = np.mean(waveform, axis=0)
    else:
        print("Audio is already mono.")
    print(f"New waveform shape: {waveform.shape}")
    
    # Create time axis
    time = np.arange(0, len(waveform)) / sampling_rate
    print(f"Time array created: from 0s to {time[-1]:.2f}s")
    
    # Plot waveform
    plt.figure(figsize=(14, 5))
    plt.plot(time, waveform, color='blue', linewidth=1)
    plt.title('Waveform: Amplitude vs Time', fontsize=16)
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Amplitude', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Resample to lower rate (8kHz)
    waveform_low, sr_low = librosa.load(filename, sr=8000)
    time_low = np.arange(0, len(waveform_low)) / sr_low
    
    print(f"Resampled to {sr_low} Hz")
    print(f"Original samples: {len(waveform)}")
    print(f"Downsampled samples: {len(waveform_low)}")
    
    # Compare original and resampled
    plt.figure(figsize=(14, 6))
    
    plt.subplot(2, 1, 1)
    plt.plot(time, waveform, color='darkblue')
    plt.title('Original Waveform')
    plt.ylabel('Amplitude')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    plt.plot(time_low, waveform_low, color='red')
    plt.title('Resampled Waveform (8 kHz)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return {
        'original_signal': waveform,
        'original_sr': sampling_rate,
        'resampled_signal': waveform_low,
        'resampled_sr': sr_low,
        'time_original': time,
        'time_resampled': time_low
    }