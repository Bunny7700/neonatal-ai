#!/usr/bin/env python3
"""
Test script for feedback endpoint
Tests the POST /api/feedback endpoint
"""

import requests
import json
import time

def test_feedback_endpoint(base_url="http://127.0.0.1:5000"):
    """Test the feedback endpoint"""
    
    print("=" * 60)
    print("Testing Feedback Endpoint")
    print("=" * 60)
    
    # Test 1: Valid feedback submission
    print("\n1. Testing valid feedback submission...")
    feedback_data = {
        "predicted_type": "hunger",
        "actual_type": "pain_distress"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/feedback",
            json=feedback_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("   ✅ Valid feedback submission: PASSED")
        else:
            print("   ❌ Valid feedback submission: FAILED")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Invalid predicted_type
    print("\n2. Testing invalid predicted_type...")
    invalid_data = {
        "predicted_type": "invalid_type",
        "actual_type": "hunger"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/feedback",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("   ✅ Invalid predicted_type validation: PASSED")
        else:
            print("   ❌ Invalid predicted_type validation: FAILED")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Missing fields
    print("\n3. Testing missing required fields...")
    incomplete_data = {
        "predicted_type": "hunger"
        # Missing actual_type
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/feedback",
            json=incomplete_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("   ✅ Missing fields validation: PASSED")
        else:
            print("   ❌ Missing fields validation: FAILED")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: All valid cry types
    print("\n4. Testing all valid cry types...")
    valid_types = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']
    
    for cry_type in valid_types:
        feedback_data = {
            "predicted_type": cry_type,
            "actual_type": cry_type
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/feedback",
                json=feedback_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"   ✅ {cry_type}: PASSED")
            else:
                print(f"   ❌ {cry_type}: FAILED (status {response.status_code})")
        except Exception as e:
            print(f"   ❌ {cry_type}: Error - {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    # Check if server is running
    base_url = "http://127.0.0.1:5000"
    
    print("Checking if server is running...")
    try:
        response = requests.get(base_url, timeout=2)
        print(f"✅ Server is running at {base_url}\n")
    except requests.exceptions.RequestException:
        print(f"❌ Server is not running at {base_url}")
        print("Please start the server first:")
        print("  python run_simple_server.py")
        print("  or")
        print("  python main.py")
        sys.exit(1)
    
    # Wait a moment for cry detection to initialize
    print("Waiting 3 seconds for cry detection to initialize...")
    time.sleep(3)
    
    # Run tests
    test_feedback_endpoint(base_url)
