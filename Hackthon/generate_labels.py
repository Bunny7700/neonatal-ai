import os
import numpy as np
import scipy.io.wavfile as wav

# Paths for the exact labels requested
HUNGER_DIR = "data/raw/hungry"
STRESS_DIR = "data/raw/discomfort"
import shutil

for d in [HUNGER_DIR, STRESS_DIR]:
    os.makedirs(d, exist_ok=True)

sample_rate = 16000
duration = 3
num_samples = 50

print("Generating 50 synthetic 'Hunger' cries...")
# Hunger: moderate pitch, rhythmic bursts
for i in range(num_samples):
    t = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    # Fundamental frequency ~400Hz
    freq = np.random.uniform(350, 450)
    
    # Rhythmic envelope (crying in bursts)
    envelope = np.abs(np.sin(2 * np.pi * 1.5 * t))
    
    # Base signal with harmonics
    audio = 0.5 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
    audio = audio * envelope
    
    # Add baby vocal noise
    audio += np.random.normal(0, 0.05, len(t))
    
    # Needs to be audible volume but not screeching
    audio_int16 = np.int16(audio / np.max(np.abs(audio) + 1e-6) * 32767 * 0.4)
    wav.write(os.path.join(HUNGER_DIR, f"hunger_{i:03d}.wav"), sample_rate, audio_int16)

print("Generating 50 synthetic 'Discomfort/Stress' cries...")
# Stress: Shrill, higher pitch, harsher, louder
for i in range(num_samples):
    t = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    # Fundamental frequency ~600Hz (much higher)
    freq = np.random.uniform(550, 750)
    
    # Faster rhythmic envelope (panicked crying)
    envelope = np.abs(np.sin(2 * np.pi * 2.5 * t))
    
    # Signal with lots of harsh harmonics
    audio = 0.6 * np.square(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 3 * t)
    audio = audio * envelope
    
    # Add much more harsh noise
    audio += np.random.normal(0, 0.15, len(t))
    
    # Much louder volume
    audio_int16 = np.int16(audio / np.max(np.abs(audio) + 1e-6) * 32767 * 0.9)
    wav.write(os.path.join(STRESS_DIR, f"stress_{i:03d}.wav"), sample_rate, audio_int16)

print("Finished generating synthetic labeled audio!")
