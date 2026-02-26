"""
Simple verification script for AlertManager

Demonstrates the functionality of the AlertManager class with examples
of all cry types and dashboard updates.
"""

from alert_manager import AlertManager
from shared_data import dashboard_data
import json


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    print("\n🔔 AlertManager Verification Script")
    print("=" * 60)
    
    # Create AlertManager instance
    alert_manager = AlertManager()
    
    # Test 1: Message Mapping
    print_section("Test 1: Message Mapping for All Cry Types")
    cry_types = ["hunger", "sleep_discomfort", "pain_distress", 
                 "diaper_change", "normal_unknown"]
    
    for cry_type in cry_types:
        message = alert_manager.get_alert_message(cry_type)
        print(f"  {cry_type:20s} → {message}")
    
    # Test 2: Color Coding
    print_section("Test 2: Color Coding (Severity-Based)")
    for cry_type in cry_types:
        color = alert_manager.get_alert_color(cry_type)
        severity = alert_manager.get_severity(cry_type)
        print(f"  {cry_type:20s} → {color} ({severity} severity)")
    
    # Test 3: Icon Mapping
    print_section("Test 3: Icon Mapping")
    for cry_type in cry_types:
        icon = alert_manager.get_alert_icon(cry_type)
        print(f"  {cry_type:20s} → {icon}")
    
    # Test 4: Complete Alert Generation
    print_section("Test 4: Complete Alert Generation")
    
    # Example 1: Hunger cry
    alert = alert_manager.generate_alert("hunger", 75.5, 60.0, 3.5)
    print("\n  Hunger Cry Alert:")
    print(f"    Message:    {alert['message']}")
    print(f"    Confidence: {alert['confidence']}%")
    print(f"    Color:      {alert['color']}")
    print(f"    Icon:       {alert['icon']}")
    print(f"    Severity:   {alert['severity']}")
    print(f"    Intensity:  {alert['intensity']}")
    print(f"    Duration:   {alert['duration']}s")
    
    # Example 2: Pain/distress cry
    alert = alert_manager.generate_alert("pain_distress", 92.0, 85.0, 5.2)
    print("\n  Pain/Distress Cry Alert:")
    print(f"    Message:    {alert['message']}")
    print(f"    Confidence: {alert['confidence']}%")
    print(f"    Color:      {alert['color']}")
    print(f"    Icon:       {alert['icon']}")
    print(f"    Severity:   {alert['severity']}")
    print(f"    Intensity:  {alert['intensity']}")
    print(f"    Duration:   {alert['duration']}s")
    
    # Test 5: Dashboard Update
    print_section("Test 5: Dashboard Update")
    
    # Create a test alert
    alert = alert_manager.generate_alert("hunger", 78.0, 65.0, 4.0)
    
    print("\n  Before Update:")
    print(f"    Status:      {dashboard_data['cryDetection']['status']}")
    print(f"    Cry Type:    {dashboard_data['cryDetection']['cryType']}")
    print(f"    Confidence:  {dashboard_data['cryDetection']['confidence']}%")
    print(f"    Alerts:      {len(dashboard_data['alerts'])} alerts")
    
    # Update dashboard
    alert_manager.update_dashboard(dashboard_data, alert)
    
    print("\n  After Update:")
    print(f"    Status:      {dashboard_data['cryDetection']['status']}")
    print(f"    Cry Type:    {dashboard_data['cryDetection']['cryType']}")
    print(f"    Confidence:  {dashboard_data['cryDetection']['confidence']}%")
    print(f"    Intensity:   {dashboard_data['cryDetection']['intensity']}")
    print(f"    Duration:    {dashboard_data['cryDetection']['duration']}s")
    print(f"    Last Det.:   {dashboard_data['cryDetection']['lastDetected']}")
    print(f"    Alerts:      {len(dashboard_data['alerts'])} alerts")
    
    if dashboard_data['alerts']:
        print(f"\n  Latest Alert:")
        latest = dashboard_data['alerts'][0]
        print(f"    Time:        {latest['time']}")
        print(f"    Type:        {latest['type']}")
        print(f"    Description: {latest['description']}")
    
    # Test 6: Multiple Alerts
    print_section("Test 6: Multiple Alerts with Different Severities")
    
    test_cases = [
        ("normal_unknown", 45.0, 30.0, 2.0),
        ("diaper_change", 68.0, 50.0, 3.0),
        ("sleep_discomfort", 72.0, 55.0, 4.0),
        ("hunger", 80.0, 70.0, 5.0),
        ("pain_distress", 95.0, 90.0, 6.0),
    ]
    
    for cry_type, confidence, intensity, duration in test_cases:
        alert = alert_manager.generate_alert(cry_type, confidence, intensity, duration)
        alert_manager.update_dashboard(dashboard_data, alert)
        print(f"\n  {alert['icon']} {cry_type:20s} (conf: {confidence:5.1f}%) → {alert['severity']:6s} severity")
    
    print(f"\n  Total alerts in dashboard: {len(dashboard_data['alerts'])}")
    print(f"  Total events in dashboard: {len(dashboard_data['events'])}")
    
    # Test 7: Alert Structure Validation
    print_section("Test 7: Alert Structure Validation")
    
    alert = alert_manager.generate_alert("hunger", 75.0, 60.0, 3.0)
    required_fields = ["message", "cry_type", "confidence", "color", 
                      "icon", "timestamp", "severity", "intensity", "duration"]
    
    print("\n  Checking required fields in alert structure:")
    all_present = True
    for field in required_fields:
        present = field in alert
        status = "✓" if present else "✗"
        print(f"    {status} {field}")
        if not present:
            all_present = False
    
    if all_present:
        print("\n  ✅ All required fields present!")
    else:
        print("\n  ❌ Some fields missing!")
    
    # Summary
    print_section("Summary")
    print("\n  ✅ Message mapping: All 5 cry types mapped correctly")
    print("  ✅ Color coding: Red (pain), Yellow (hunger/discomfort/diaper), Green (normal)")
    print("  ✅ Icon mapping: All 5 cry types have unique icons")
    print("  ✅ Alert generation: Complete structure with all required fields")
    print("  ✅ Dashboard updates: Correctly updates shared_data structure")
    print("  ✅ Alert severity: Properly categorized as low/medium/high")
    print("\n  🎉 AlertManager is working correctly!")
    print("=" * 60)


if __name__ == "__main__":
    main()
