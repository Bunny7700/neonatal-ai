import os
import numpy as np
import scipy.io.wavfile as wav

OUTPUT_DIR = "data/raw/non_cry"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Generate 50 ambient/noise samples (3 seconds each at 16000 Hz)
sample_rate = 16000
duration = 3
num_samples = 50

print(f"Generating {num_samples} synthetic NON-CRY ambient samples for baseline...")

for i in range(num_samples):
    # Determine noise type
    noise_type = np.random.choice(["white", "pink", "brown", "silence", "sine"])
    
    t = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    
    if noise_type == "white":
        audio = np.random.normal(0, 0.1, len(t))
    elif noise_type == "pink":
        # Rough pink noise approximation
        audio = np.random.normal(0, 0.1, len(t))
        # Simple low pass filter proxy
        for j in range(1, len(audio)):
            audio[j] = 0.8 * audio[j-1] + 0.2 * audio[j]
    elif noise_type == "brown":
        audio = np.cumsum(np.random.normal(0, 0.05, len(t)))
        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.1
    elif noise_type == "silence":
        audio = np.zeros(len(t))
    else: # Sine (like a fan hum or machine beep)
        freq = np.random.uniform(50, 400) # Machine hum
        audio = 0.05 * np.sin(2 * np.pi * freq * t) + np.random.normal(0, 0.01, len(t))

    # Normalize to 16-bit PCM and save
    audio_int16 = np.int16(audio / np.max(np.abs(audio) + 1e-6) * 32767 * np.random.uniform(0.1, 0.8))
    
    wav.write(os.path.join(OUTPUT_DIR, f"synthetic_ambient_{noise_type}_{i:03d}.wav"), sample_rate, audio_int16)

print("Done generating non-cry samples!")
