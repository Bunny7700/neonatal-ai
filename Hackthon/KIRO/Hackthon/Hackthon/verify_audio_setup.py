"""
Verify Audio Processing Setup
Tests if all required libraries are installed correctly
"""

def check_library(name, import_name=None):
    """Check if a library is installed and get its version"""
    if import_name is None:
        import_name = name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {name}: NOT INSTALLED")
        print(f"   Error: {e}")
        return False

def main():
    print("="*60)
    print("🔍 Checking Audio Processing Libraries")
    print("="*60)
    print()
    
    # Check Python version
    import sys
    print(f"Python Version: {sys.version}")
    print()
    
    # Required libraries
    libraries = [
        ('numpy', 'numpy'),
        ('librosa', 'librosa'),
        ('scipy', 'scipy'),
        ('soundfile', 'soundfile'),
    ]
    
    # Optional libraries
    optional_libraries = [
        ('tensorflow', 'tensorflow'),
        ('scikit-learn', 'sklearn'),
        ('matplotlib', 'matplotlib'),
    ]
    
    print("Required Libraries:")
    print("-" * 60)
    all_required = True
    for name, import_name in libraries:
        if not check_library(name, import_name):
            all_required = False
    
    print()
    print("Optional Libraries (for training):")
    print("-" * 60)
    for name, import_name in optional_libraries:
        check_library(name, import_name)
    
    print()
    print("="*60)
    if all_required:
        print("✅ All required audio processing libraries installed successfully!")
        print("✅ You can now use real ML-based cry detection!")
        print()
        print("Next steps:")
        print("1. Run: python main_enhanced.py")
        print("2. Open the frontend in your browser")
        print("3. Click 'Start Listening' and test with real audio")
    else:
        print("❌ Some required libraries are missing!")
        print()
        print("To install missing libraries:")
        print("pip install numpy librosa scipy soundfile")
    print("="*60)

if __name__ == "__main__":
    main()
