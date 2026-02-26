"""
Simple test to verify the system works without numpy crashes
"""

print("=" * 60)
print("Testing Neonatal Cry Detection System")
print("=" * 60)

# Test 1: Import shared_data
print("\n1. Testing shared_data import...")
try:
    from shared_data import dashboard_data
    print("   ✅ shared_data imported successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Import enhanced cry detector
print("\n2. Testing enhanced cry detector import...")
try:
    from cry_detection_enhanced import CryDetector
    print("   ✅ CryDetector imported successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Create detector instance
print("\n3. Testing detector initialization...")
try:
    detector = CryDetector()
    print("   ✅ Detector initialized successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Run detection
print("\n4. Testing detection...")
try:
    result = detector.detect()
    print(f"   ✅ Detection successful")
    print(f"      - Crying: {result['isCrying']}")
    print(f"      - Type: {result['cryType']}")
    print(f"      - Confidence: {result['confidence']}%")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Test FastAPI import
print("\n5. Testing FastAPI import...")
try:
    from fastapi import FastAPI
    print("   ✅ FastAPI imported successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
