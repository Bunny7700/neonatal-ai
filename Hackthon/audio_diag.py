import sys
print(f"Python Version: {sys.version}")

try:
    import sounddevice as sd
    print("sounddevice: OK")
    try:
        devices = sd.query_devices()
        print(f"Devices found: {len(devices)}")
        print(devices)
    except Exception as e:
        print(f"sd.query_devices error: {e}")
except ImportError as e:
    print(f"sounddevice import error: {e}")

try:
    import librosa
    print("librosa: OK")
except ImportError as e:
    print(f"librosa import error: {e}")

try:
    import joblib
    print("joblib: OK")
except ImportError as e:
    print(f"joblib import error: {e}")

try:
    import sklearn
    print(f"sklearn version: {sklearn.__version__}")
except ImportError as e:
    print(f"sklearn import error: {e}")
