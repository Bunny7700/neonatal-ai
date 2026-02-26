"""
Alert Manager Module for Neonatal Cry Detection System

This module generates and manages alerts for different cry types, providing
human-readable messages, color-coded visual indicators, and dashboard updates.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.9
"""

from typing import Dict, Any
from datetime import datetime
import time


class AlertManager:
    """
    Manages alert generation and display for cry detection system.
    
    Responsibilities:
    - Map cry types to human-readable messages
    - Assign color codes based on severity
    - Assign icons for visual representation
    - Generate complete alert structures
    - Update dashboard with alert information
    """
    
    # Cry type to message mapping - Simplified to 3 categories
    CRY_MESSAGES = {
        "hunger": "Baby may be hungry 🍼",
        "sleep": "Baby is tired and needs sleep 😴",
        "discomfort": "Baby is uncomfortable or in distress ⚠️"
    }
    
    # Cry type to color code mapping - 3 categories
    # Red for discomfort/distress, yellow for hunger, blue for sleep
    CRY_COLORS = {
        "discomfort": "#ef4444",    # Red - high severity (pain/distress)
        "hunger": "#f59e0b",        # Yellow/Orange - medium severity
        "sleep": "#3b82f6"          # Blue - medium severity (tiredness)
    }
    
    # Cry type to icon mapping - 3 categories
    CRY_ICONS = {
        "hunger": "🍼",
        "sleep": "😴",
        "discomfort": "⚠️"
    }
    
    # Cry type to severity level mapping - 3 categories
    CRY_SEVERITY = {
        "discomfort": "high",    # Distress/pain needs immediate attention
        "hunger": "medium",      # Needs attention soon
        "sleep": "medium"        # Needs attention soon
    }
    
    # Cry type to dashboard status mapping - 3 categories
    CRY_STATUS = {
        "discomfort": "distress",   # High priority
        "hunger": "abnormal",       # Medium priority
        "sleep": "abnormal"         # Medium priority
    }
    
    def __init__(self):
        """Initialize the AlertManager."""
        pass
    
    def get_alert_message(self, cry_type: str) -> str:
        """
        Get human-readable message for a cry type.
        
        Args:
            cry_type: One of the three cry categories (hunger, sleep, discomfort)
            
        Returns:
            Human-readable alert message
            
        Requirements: 5.1, 5.2, 5.3
        """
        return self.CRY_MESSAGES.get(cry_type, "Unknown cry type")
    
    def get_alert_color(self, cry_type: str) -> str:
        """
        Get color code for a cry type.
        
        Args:
            cry_type: One of the three cry categories (hunger, sleep, discomfort)
            
        Returns:
            Hex color code string
            
        Requirement: 5.6
        """
        return self.CRY_COLORS.get(cry_type, "#6b7280")  # Default gray
    
    def get_alert_icon(self, cry_type: str) -> str:
        """
        Get icon identifier for a cry type.
        
        Args:
            cry_type: One of the three cry categories (hunger, sleep, discomfort)
            
        Returns:
            Icon emoji or identifier string
            
        Requirement: 5.7
        """
        return self.CRY_ICONS.get(cry_type, "❔")  # Default question mark
    
    def get_severity(self, cry_type: str) -> str:
        """
        Get severity level for a cry type.
        
        Args:
            cry_type: One of the three cry categories (hunger, sleep, discomfort)
            
        Returns:
            Severity level: "medium" or "high"
        """
        return self.CRY_SEVERITY.get(cry_type, "medium")
    
    def get_status(self, cry_type: str) -> str:
        """
        Get dashboard status for a cry type.
        
        Args:
            cry_type: One of the three cry categories (hunger, sleep, discomfort)
            
        Returns:
            Status: "abnormal" or "distress"
        """
        return self.CRY_STATUS.get(cry_type, "abnormal")
    
    def generate_alert(self, cry_type: str, confidence: float, 
                      intensity: float = 0.0, duration: float = 0.0) -> Dict[str, Any]:
        """
        Generate complete alert structure for a cry detection.
        
        Args:
            cry_type: One of the three cry categories (hunger, sleep, discomfort)
            confidence: Confidence score (0-100)
            intensity: Cry intensity (0-100), optional
            duration: Cry duration in seconds, optional
            
        Returns:
            Dictionary containing complete alert information:
            - message: Human-readable alert message
            - cry_type: Cry category
            - confidence: Confidence score
            - color: Color code for visual indicator
            - icon: Icon identifier
            - timestamp: Alert generation timestamp
            - severity: Severity level (medium/high)
            - intensity: Cry intensity
            - duration: Cry duration
            
        Requirements: 5.1-5.9
        """
        timestamp = time.time()
        
        alert_data = {
            "message": self.get_alert_message(cry_type),
            "cry_type": cry_type,
            "confidence": confidence,
            "color": self.get_alert_color(cry_type),
            "icon": self.get_alert_icon(cry_type),
            "timestamp": timestamp,
            "severity": self.get_severity(cry_type),
            "intensity": intensity,
            "duration": duration
        }
        
        return alert_data
    
    def update_dashboard(self, shared_data: Dict[str, Any], alert_data: Dict[str, Any]) -> None:
        """
        Update the shared dashboard data structure with alert information.
        
        Args:
            shared_data: Reference to the shared dashboard_data dictionary
            alert_data: Alert data from generate_alert()
            
        Updates the following fields in shared_data["cryDetection"]:
        - status: "normal", "abnormal", or "distress"
        - cryType: Human-readable cry type
        - confidence: Confidence score
        - intensity: Cry intensity
        - duration: Cry duration
        - lastDetected: Formatted timestamp
        
        Also adds alert to shared_data["alerts"] list if severity is medium or high.
        
        Requirement: 11.2 (Dashboard integration)
        """
        cry_type = alert_data["cry_type"]
        
        # Update cry detection section
        shared_data["cryDetection"]["status"] = self.get_status(cry_type)
        shared_data["cryDetection"]["cryType"] = alert_data["message"]
        shared_data["cryDetection"]["confidence"] = int(alert_data["confidence"])
        shared_data["cryDetection"]["intensity"] = int(alert_data["intensity"])
        shared_data["cryDetection"]["duration"] = int(alert_data["duration"])
        
        # Format timestamp
        dt = datetime.fromtimestamp(alert_data["timestamp"])
        shared_data["cryDetection"]["lastDetected"] = dt.strftime("%H:%M:%S")
        
        # Add to alerts list (all 3 categories are medium or high severity)
        alert_entry = {
            "time": dt.strftime("%H:%M:%S"),
            "type": "warning" if alert_data["severity"] == "medium" else "critical",
            "description": f"{alert_data['icon']} {alert_data['message']} (Confidence: {int(alert_data['confidence'])}%)",
            "color": alert_data["color"]
        }
        
        # Add to beginning of alerts list
        shared_data["alerts"].insert(0, alert_entry)
        
        # Keep only last 10 alerts
        if len(shared_data["alerts"]) > 10:
            shared_data["alerts"] = shared_data["alerts"][:10]
        
        # Update events log
        event_entry = {
            "time": dt.strftime("%H:%M:%S"),
            "type": "warning" if alert_data["severity"] == "medium" else "critical",
            "description": f"Cry detected: {alert_data['message']}"
        }
        shared_data["events"].insert(0, event_entry)
        
        # Keep only last 20 events
        if len(shared_data["events"]) > 20:
            shared_data["events"] = shared_data["events"][:20]
