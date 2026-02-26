"""
Gemini API Client for generating AI insights from cry detection data
"""

import google.generativeai as genai
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    pass


class GeminiInsightsClient:
    """Client for generating AI insights using Google's Gemini API"""
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini client with API key
        
        Args:
            api_key: Google Gemini API key
        """
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
        logger.info("Gemini client initialized successfully")
    
    def generate_insights(self, cry_data: Dict[str, Any]) -> str:
        """
        Generate AI insights from cry detection data
        
        Args:
            cry_data: Dictionary containing cry type, confidence, and features
            
        Returns:
            String containing AI-generated insights and analysis
            
        Raises:
            GeminiAPIError: If API request fails
        """
        try:
            # Format the prompt
            prompt = self._format_prompt(cry_data)
            
            # Call Gemini API
            logger.info("Requesting insights from Gemini API")
            response = self.model.generate_content(prompt)
            
            # Extract insights text
            insights = response.text
            logger.info("Successfully generated insights from Gemini")
            
            return insights
            
        except Exception as e:
            error_msg = f"Gemini API request failed: {str(e)}"
            logger.error(error_msg)
            raise GeminiAPIError(error_msg) from e
    
    def _format_prompt(self, cry_data: Dict[str, Any]) -> str:
        """
        Format cry detection data into a medical-appropriate prompt
        
        Args:
            cry_data: Dictionary containing cry detection parameters
            
        Returns:
            Formatted prompt string
        """
        cry_type = cry_data.get('cry_type', 'unknown')
        confidence = cry_data.get('confidence', 0)
        
        # Extract features
        features = cry_data.get('features', {})
        pitch = features.get('pitch', 0)
        pitch_std = features.get('pitch_std', 0)
        intensity_db = features.get('intensity_db', 0)
        spectral_centroid = features.get('spectral_centroid', 0)
        duration = features.get('duration', 0)
        
        prompt = f"""Analyze this infant cry detection data and provide insights for caregivers:

Cry Type: {cry_type.capitalize()}
Confidence: {confidence:.1f}%

Audio Features:
- Pitch: {pitch:.1f} Hz
- Pitch Variation: {pitch_std:.1f} Hz
- Intensity: {intensity_db:.1f} dB
- Spectral Centroid: {spectral_centroid:.1f} Hz
- Duration: {duration:.1f} seconds

Please provide:
1. Analysis of the cry pattern and what it indicates
2. Possible causes and interpretations
3. Recommended caregiver responses
4. Any notable patterns in the audio features

Keep the language clear, compassionate, and appropriate for caregivers. Focus on actionable guidance."""
        
        return prompt
