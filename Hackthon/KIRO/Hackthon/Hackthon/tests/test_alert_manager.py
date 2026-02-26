"""
Unit tests for AlertManager module

Tests alert generation, message mapping, color coding, icon mapping,
and dashboard updates.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.9, 11.2
"""

import pytest
import time
from datetime import datetime
from alert_manager import AlertManager


class TestAlertManager:
    """Test suite for AlertManager class"""
    
    @pytest.fixture
    def alert_manager(self):
        """Create AlertManager instance for testing"""
        return AlertManager()
    
    @pytest.fixture
    def mock_shared_data(self):
        """Create mock shared_data structure"""
        return {
            "cryDetection": {
                "status": "normal",
                "cryType": "None detected",
                "intensity": 0,
                "duration": 0,
                "confidence": 0,
                "lastDetected": "None",
                "audioWaveform": [0.1] * 10
            },
            "alerts": [],
            "events": []
        }
    
    # Test message mapping (Requirements 5.1-5.5)
    
    def test_hunger_message(self, alert_manager):
        """Test hunger cry message mapping"""
        message = alert_manager.get_alert_message("hunger")
        assert message == "Baby may be hungry"
    
    def test_sleep_discomfort_message(self, alert_manager):
        """Test sleep discomfort cry message mapping"""
        message = alert_manager.get_alert_message("sleep_discomfort")
        assert message == "Baby may be uncomfortable"
    
    def test_pain_distress_message(self, alert_manager):
        """Test pain/distress cry message mapping"""
        message = alert_manager.get_alert_message("pain_distress")
        assert message == "Baby shows signs of pain – immediate attention needed"
    
    def test_diaper_change_message(self, alert_manager):
        """Test diaper change cry message mapping"""
        message = alert_manager.get_alert_message("diaper_change")
        assert message == "Baby may need a diaper change"
    
    def test_normal_unknown_message(self, alert_manager):
        """Test normal/unknown cry message mapping"""
        message = alert_manager.get_alert_message("normal_unknown")
        assert message == "Baby is crying – reason unclear"
    
    def test_invalid_cry_type_message(self, alert_manager):
        """Test message for invalid cry type"""
        message = alert_manager.get_alert_message("invalid_type")
        assert message == "Unknown cry type"
    
    # Test color coding (Requirement 5.6)
    
    def test_pain_distress_color_red(self, alert_manager):
        """Test pain/distress has red color"""
        color = alert_manager.get_alert_color("pain_distress")
        assert color == "#ef4444"  # Red
    
    def test_hunger_color_yellow(self, alert_manager):
        """Test hunger has yellow color"""
        color = alert_manager.get_alert_color("hunger")
        assert color == "#f59e0b"  # Yellow
    
    def test_sleep_discomfort_color_yellow(self, alert_manager):
        """Test sleep discomfort has yellow color"""
        color = alert_manager.get_alert_color("sleep_discomfort")
        assert color == "#f59e0b"  # Yellow
    
    def test_diaper_change_color_yellow(self, alert_manager):
        """Test diaper change has yellow color"""
        color = alert_manager.get_alert_color("diaper_change")
        assert color == "#f59e0b"  # Yellow
    
    def test_normal_unknown_color_green(self, alert_manager):
        """Test normal/unknown has green color"""
        color = alert_manager.get_alert_color("normal_unknown")
        assert color == "#10b981"  # Green
    
    def test_invalid_cry_type_color(self, alert_manager):
        """Test invalid cry type returns default gray color"""
        color = alert_manager.get_alert_color("invalid_type")
        assert color == "#6b7280"  # Gray
    
    # Test icon mapping (Requirement 5.7)
    
    def test_hunger_icon(self, alert_manager):
        """Test hunger has bottle icon"""
        icon = alert_manager.get_alert_icon("hunger")
        assert icon == "🍼"
    
    def test_sleep_discomfort_icon(self, alert_manager):
        """Test sleep discomfort has sleep icon"""
        icon = alert_manager.get_alert_icon("sleep_discomfort")
        assert icon == "😴"
    
    def test_pain_distress_icon(self, alert_manager):
        """Test pain/distress has warning icon"""
        icon = alert_manager.get_alert_icon("pain_distress")
        assert icon == "⚠️"
    
    def test_diaper_change_icon(self, alert_manager):
        """Test diaper change has diaper icon"""
        icon = alert_manager.get_alert_icon("diaper_change")
        assert icon == "🧷"
    
    def test_normal_unknown_icon(self, alert_manager):
        """Test normal/unknown has question mark icon"""
        icon = alert_manager.get_alert_icon("normal_unknown")
        assert icon == "❓"
    
    def test_invalid_cry_type_icon(self, alert_manager):
        """Test invalid cry type returns default question mark"""
        icon = alert_manager.get_alert_icon("invalid_type")
        assert icon == "❔"
    
    # Test severity mapping
    
    def test_pain_distress_severity_high(self, alert_manager):
        """Test pain/distress has high severity"""
        severity = alert_manager.get_severity("pain_distress")
        assert severity == "high"
    
    def test_hunger_severity_medium(self, alert_manager):
        """Test hunger has medium severity"""
        severity = alert_manager.get_severity("hunger")
        assert severity == "medium"
    
    def test_normal_unknown_severity_low(self, alert_manager):
        """Test normal/unknown has low severity"""
        severity = alert_manager.get_severity("normal_unknown")
        assert severity == "low"
    
    # Test status mapping
    
    def test_pain_distress_status(self, alert_manager):
        """Test pain/distress maps to distress status"""
        status = alert_manager.get_status("pain_distress")
        assert status == "distress"
    
    def test_hunger_status(self, alert_manager):
        """Test hunger maps to abnormal status"""
        status = alert_manager.get_status("hunger")
        assert status == "abnormal"
    
    def test_normal_unknown_status(self, alert_manager):
        """Test normal/unknown maps to normal status"""
        status = alert_manager.get_status("normal_unknown")
        assert status == "normal"
    
    # Test alert generation (Requirements 5.1-5.9)
    
    def test_generate_alert_structure(self, alert_manager):
        """Test generate_alert returns complete structure"""
        alert = alert_manager.generate_alert("hunger", 75.5, 60.0, 3.5)
        
        # Check all required fields are present
        assert "message" in alert
        assert "cry_type" in alert
        assert "confidence" in alert
        assert "color" in alert
        assert "icon" in alert
        assert "timestamp" in alert
        assert "severity" in alert
        assert "intensity" in alert
        assert "duration" in alert
    
    def test_generate_alert_values(self, alert_manager):
        """Test generate_alert has correct values"""
        alert = alert_manager.generate_alert("hunger", 75.5, 60.0, 3.5)
        
        assert alert["message"] == "Baby may be hungry"
        assert alert["cry_type"] == "hunger"
        assert alert["confidence"] == 75.5
        assert alert["color"] == "#f59e0b"
        assert alert["icon"] == "🍼"
        assert alert["severity"] == "medium"
        assert alert["intensity"] == 60.0
        assert alert["duration"] == 3.5
        assert isinstance(alert["timestamp"], float)
        assert alert["timestamp"] > 0
    
    def test_generate_alert_all_cry_types(self, alert_manager):
        """Test generate_alert works for all cry types"""
        cry_types = ["hunger", "sleep_discomfort", "pain_distress", 
                     "diaper_change", "normal_unknown"]
        
        for cry_type in cry_types:
            alert = alert_manager.generate_alert(cry_type, 80.0)
            assert alert["cry_type"] == cry_type
            assert alert["message"] == alert_manager.get_alert_message(cry_type)
            assert alert["color"] == alert_manager.get_alert_color(cry_type)
            assert alert["icon"] == alert_manager.get_alert_icon(cry_type)
    
    def test_generate_alert_default_intensity_duration(self, alert_manager):
        """Test generate_alert with default intensity and duration"""
        alert = alert_manager.generate_alert("hunger", 75.0)
        
        assert alert["intensity"] == 0.0
        assert alert["duration"] == 0.0
    
    # Test dashboard updates (Requirement 11.2)
    
    def test_update_dashboard_cry_detection(self, alert_manager, mock_shared_data):
        """Test dashboard update modifies cryDetection section"""
        alert = alert_manager.generate_alert("hunger", 75.5, 60.0, 3.5)
        alert_manager.update_dashboard(mock_shared_data, alert)
        
        cry_data = mock_shared_data["cryDetection"]
        assert cry_data["status"] == "abnormal"
        assert cry_data["cryType"] == "Baby may be hungry"
        assert cry_data["confidence"] == 75
        assert cry_data["intensity"] == 60
        assert cry_data["duration"] == 3
        assert cry_data["lastDetected"] != "None"
    
    def test_update_dashboard_timestamp_format(self, alert_manager, mock_shared_data):
        """Test dashboard timestamp is formatted correctly"""
        alert = alert_manager.generate_alert("hunger", 75.0)
        alert_manager.update_dashboard(mock_shared_data, alert)
        
        last_detected = mock_shared_data["cryDetection"]["lastDetected"]
        # Should be in HH:MM:SS format
        assert len(last_detected) == 8
        assert last_detected[2] == ":"
        assert last_detected[5] == ":"
    
    def test_update_dashboard_adds_medium_severity_alert(self, alert_manager, mock_shared_data):
        """Test medium severity alerts are added to alerts list"""
        alert = alert_manager.generate_alert("hunger", 75.0)
        alert_manager.update_dashboard(mock_shared_data, alert)
        
        assert len(mock_shared_data["alerts"]) == 1
        alert_entry = mock_shared_data["alerts"][0]
        assert alert_entry["type"] == "warning"
        assert "Baby may be hungry" in alert_entry["description"]
        assert "🍼" in alert_entry["description"]
    
    def test_update_dashboard_adds_high_severity_alert(self, alert_manager, mock_shared_data):
        """Test high severity alerts are added to alerts list"""
        alert = alert_manager.generate_alert("pain_distress", 85.0)
        alert_manager.update_dashboard(mock_shared_data, alert)
        
        assert len(mock_shared_data["alerts"]) == 1
        alert_entry = mock_shared_data["alerts"][0]
        assert alert_entry["type"] == "critical"
        assert "immediate attention needed" in alert_entry["description"]
    
    def test_update_dashboard_no_alert_for_low_severity(self, alert_manager, mock_shared_data):
        """Test low severity does not add to alerts list"""
        alert = alert_manager.generate_alert("normal_unknown", 50.0)
        alert_manager.update_dashboard(mock_shared_data, alert)
        
        # Should not add to alerts list
        assert len(mock_shared_data["alerts"]) == 0
    
    def test_update_dashboard_adds_event(self, alert_manager, mock_shared_data):
        """Test all alerts add an event to events list"""
        alert = alert_manager.generate_alert("hunger", 75.0)
        alert_manager.update_dashboard(mock_shared_data, alert)
        
        assert len(mock_shared_data["events"]) == 1
        event = mock_shared_data["events"][0]
        assert "Cry detected" in event["description"]
        assert "Baby may be hungry" in event["description"]
    
    def test_update_dashboard_limits_alerts_to_10(self, alert_manager, mock_shared_data):
        """Test alerts list is limited to 10 entries"""
        # Add 15 alerts
        for i in range(15):
            alert = alert_manager.generate_alert("hunger", 75.0)
            alert_manager.update_dashboard(mock_shared_data, alert)
        
        # Should only keep last 10
        assert len(mock_shared_data["alerts"]) == 10
    
    def test_update_dashboard_limits_events_to_20(self, alert_manager, mock_shared_data):
        """Test events list is limited to 20 entries"""
        # Add 25 events
        for i in range(25):
            alert = alert_manager.generate_alert("hunger", 75.0)
            alert_manager.update_dashboard(mock_shared_data, alert)
        
        # Should only keep last 20
        assert len(mock_shared_data["events"]) == 20
    
    def test_update_dashboard_pain_distress(self, alert_manager, mock_shared_data):
        """Test pain/distress updates dashboard with distress status"""
        alert = alert_manager.generate_alert("pain_distress", 90.0, 80.0, 5.0)
        alert_manager.update_dashboard(mock_shared_data, alert)
        
        assert mock_shared_data["cryDetection"]["status"] == "distress"
        assert mock_shared_data["cryDetection"]["cryType"] == "Baby shows signs of pain – immediate attention needed"
    
    def test_update_dashboard_multiple_cry_types(self, alert_manager, mock_shared_data):
        """Test dashboard updates correctly for different cry types"""
        cry_types = ["hunger", "sleep_discomfort", "pain_distress", 
                     "diaper_change", "normal_unknown"]
        
        for cry_type in cry_types:
            alert = alert_manager.generate_alert(cry_type, 75.0)
            alert_manager.update_dashboard(mock_shared_data, alert)
            
            # Verify status is updated correctly
            expected_status = alert_manager.get_status(cry_type)
            assert mock_shared_data["cryDetection"]["status"] == expected_status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
