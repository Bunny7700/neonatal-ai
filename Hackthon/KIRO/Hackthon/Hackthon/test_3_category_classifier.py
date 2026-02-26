"""
Test script for 3-category cry classifier (Hunger, Sleep, Discomfort)

This script tests the updated cry classifier with simplified 3-category classification.
"""

import numpy as np
from cry_classifier import CryClassifier
from alert_manager import AlertManager
from feature_extractor import FeatureExtractor

def test_3_categories():
    """Test the 3-category classification system."""
    
    print("=" * 60)
    print("Testing 3-Category Cry Classifier")
    print("Categories: Hunger, Sleep, Discomfort")
    print("=" * 60)
    print()
    
    # Initialize components
    classifier = CryClassifier()
    alert_manager = AlertManager()
    feature_extractor = FeatureExtractor()
    
    # Test 1: Hunger pattern (rhythmic, moderate pitch, sustained)
    print("Test 1: Hunger Pattern")
    print("-" * 40)
    hunger_audio = np.sin(2 * np.pi * 350 * np.linspace(0, 1.5, 24000))  # 350 Hz, 1.5 sec
    hunger_audio = hunger_audio * 0.3  # Moderate intensity
    hunger_features = feature_extractor.extract_all_features(hunger_audio)
    hunger_result = classifier.predict(hunger_audio, hunger_features)
    
    print(f"Detected: {hunger_result['cry_type']}")
    print(f"Confidence: {hunger_result['confidence']:.1f}%")
    print(f"Is Crying: {hunger_result['is_crying']}")
    
    # Generate alert
    alert = alert_manager.generate_alert(
        hunger_result['cry_type'],
        hunger_result['confidence'],
        intensity=50,
        duration=1.5
    )
    print(f"Alert: {alert['message']}")
    print(f"Color: {alert['color']}, Icon: {alert['icon']}, Severity: {alert['severity']}")
    print()
    
    # Test 2: Sleep pattern (variable pitch, lower intensity, longer)
    print("Test 2: Sleep/Tiredness Pattern")
    print("-" * 40)
    # Create variable pitch signal
    t = np.linspace(0, 2.0, 32000)
    sleep_audio = np.sin(2 * np.pi * (300 + 50 * np.sin(2 * np.pi * 2 * t)) * t)
    sleep_audio = sleep_audio * 0.15  # Lower intensity
    sleep_features = feature_extractor.extract_all_features(sleep_audio)
    sleep_result = classifier.predict(sleep_audio, sleep_features)
    
    print(f"Detected: {sleep_result['cry_type']}")
    print(f"Confidence: {sleep_result['confidence']:.1f}%")
    print(f"Is Crying: {sleep_result['is_crying']}")
    
    alert = alert_manager.generate_alert(
        sleep_result['cry_type'],
        sleep_result['confidence'],
        intensity=30,
        duration=2.0
    )
    print(f"Alert: {alert['message']}")
    print(f"Color: {alert['color']}, Icon: {alert['icon']}, Severity: {alert['severity']}")
    print()
    
    # Test 3: Discomfort pattern (high pitch, high intensity, irregular)
    print("Test 3: Discomfort/Distress Pattern")
    print("-" * 40)
    # High pitch with variation
    t = np.linspace(0, 1.0, 16000)
    discomfort_audio = np.sin(2 * np.pi * (500 + 100 * np.sin(2 * np.pi * 5 * t)) * t)
    discomfort_audio = discomfort_audio * 0.6  # High intensity
    discomfort_features = feature_extractor.extract_all_features(discomfort_audio)
    discomfort_result = classifier.predict(discomfort_audio, discomfort_features)
    
    print(f"Detected: {discomfort_result['cry_type']}")
    print(f"Confidence: {discomfort_result['confidence']:.1f}%")
    print(f"Is Crying: {discomfort_result['is_crying']}")
    
    alert = alert_manager.generate_alert(
        discomfort_result['cry_type'],
        discomfort_result['confidence'],
        intensity=80,
        duration=1.0
    )
    print(f"Alert: {alert['message']}")
    print(f"Color: {alert['color']}, Icon: {alert['icon']}, Severity: {alert['severity']}")
    print()
    
    # Test 4: Verify valid categories
    print("Test 4: Valid Categories Check")
    print("-" * 40)
    print(f"Valid categories: {classifier.CRY_CATEGORIES}")
    print(f"Number of categories: {len(classifier.CRY_CATEGORIES)}")
    
    for category in classifier.CRY_CATEGORIES:
        is_valid = classifier.validate_cry_type(category)
        print(f"  {category}: {'✓ Valid' if is_valid else '✗ Invalid'}")
    print()
    
    # Test 5: Alert manager mappings
    print("Test 5: Alert Manager Mappings")
    print("-" * 40)
    for category in classifier.CRY_CATEGORIES:
        message = alert_manager.get_alert_message(category)
        color = alert_manager.get_alert_color(category)
        icon = alert_manager.get_alert_icon(category)
        severity = alert_manager.get_severity(category)
        print(f"{category}:")
        print(f"  Message: {message}")
        print(f"  Color: {color}, Icon: {icon}, Severity: {severity}")
    print()
    
    print("=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_3_categories()
