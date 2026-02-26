# Cry Detection Frontend Integration Guide

This guide explains how to integrate the Neonatal Cry Detection System into your frontend application using TypeScript/JavaScript.

## 📁 Files

- `cry-detection.ts` - Main TypeScript module with API client and type definitions
- `cry-detection-example.tsx` - React component examples
- `FRONTEND_INTEGRATION.md` - This file

## 🚀 Quick Start

### 1. Copy the TypeScript Module

Copy `cry-detection.ts` to your frontend project:

```bash
cp cry-detection.ts /path/to/your/frontend/src/api/
```

### 2. Install Dependencies (if needed)

The module uses native `fetch` API, so no additional dependencies are required for modern browsers.

For TypeScript projects, ensure you have:
```bash
npm install --save-dev @types/node
```

### 3. Import and Use

```typescript
import cryDetectionAPI from './api/cry-detection';

// Get dashboard data
const data = await cryDetectionAPI.getDashboardData();
console.log('Cry Status:', data.cryDetection.status);

// Submit feedback
await cryDetectionAPI.submitFeedback({
  predicted_type: 'hunger',
  actual_type: 'pain_distress'
});
```

## 📡 API Endpoints

### GET /api/dashboard

Returns complete dashboard data including:
- Cry detection status and classification
- Patient information
- Vital signs
- Recent alerts
- Risk assessment
- Motion monitoring
- Sleep position
- Breathing analysis

**Example:**
```typescript
const dashboard = await cryDetectionAPI.getDashboardData();
```

### POST /api/feedback

Submit caregiver feedback for cry classification.

**Request Body:**
```json
{
  "predicted_type": "hunger",
  "actual_type": "pain_distress"
}
```

**Valid Cry Types:**
- `hunger` - Baby may be hungry
- `sleep_discomfort` - Baby may be uncomfortable
- `pain_distress` - Baby shows signs of pain
- `diaper_change` - Baby may need a diaper change
- `normal_unknown` - Cry reason unclear

**Example:**
```typescript
const response = await cryDetectionAPI.submitFeedback({
  predicted_type: 'hunger',
  actual_type: 'pain_distress'
});
```

### GET /

Check server status and get system information.

**Example:**
```typescript
const isOnline = await cryDetectionAPI.checkServerStatus();
const systemInfo = await cryDetectionAPI.getSystemStatus();
```

## 🎨 React Component Examples

### Simple Dashboard

```tsx
import React, { useEffect, useState } from 'react';
import cryDetectionAPI, { DashboardData } from './api/cry-detection';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const dashboardData = await cryDetectionAPI.getDashboardData();
      setData(dashboardData);
    };

    fetchData();
    const interval = setInterval(fetchData, 3000); // Refresh every 3s
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h2>Cry Detection: {data.cryDetection.status}</h2>
      <p>Type: {data.cryDetection.cryType}</p>
      <p>Confidence: {data.cryDetection.confidence}%</p>
    </div>
  );
};
```

### Cry Status Widget

```tsx
import { getCryStatusColor, getCryTypeIcon } from './api/cry-detection';

export const CryWidget: React.FC<{ data: CryDetectionData }> = ({ data }) => {
  return (
    <div style={{ 
      backgroundColor: getCryStatusColor(data.status),
      padding: '20px',
      borderRadius: '8px',
      color: 'white'
    }}>
      <div style={{ fontSize: '3em' }}>
        {getCryTypeIcon(data.cryType)}
      </div>
      <h3>{data.cryType}</h3>
      <p>{data.confidence}% confidence</p>
    </div>
  );
};
```

### Feedback Form

```tsx
export const FeedbackForm: React.FC = () => {
  const [predicted, setPredicted] = useState('hunger');
  const [actual, setActual] = useState('hunger');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await cryDetectionAPI.submitFeedback({
      predicted_type: predicted as any,
      actual_type: actual as any
    });
    alert('Feedback submitted!');
  };

  return (
    <form onSubmit={handleSubmit}>
      <select value={predicted} onChange={e => setPredicted(e.target.value)}>
        <option value="hunger">🍼 Hunger</option>
        <option value="sleep_discomfort">😴 Sleep Discomfort</option>
        <option value="pain_distress">⚠️ Pain/Distress</option>
        <option value="diaper_change">🧷 Diaper Change</option>
        <option value="normal_unknown">❓ Unknown</option>
      </select>
      
      <select value={actual} onChange={e => setActual(e.target.value)}>
        {/* Same options */}
      </select>
      
      <button type="submit">Submit Feedback</button>
    </form>
  );
};
```

## 🔧 Utility Functions

The module includes helpful utility functions:

```typescript
import {
  formatCryType,
  getCryStatusColor,
  getCryTypeIcon,
  getCrySeverity,
  formatTimestamp,
  timeAgo
} from './api/cry-detection';

// Format cry type for display
formatCryType('sleep_discomfort'); // "Sleep Discomfort"

// Get color for status
getCryStatusColor('distress'); // "#ef4444" (red)

// Get icon for cry type
getCryTypeIcon('hunger'); // "🍼"

// Get severity level
getCrySeverity('pain_distress'); // "high"

// Format timestamp
formatTimestamp(1706745600); // "10:00:00 AM"

// Time ago
timeAgo(Date.now() / 1000 - 120); // "2m ago"
```

## 🌐 Vanilla JavaScript Usage

No React? No problem! Use it with vanilla JavaScript:

```javascript
import cryDetectionAPI from './cry-detection.js';

// Update dashboard
async function updateDashboard() {
  const data = await cryDetectionAPI.getDashboardData();
  
  document.getElementById('cry-status').textContent = data.cryDetection.status;
  document.getElementById('cry-type').textContent = data.cryDetection.cryType;
  document.getElementById('confidence').textContent = `${data.cryDetection.confidence}%`;
}

// Refresh every 3 seconds
setInterval(updateDashboard, 3000);
updateDashboard();
```

## 🎯 Type Definitions

All TypeScript types are included in `cry-detection.ts`:

- `DashboardData` - Complete dashboard structure
- `CryDetectionData` - Cry detection specific data
- `FeedbackRequest` - Feedback submission format
- `FeedbackResponse` - Feedback response format
- `PatientInfo` - Patient information
- `Vital` - Vital sign data
- `Alert` - Alert structure
- `RiskAssessment` - Risk assessment data

## 🔒 CORS Configuration

The backend server is configured with CORS enabled for all origins:

```python
# Already configured in run_simple_server.py
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## 🚨 Error Handling

Always wrap API calls in try-catch blocks:

```typescript
try {
  const data = await cryDetectionAPI.getDashboardData();
  // Handle success
} catch (error) {
  console.error('API Error:', error);
  // Handle error - show user message, retry, etc.
}
```

## 📊 Data Refresh Recommendations

- **Dashboard Data**: Refresh every 2-3 seconds
- **Cry Detection Only**: Refresh every 1-2 seconds
- **Server Status**: Check every 10-30 seconds
- **Feedback**: Submit immediately on user action

## 🎨 Styling Recommendations

### Status Colors

```css
.status-normal { background-color: #10b981; } /* Green */
.status-abnormal { background-color: #f59e0b; } /* Yellow */
.status-distress { background-color: #ef4444; } /* Red */
```

### Alert Types

```css
.alert-info { border-left: 4px solid #3b82f6; } /* Blue */
.alert-warning { border-left: 4px solid #f59e0b; } /* Yellow */
.alert-critical { border-left: 4px solid #ef4444; } /* Red */
```

## 🔄 Real-time Updates

For real-time updates, use polling:

```typescript
useEffect(() => {
  const interval = setInterval(async () => {
    const data = await cryDetectionAPI.getDashboardData();
    setDashboardData(data);
  }, 3000); // 3 second refresh

  return () => clearInterval(interval);
}, []);
```

For production, consider using WebSockets for true real-time updates.

## 📱 Mobile Considerations

The API works on mobile browsers. Consider:

- Longer refresh intervals on mobile to save battery
- Offline detection and graceful degradation
- Touch-friendly UI for feedback forms

## 🧪 Testing

Test the API connection:

```typescript
// Check if server is online
const isOnline = await cryDetectionAPI.checkServerStatus();
console.log('Server online:', isOnline);

// Get system info
const systemInfo = await cryDetectionAPI.getSystemStatus();
console.log('System:', systemInfo);

// Test dashboard fetch
const data = await cryDetectionAPI.getDashboardData();
console.log('Dashboard data:', data);
```

## 🐛 Troubleshooting

### Server Not Responding

```typescript
const isOnline = await cryDetectionAPI.checkServerStatus();
if (!isOnline) {
  console.error('Server is offline. Please start run_simple_server.py');
}
```

### CORS Errors

Ensure the backend server is running with CORS enabled. The server should show:
```
Access-Control-Allow-Origin: *
```

### Type Errors

Make sure you're using the correct cry types:
- `hunger`
- `sleep_discomfort`
- `pain_distress`
- `diaper_change`
- `normal_unknown`

## 📚 Additional Resources

- See `cry-detection-example.tsx` for complete React examples
- Check `run_simple_server.py` for backend API implementation
- Review `RUNNING_THE_PROJECT.md` for server setup

## 🎉 Complete Example

Here's a complete working example:

```tsx
import React, { useEffect, useState } from 'react';
import cryDetectionAPI, {
  DashboardData,
  getCryStatusColor,
  getCryTypeIcon,
  formatCryType
} from './api/cry-detection';

export const CryDetectionApp: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const dashboardData = await cryDetectionAPI.getDashboardData();
        setData(dashboardData);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data available</div>;

  const { cryDetection, patient, vitals } = data;

  return (
    <div className="app">
      <header>
        <h1>🏥 Neonatal Cry Detection System</h1>
        <p>Patient: {patient.id} | {patient.age}</p>
      </header>

      <div 
        className="cry-status"
        style={{
          backgroundColor: getCryStatusColor(cryDetection.status),
          padding: '30px',
          borderRadius: '12px',
          color: 'white',
          textAlign: 'center'
        }}
      >
        <div style={{ fontSize: '4em' }}>
          {getCryTypeIcon(cryDetection.cryType)}
        </div>
        <h2>{formatCryType(cryDetection.cryType)}</h2>
        <p>Confidence: {cryDetection.confidence}%</p>
        <p>Intensity: {cryDetection.intensity}/100</p>
      </div>

      <div className="vitals">
        <h3>Vital Signs</h3>
        {vitals.map((vital, i) => (
          <div key={i}>
            {vital.title}: {vital.value} {vital.unit}
            {vital.status === 'normal' ? ' ✅' : ' ⚠️'}
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 🚀 Next Steps

1. Copy `cry-detection.ts` to your project
2. Import and use the API client
3. Build your UI components
4. Test with the running backend server
5. Deploy to production!

Happy coding! 🎉
