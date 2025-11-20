import numpy as np
import matplotlib.pyplot as plt
import librosa
import soundfile as sf
import librosa.display
from .utils import load_audio

def analyze_audio_quiz1(filename):
    """
    Perform audio analysis for Quiz 1 tasks
    """
    # Load waveform
    y, sr = load_audio(filename, sr=None)
    
    # Plot first 50 ms
    samples_50ms = int(0.05 * sr)
    y_first_50ms = y[:samples_50ms]
    time_50ms = np.arange(0, len(y_first_50ms)) / sr * 1000  # Convert to milliseconds
    
    plt.figure(figsize=(10, 4))
    plt.plot(time_50ms, y_first_50ms)
    plt.title('First 50 ms of Audio Waveform')
    plt.xlabel('Time (milliseconds)')
    plt.ylabel('Amplitude')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Normalize amplitude to range [-1, 1]
    normal = librosa.util.normalize(y, norm=np.inf)
    
    plt.figure(figsize=(10, 4))
    plt.plot(normal, label='normalization', alpha=0.7)
    plt.title('Normalized Audio Signal')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.ylim(-1, 1)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()
    
    # Segment waveform into two parts
    word1_start_sample = 5000
    word1_end_sample = 15000
    word2_start_sample = 20000
    word2_end_sample = 30000
    
    word1_segment = y[word1_start_sample:word1_end_sample]
    word2_segment = y[word2_start_sample:word2_end_sample]
    
    print(f"Length of word 1 segment: {len(word1_segment)} samples")
    print(f"Length of word 2 segment: {len(word2_segment)} samples")
    
    # Plot both segments
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(word1_segment, sr=sr)
    plt.title("Word 1 Segment")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.show()
    
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(word2_segment, sr=sr)
    plt.title("Word 2 Segment")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.show()
    
    # Compute energy
    energy_word1 = np.sum(word1_segment**2)
    energy_word2 = np.sum(word2_segment**2)
    
    print(f"Energy of word 1 segment: {energy_word1}")
    print(f"Energy of word 2 segment: {energy_word2}")
    
    # Determine voiced/unvoiced dominance
    if energy_word1 > energy_word2:
        voiced_word = "Word 1"
        unvoiced_word = "Word 2"
    else:
        voiced_word = "Word 2"
        unvoiced_word = "Word 1"
    
    print(f"\nBased on energy analysis:")
    print(f"Voiced-dominant word: {voiced_word}")
    print(f"Unvoiced-dominant word: {unvoiced_word}")
    
    return {
        'signal': y,
        'normalized_signal': normal,
        'sr': sr,
        'word1_segment': word1_segment,
        'word2_segment': word2_segment,
        'energy_word1': energy_word1,
        'energy_word2': energy_word2,
        'voiced_word': voiced_word,
        'unvoiced_word': unvoiced_word
    }