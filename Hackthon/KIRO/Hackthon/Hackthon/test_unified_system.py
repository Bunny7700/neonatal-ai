"""
Test script to verify the unified system is working
"""

import urllib.request
import json

print("=" * 70)
print("Testing Unified Neonatal Monitoring System")
print("=" * 70)

try:
    # Get dashboard data
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/dashboard')
    data = json.loads(response.read().decode())
    
    print("\n✅ Server is responding!")
    
    # Test Cry Detection
    print("\n🔊 CRY DETECTION:")
    cry = data['cryDetection']
    print(f"   Status: {cry['status']}")
    print(f"   Type: {cry['cryType']}")
    print(f"   Confidence: {cry['confidence']}%")
    print(f"   Intensity: {cry['intensity']}/100")
    print(f"   Last Detected: {cry['lastDetected']}")
    
    # Test Motion Monitoring
    print("\n📹 MOTION MONITORING:")
    motion = data['motionMonitoring']
    print(f"   Status: {motion['status']}")
    print(f"   Still Time: {motion['stillTime']}s")
    print(f"   Motion: {motion['motion']}")
    print(f"   Confidence: {motion['confidence']}%")
    print(f"   Alert Active: {motion['alertActive']}")
    
    # Test Vitals
    print("\n💓 VITAL SIGNS:")
    for vital in data['vitals']:
        status_icon = "✅" if vital['status'] == 'normal' else "⚠️"
        print(f"   {status_icon} {vital['title']}: {vital['value']} {vital['unit']}")
    
    # Test Alerts
    print(f"\n🚨 ALERTS: {len(data['alerts'])} total")
    for i, alert in enumerate(data['alerts'][:3], 1):
        print(f"   {i}. [{alert['type']}] {alert['message']}")
    
    # Test Risk Assessment
    risk = data['riskAssessment']
    print(f"\n📊 RISK ASSESSMENT: {risk['overall'].upper()} (Confidence: {risk['confidence']}%)")
    
    print("\n" + "=" * 70)
    print("✅ All systems operational!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("Make sure the server is running: python run_simple_server.py")
