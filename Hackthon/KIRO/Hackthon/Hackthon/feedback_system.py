# feedback_system.py
"""
Feedback System Module for Neonatal Cry Detection System

This module provides functionality for collecting and storing caregiver feedback
to improve model accuracy over time. It stores only feature vectors and labels,
not raw audio data, to protect privacy.

Requirements: 6.3, 6.4, 8.3
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import time


class FeedbackSystem:
    """
    Collects and manages caregiver feedback for model improvement.
    
    Responsibilities:
    - Store feedback entries with features and labels (no raw audio)
    - Retrieve feedback data for model retraining
    - Export feedback data to files
    - Ensure privacy by never storing raw audio
    """
    
    def __init__(self, storage_path: str = "./feedback_data"):
        """
        Initialize feedback system with storage location.
        
        Args:
            storage_path: Directory path for storing feedback data (default: "./feedback_data")
        """
        self.storage_path = storage_path
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(self.storage_path):
            try:
                os.makedirs(self.storage_path)
            except Exception as e:
                print(f"Warning: Could not create feedback storage directory: {e}")
    
    def record_feedback(self,
                       features: Dict[str, Any],
                       predicted_type: str,
                       actual_type: str,
                       confidence: float,
                       timestamp: Optional[float] = None) -> bool:
        """
        Store a feedback entry with features and labels.
        
        This method stores caregiver corrections along with the extracted
        audio features. Raw audio is NEVER stored to protect privacy.
        
        Args:
            features: Dictionary of extracted audio features (from FeatureExtractor)
            predicted_type: Model's original prediction (one of five cry types)
            actual_type: Caregiver's correction (one of five cry types)
            confidence: Original confidence score (0-100)
            timestamp: Feedback submission time (defaults to current time)
            
        Returns:
            True if feedback was successfully stored, False otherwise
            
        Validates: Requirements 6.3, 8.3
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Create feedback entry
        feedback_entry = {
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "predicted_type": predicted_type,
            "actual_type": actual_type,
            "confidence": float(confidence),
            "features": self._serialize_features(features)
        }
        
        # Generate unique filename based on timestamp
        filename = f"feedback_{int(timestamp * 1000)}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        # Save to file
        try:
            with open(filepath, 'w') as f:
                json.dump(feedback_entry, f, indent=2)
            return True
        except Exception as e:
            print(f"Error storing feedback: {e}")
            return False
    
    def _serialize_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert feature dictionary to JSON-serializable format.
        
        Handles numpy arrays and other non-serializable types.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            JSON-serializable dictionary
        """
        try:
            import numpy as np
            has_numpy = True
        except ImportError:
            has_numpy = False
        
        serialized = {}
        for key, value in features.items():
            if has_numpy:
                if isinstance(value, np.ndarray):
                    # Convert numpy arrays to lists
                    serialized[key] = value.tolist()
                elif isinstance(value, (np.integer, np.floating)):
                    # Convert numpy scalars to Python types
                    serialized[key] = float(value)
                else:
                    # Keep as is
                    serialized[key] = value
            else:
                # No numpy available, assume already serializable
                if hasattr(value, 'tolist'):
                    serialized[key] = value.tolist()
                else:
                    serialized[key] = value
        
        return serialized
    
    def _deserialize_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert JSON-loaded features back to appropriate types.
        
        Converts lists back to numpy arrays where appropriate.
        
        Args:
            features: Dictionary loaded from JSON
            
        Returns:
            Dictionary with proper types
        """
        try:
            import numpy as np
            has_numpy = True
        except ImportError:
            has_numpy = False
        
        deserialized = {}
        for key, value in features.items():
            if has_numpy and key in ['mfccs', 'frequency_spectrum'] and isinstance(value, list):
                # Convert lists back to numpy arrays for these features
                deserialized[key] = np.array(value)
            else:
                deserialized[key] = value
        
        return deserialized
    
    def get_feedback_data(self) -> List[Dict[str, Any]]:
        """
        Retrieve all feedback entries for model retraining.
        
        Loads all feedback files from the storage directory and returns
        them as a list of dictionaries.
        
        Returns:
            List of feedback entry dictionaries, each containing:
            - timestamp: Submission time
            - datetime: Human-readable timestamp
            - predicted_type: Original prediction
            - actual_type: Corrected label
            - confidence: Original confidence score
            - features: Extracted audio features
            
        Validates: Requirements 6.4
        """
        feedback_data = []
        
        # Check if storage directory exists
        if not os.path.exists(self.storage_path):
            return feedback_data
        
        # Load all feedback files
        try:
            for filename in os.listdir(self.storage_path):
                if filename.startswith("feedback_") and filename.endswith(".json"):
                    filepath = os.path.join(self.storage_path, filename)
                    try:
                        with open(filepath, 'r') as f:
                            entry = json.load(f)
                            # Deserialize features
                            entry['features'] = self._deserialize_features(entry['features'])
                            feedback_data.append(entry)
                    except Exception as e:
                        print(f"Warning: Could not load feedback file {filename}: {e}")
                        continue
        except Exception as e:
            print(f"Error reading feedback directory: {e}")
        
        # Sort by timestamp (oldest first)
        feedback_data.sort(key=lambda x: x['timestamp'])
        
        return feedback_data
    
    def export_feedback(self, output_path: str) -> bool:
        """
        Export all feedback data to a single file for model retraining.
        
        Consolidates all feedback entries into a single JSON file that can
        be used for batch model retraining.
        
        Args:
            output_path: File path for the exported data (e.g., "feedback_export.json")
            
        Returns:
            True if export was successful, False otherwise
            
        Validates: Requirements 6.4
        """
        # Get all feedback data
        feedback_data = self.get_feedback_data()
        
        if len(feedback_data) == 0:
            print("No feedback data to export")
            return False
        
        # Create export structure
        export_data = {
            "export_timestamp": time.time(),
            "export_datetime": datetime.now().isoformat(),
            "total_entries": len(feedback_data),
            "feedback_entries": feedback_data
        }
        
        # Save to file
        try:
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"Successfully exported {len(feedback_data)} feedback entries to {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting feedback: {e}")
            return False
    
    def get_feedback_count(self) -> int:
        """
        Get the total number of feedback entries stored.
        
        Returns:
            Number of feedback entries
        """
        if not os.path.exists(self.storage_path):
            return 0
        
        try:
            count = sum(1 for f in os.listdir(self.storage_path) 
                       if f.startswith("feedback_") and f.endswith(".json"))
            return count
        except Exception as e:
            print(f"Error counting feedback entries: {e}")
            return 0
    
    def clear_feedback(self) -> bool:
        """
        Clear all stored feedback data.
        
        WARNING: This permanently deletes all feedback entries.
        Use with caution!
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.storage_path):
            return True
        
        try:
            for filename in os.listdir(self.storage_path):
                if filename.startswith("feedback_") and filename.endswith(".json"):
                    filepath = os.path.join(self.storage_path, filename)
                    os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error clearing feedback data: {e}")
            return False
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get a summary of stored feedback data.
        
        Returns:
            Dictionary containing:
            - total_entries: Total number of feedback entries
            - by_predicted_type: Count of entries by predicted type
            - by_actual_type: Count of entries by actual type
            - correction_rate: Percentage of entries where prediction was corrected
        """
        feedback_data = self.get_feedback_data()
        
        if len(feedback_data) == 0:
            return {
                "total_entries": 0,
                "by_predicted_type": {},
                "by_actual_type": {},
                "correction_rate": 0.0
            }
        
        # Count by predicted and actual types
        by_predicted = {}
        by_actual = {}
        corrections = 0
        
        for entry in feedback_data:
            predicted = entry['predicted_type']
            actual = entry['actual_type']
            
            by_predicted[predicted] = by_predicted.get(predicted, 0) + 1
            by_actual[actual] = by_actual.get(actual, 0) + 1
            
            if predicted != actual:
                corrections += 1
        
        correction_rate = (corrections / len(feedback_data)) * 100
        
        return {
            "total_entries": len(feedback_data),
            "by_predicted_type": by_predicted,
            "by_actual_type": by_actual,
            "correction_rate": correction_rate
        }
