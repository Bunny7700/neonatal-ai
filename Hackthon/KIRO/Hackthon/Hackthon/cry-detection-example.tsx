/**
 * Cry Detection Frontend Integration - Usage Examples
 * 
 * This file demonstrates how to use the cry-detection.ts module
 * in your React/TypeScript frontend application.
 */

import React, { useEffect, useState } from 'react';
import cryDetectionAPI, {
  CryDetectionAPI,
  DashboardData,
  FeedbackRequest,
  formatCryType,
  getCryStatusColor,
  getCryTypeIcon,
  getCrySeverity,
} from './cry-detection';

// ============================================================================
// Example 1: Simple Dashboard Component
// ============================================================================

export const CryDetectionDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const dashboardData = await cryDetectionAPI.getDashboardData();
        setData(dashboardData);
        setError(null);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Refresh every 3 seconds
    const interval = setInterval(fetchData, 3000);

    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return <div>Loading cry detection data...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!data) {
    return <div>No data available</div>;
  }

  const { cryDetection, patient, vitals, alerts, riskAssessment } = data;

  return (
    <div className="cry-detection-dashboard">
      {/* Patient Info */}
      <div className="patient-info">
        <h2>Patient: {patient.id}</h2>
        <p>Age: {patient.age} | Status: {patient.status}</p>
      </div>

      {/* Cry Detection Status */}
      <div 
        className="cry-status"
        style={{ 
          backgroundColor: getCryStatusColor(cryDetection.status),
          padding: '20px',
          borderRadius: '8px',
          color: 'white'
        }}
      >
        <h3>
          {getCryTypeIcon(cryDetection.cryType)} Cry Detection
        </h3>
        <p>Status: {cryDetection.status.toUpperCase()}</p>
        <p>Type: {formatCryType(cryDetection.cryType)}</p>
        <p>Confidence: {cryDetection.confidence}%</p>
        <p>Intensity: {cryDetection.intensity}/100</p>
        <p>Last Detected: {cryDetection.lastDetected}</p>
      </div>

      {/* Vital Signs */}
      <div className="vitals">
        <h3>Vital Signs</h3>
        {vitals.map((vital, index) => (
          <div key={index} className="vital-item">
            <span>{vital.title}: </span>
            <strong>{vital.value} {vital.unit}</strong>
            <span> (Normal: {vital.normalRange})</span>
            <span className={`status-${vital.status}`}>
              {vital.status === 'normal' ? ' ✅' : ' ⚠️'}
            </span>
          </div>
        ))}
      </div>

      {/* Recent Alerts */}
      <div className="alerts">
        <h3>Recent Alerts</h3>
        {alerts.slice(0, 5).map((alert, index) => (
          <div 
            key={index} 
            className={`alert alert-${alert.type}`}
            style={{ borderLeft: `4px solid ${alert.color || '#f59e0b'}` }}
          >
            <span className="alert-time">{alert.time || alert.timestamp}</span>
            <span className="alert-message">
              {alert.message || alert.description}
            </span>
          </div>
        ))}
      </div>

      {/* Risk Assessment */}
      <div className="risk-assessment">
        <h3>Risk Assessment</h3>
        <p>
          Overall Risk: <strong>{riskAssessment.overall.toUpperCase()}</strong>
          {' '}(Confidence: {riskAssessment.confidence}%)
        </p>
        <div className="risk-categories">
          {riskAssessment.categories.map((category, index) => (
            <div 
              key={index}
              className="risk-category"
              style={{ borderLeft: `4px solid ${category.color}` }}
            >
              {category.name}: {category.level}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Example 2: Cry Detection Widget (Compact)
// ============================================================================

export const CryDetectionWidget: React.FC = () => {
  const [cryData, setCryData] = useState<any>(null);

  useEffect(() => {
    const fetchCryData = async () => {
      try {
        const data = await cryDetectionAPI.getCryDetectionData();
        setCryData(data);
      } catch (err) {
        console.error('Failed to fetch cry data:', err);
      }
    };

    fetchCryData();
    const interval = setInterval(fetchCryData, 2000);
    return () => clearInterval(interval);
  }, []);

  if (!cryData) return <div>Loading...</div>;

  return (
    <div 
      className="cry-widget"
      style={{
        padding: '15px',
        borderRadius: '8px',
        backgroundColor: getCryStatusColor(cryData.status),
        color: 'white',
      }}
    >
      <div className="cry-icon" style={{ fontSize: '2em' }}>
        {getCryTypeIcon(cryData.cryType)}
      </div>
      <div className="cry-info">
        <h4>{formatCryType(cryData.cryType)}</h4>
        <p>{cryData.confidence}% confidence</p>
        <p>Intensity: {cryData.intensity}/100</p>
      </div>
    </div>
  );
};

// ============================================================================
// Example 3: Feedback Form Component
// ============================================================================

export const FeedbackForm: React.FC = () => {
  const [predictedType, setPredictedType] = useState<string>('hunger');
  const [actualType, setActualType] = useState<string>('hunger');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const cryTypes = [
    { value: 'hunger', label: '🍼 Hunger' },
    { value: 'sleep_discomfort', label: '😴 Sleep Discomfort' },
    { value: 'pain_distress', label: '⚠️ Pain/Distress' },
    { value: 'diaper_change', label: '🧷 Diaper Change' },
    { value: 'normal_unknown', label: '❓ Unknown' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);

    try {
      const feedback: FeedbackRequest = {
        predicted_type: predictedType as any,
        actual_type: actualType as any,
      };

      const response = await cryDetectionAPI.submitFeedback(feedback);
      
      if (response.status === 'success') {
        setMessage('✅ Feedback submitted successfully!');
      } else {
        setMessage('❌ Failed to submit feedback');
      }
    } catch (err) {
      setMessage(`❌ Error: ${(err as Error).message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="feedback-form">
      <h3>Submit Caregiver Feedback</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>System Predicted:</label>
          <select 
            value={predictedType} 
            onChange={(e) => setPredictedType(e.target.value)}
            disabled={submitting}
          >
            {cryTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Actual Cry Type:</label>
          <select 
            value={actualType} 
            onChange={(e) => setActualType(e.target.value)}
            disabled={submitting}
          >
            {cryTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <button type="submit" disabled={submitting}>
          {submitting ? 'Submitting...' : 'Submit Feedback'}
        </button>

        {message && (
          <div className="feedback-message">
            {message}
          </div>
        )}
      </form>
    </div>
  );
};

// ============================================================================
// Example 4: Server Status Indicator
// ============================================================================

export const ServerStatus: React.FC = () => {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const checkStatus = async () => {
      const online = await cryDetectionAPI.checkServerStatus();
      setIsOnline(online);
    };

    checkStatus();
    const interval = setInterval(checkStatus, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  if (isOnline === null) {
    return <div>Checking server status...</div>;
  }

  return (
    <div className={`server-status ${isOnline ? 'online' : 'offline'}`}>
      <span className="status-indicator">
        {isOnline ? '🟢' : '🔴'}
      </span>
      <span className="status-text">
        Server {isOnline ? 'Online' : 'Offline'}
      </span>
    </div>
  );
};

// ============================================================================
// Example 5: Using Custom API Instance
// ============================================================================

export const CustomAPIExample: React.FC = () => {
  // Create a custom API instance with different base URL
  const [api] = useState(() => new CryDetectionAPI('http://localhost:8000'));
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const systemStatus = await api.getSystemStatus();
        const dashboardData = await api.getDashboardData();
        setData({ systemStatus, dashboardData });
      } catch (err) {
        console.error('Error:', err);
      }
    };

    fetchData();
  }, [api]);

  return (
    <div>
      <h3>Custom API Instance</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

// ============================================================================
// Example 6: Vanilla JavaScript Usage (No React)
// ============================================================================

/*
// Import the API
import cryDetectionAPI from './cry-detection';

// Get dashboard data
async function updateDashboard() {
  try {
    const data = await cryDetectionAPI.getDashboardData();
    
    // Update DOM elements
    document.getElementById('cry-status').textContent = data.cryDetection.status;
    document.getElementById('cry-type').textContent = data.cryDetection.cryType;
    document.getElementById('confidence').textContent = `${data.cryDetection.confidence}%`;
    
    // Update alerts
    const alertsContainer = document.getElementById('alerts');
    alertsContainer.innerHTML = data.alerts
      .map(alert => `<div class="alert">${alert.message}</div>`)
      .join('');
      
  } catch (error) {
    console.error('Error:', error);
  }
}

// Refresh every 3 seconds
setInterval(updateDashboard, 3000);
updateDashboard();

// Submit feedback
async function submitFeedback() {
  try {
    const response = await cryDetectionAPI.submitFeedback({
      predicted_type: 'hunger',
      actual_type: 'pain_distress'
    });
    
    console.log('Feedback submitted:', response);
  } catch (error) {
    console.error('Error submitting feedback:', error);
  }
}
*/
