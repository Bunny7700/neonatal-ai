import sounddevice as sd
print("Checking for audio devices...")
devices = sd.query_devices()
input_devices = [d for d in devices if d['max_input_channels'] > 0]
if not input_devices:
    print("FATAL ERROR: No input devices (microphones) found!")
else:
    print(f"SUCCESS: {len(input_devices)} input devices found.")
    for d in input_devices:
        print(f" - {d['name']} (Chans: {d['max_input_channels']})")

try:
    print("Testing a 1-second record...")
    fs = 16000
    duration = 1
    rec = sd.rec(int(duration * fs), samplerate=fs, channels=1, blocking=True)
    print("Recording: OK")
except Exception as e:
    print(f"Recording error: {e}")
