import React, * as react from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Brain, Thermometer, AlertCircle, Clock } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

// ============================================
// DATA STRUCTURE - Ready for API Integration
// ============================================

// This is where you'll fetch from your Python backend
const fetchDashboardData = async () => {
  // TODO: Replace with actual API calls to your ML backends

  // Example integration structure:
  // const motionState = await fetch('http://localhost:5000/api/motion').then(r => r.json());
  // const cryAnalysis = await fetch('http://localhost:5001/api/cry-detection').then(r => r.json());
  // const sleepPosition = await fetch('http://localhost:5002/api/sleep-position').then(r => r.json());
  // const breathing = await fetch('http://localhost:5003/api/breathing').then(r => r.json());
  // const faceAnalysis = await fetch('http://localhost:5004/api/face-analysis').then(r => r.json());

  // For now, return dummy data with the EXACT structure your backends should provide
  return {
    // Motion monitoring from your OpenCV backend (already built)
    motionMonitoring: {
      status: "SAFE",  // SAFE / MONITOR / ALERT
      stillTime: 6,
      motion: 1.24,
      confidence: 82,
      alertActive: false
    },

    // Cry Detection AI (new)
    cryDetection: {
      status: "normal",  // normal / abnormal / distress
      cryType: "None detected",  // hunger, pain, discomfort, none
      intensity: 0,  // 0-100
      duration: 0,  // seconds
      confidence: 95,
      lastDetected: "No cry in last 15 min",
      audioWaveform: [0.2, 0.5, 0.8, 1.2, 0.9, 0.4, 0.1]  // For visualization
    },

    // Sleep Position Monitoring (new)
    sleepPosition: {
      position: "Back",  // Back, Side, Stomach, Unknown
      status: "safe",  // safe / warning / unsafe
      riskLevel: "low",  // low / medium / high
      timeInPosition: 45,  // minutes
      confidence: 92,
      recommendations: "Position is optimal for breathing",
      positionHistory: [
        { time: "13:00", position: "Back" },
        { time: "12:30", position: "Side" },
        { time: "12:00", position: "Back" }
      ]
    },

    // Breathing Pattern Analysis (new)
    breathingAnalysis: {
      rate: 42,  // breaths per minute
      pattern: "Regular",  // Regular, Irregular, Apnea detected
      status: "normal",  // normal / concerning / critical
      oxygenLevel: 98,  // SpO2 percentage
      confidence: 89,
      irregularities: 0,  // count in last hour
      trend: "stable"  // improving / stable / declining
    },

    // Face & Distress Detection (new)
    faceAnalysis: {
      faceDetected: true,
      distressLevel: "none",  // none / mild / moderate / severe
      emotionalState: "calm",  // calm, fussy, crying, sleeping
      facialMovement: "minimal",  // minimal, moderate, active
      eyesOpen: false,
      mouthOpen: false,
      confidence: 88,
      alerts: []
    },
    patient: {
      id: "NB-2026-001",
      age: "3 days old",
      weight: "3.2 kg",
      gestationalAge: "38 weeks",
      admissionDate: "Jan 21, 2026",
      status: "Stable"
    },
    aiStatus: [
      { title: "Cry Pattern", value: "Normal", confidence: 92, note: "Audio-based AI analysis", status: "normal" },
      { title: "Sleep Position", value: "Safe", confidence: 95, note: "Posture classification model", status: "normal" },
      { title: "Body Temperature", value: "36.8 °C", confidence: 98, note: "Infrared monitoring", status: "normal" }
    ],
    vitals: [
      { title: "Heart Rate", value: 142, unit: "bpm", normalRange: "120-160", status: "normal" },
      { title: "Respiratory Rate", value: 45, unit: "breaths/min", normalRange: "40-60", status: "normal" },
      { title: "Oxygen Saturation", value: 98, unit: "%", normalRange: "95-100", status: "normal" }
    ],
    alerts: [
      { type: "normal", message: "All vital signs within normal parameters", timestamp: "Just now" },
      { type: "warning", message: "Slight increase in respiratory rate detected - monitoring closely", timestamp: "5 mins ago" },
      { type: "info", message: "Feeding scheduled in 30 minutes", timestamp: "10 mins ago" }
    ],
    riskAssessment: {
      overall: "low",
      confidence: 94,
      categories: [
        { name: "Respiratory", level: "Low", color: "#10b981" },
        { name: "Cardiac", level: "Low", color: "#10b981" },
        { name: "Neurological", level: "Low", color: "#10b981" },
        { name: "Thermal", level: "Low", color: "#10b981" }
      ]
    },
    trainingData: [
      { epoch: 1, accuracy: 62, loss: 0.92 },
      { epoch: 2, accuracy: 68, loss: 0.81 },
      { epoch: 3, accuracy: 74, loss: 0.69 },
      { epoch: 4, accuracy: 81, loss: 0.54 },
      { epoch: 5, accuracy: 88, loss: 0.38 }
    ],
    events: [
      { time: "13:52", type: "measurement", description: "Vital signs recorded - all normal" },
      { time: "13:45", type: "alert", description: "Respiratory rate spike detected" },
      { time: "13:30", type: "activity", description: "Position changed - Back to side" },
      { time: "13:00", type: "care", description: "Feeding completed successfully" },
      { time: "12:45", type: "measurement", description: "Temperature check: 36.8°C" },
      { time: "12:30", type: "activity", description: "Diaper changed" }
    ]
  };
};

function App() {
  const [data, setData] = react.useState<any>(null);
  const [lastUpdated, setLastUpdated] = react.useState(new Date().toLocaleTimeString());

  // Load data on mount
  react.useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard`);
        if (!response.ok) throw new Error('Failed to fetch');
        const dashboardData = await response.json();
        setData(dashboardData);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    // Initial load
    loadData();

    // Poll every 1 second for near real-time updates
    const interval = setInterval(() => {
      loadData();
      setLastUpdated(new Date().toLocaleTimeString());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (!data) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#64748b'
      }}>
        Loading dashboard data...
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', fontFamily: 'system-ui, sans-serif' }}>
      {/* Professional Header */}
      <div style={{
        backgroundColor: '#ffffff',
        padding: '24px 48px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        borderBottom: '3px solid #3b82f6'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                backgroundColor: '#3b82f6',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px',
                color: '#ffffff',
                fontWeight: 700
              }}>
                👶
              </div>
              <div>
                <h1 style={{ fontSize: '28px', margin: 0, color: '#0f172a', fontWeight: 700, letterSpacing: '-0.5px' }}>
                  Neonatal AI Monitoring System
                </h1>
                <p style={{ color: '#64748b', fontSize: '14px', margin: 0, marginTop: '2px' }}>
                  Real-time AI-assisted neonatal care & monitoring
                </p>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <div style={{
              backgroundColor: '#f0fdf4',
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid #86efac'
            }}>
              <p style={{ fontSize: '12px', color: '#15803d', margin: 0 }}>
                🟢 System Active
              </p>
            </div>
            <button style={{
              padding: '10px 20px',
              backgroundColor: '#3b82f6',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 2px 4px rgba(59,130,246,0.3)'
            }}>
              📊 Export Report
            </button>
            <button style={{
              padding: '10px 20px',
              backgroundColor: '#ef4444',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 2px 4px rgba(239,68,68,0.3)'
            }}>
              🚨 Emergency Contact
            </button>
          </div>
        </div>

        <div style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #e2e8f0',
          display: 'flex',
          gap: '32px',
          fontSize: '13px'
        }}>
          <span style={{ color: '#64748b' }}>
            <strong style={{ color: '#0f172a' }}>Last Updated:</strong> {lastUpdated}
          </span>
          <span style={{ color: '#64748b' }}>
            <strong style={{ color: '#0f172a' }}>Monitoring Since:</strong> Jan 21, 2026 08:30 AM
          </span>
          <span style={{ color: '#64748b' }}>
            <strong style={{ color: '#0f172a' }}>Session Duration:</strong> 5h 22m
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ padding: '32px 48px', maxWidth: '1600px', margin: '0 auto' }}>
        {/* Side-by-Side: Camera + Motion Monitoring */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {/* Left: Live Camera Feed */}
          <SectionContainer title="Live Baby Monitor" accentColor="#3b82f6">
            <CameraMonitor motionData={data.motionMonitoring} />
          </SectionContainer>

          {/* Right: Motion Monitoring Dashboard */}
          <SectionContainer title="Real-Time Motion Monitoring" accentColor="#3b82f6">
            <MotionMonitoringCard motion={data.motionMonitoring} />
          </SectionContainer>
        </div>

        {/* Patient Information */}
        <PatientInfoPanel patient={data.patient} />
        <div style={{ height: '32px' }} />

        {/* AI Detection Grid - All AI Models */}
        <SectionContainer title="AI Detection Systems" accentColor="#8b5cf6">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <CryDetectionCard cry={data.cryDetection} />
            <SleepPositionCard sleep={data.sleepPosition} />
            <BreathingAnalysisCard breathing={data.breathingAnalysis} />
            <FaceAnalysisCard face={data.faceAnalysis} />
          </div>
        </SectionContainer>

        {/* AI Status Cards */}
        <div style={{
          backgroundColor: '#ffffff',
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '32px',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <div style={{
              width: '4px',
              height: '24px',
              backgroundColor: '#8b5cf6',
              borderRadius: '2px'
            }}></div>
            <h2 style={{ margin: 0, fontSize: '20px', color: '#0f172a', fontWeight: 600 }}>
              AI-Powered Health Monitoring
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            {data.aiStatus.map((item: any, idx: number) => (
              <StatusCard key={idx} {...item} />
            ))}
          </div>
        </div>

        {/* Vital Signs */}
        <div style={{
          backgroundColor: '#ffffff',
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '32px',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <div style={{
              width: '4px',
              height: '24px',
              backgroundColor: '#ef4444',
              borderRadius: '2px'
            }}></div>
            <h2 style={{ margin: 0, fontSize: '20px', color: '#0f172a', fontWeight: 600 }}>
              Vital Signs Monitoring
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            {data.vitals.map((vital: any, idx: number) => (
              <VitalSignCard key={idx} {...vital} />
            ))}
          </div>
        </div>

        {/* Two Column Layout: Events + Training */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
          {/* Event Timeline */}
          <div style={{
            backgroundColor: '#ffffff',
            padding: '24px',
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <div style={{
                width: '4px',
                height: '24px',
                backgroundColor: '#10b981',
                borderRadius: '2px'
              }}></div>
              <h2 style={{ margin: 0, fontSize: '20px', color: '#0f172a', fontWeight: 600 }}>
                Recent Events
              </h2>
            </div>
            <EventTimeline events={data.events} />
          </div>

          {/* Training Chart */}
          <div style={{
            backgroundColor: '#ffffff',
            padding: '24px',
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <div style={{
                width: '4px',
                height: '24px',
                backgroundColor: '#f59e0b',
                borderRadius: '2px'
              }}></div>
              <h2 style={{ margin: 0, fontSize: '20px', color: '#0f172a', fontWeight: 600 }}>
                AI Model Performance
              </h2>
            </div>
            <TrainingChart data={data.trainingData} />
          </div>
        </div>

        {/* Alerts */}
        <div style={{
          backgroundColor: '#ffffff',
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '32px',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <div style={{
              width: '4px',
              height: '24px',
              backgroundColor: '#06b6d4',
              borderRadius: '2px'
            }}></div>
            <h2 style={{ margin: 0, fontSize: '20px', color: '#0f172a', fontWeight: 600 }}>
              System Alerts & Notifications
            </h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {data.alerts.map((alert: any, idx: number) => (
              <AlertBox key={idx} {...alert} />
            ))}
          </div>
        </div>

        {/* Risk Assessment */}
        <div style={{
          backgroundColor: '#ffffff',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <div style={{
              width: '4px',
              height: '24px',
              backgroundColor: '#ec4899',
              borderRadius: '2px'
            }}></div>
            <h2 style={{ margin: 0, fontSize: '20px', color: '#0f172a', fontWeight: 600 }}>
              Risk Assessment
            </h2>
          </div>
          <RiskLevelPanel risk={data.riskAssessment} />
        </div>
      </div>
    </div>
  );
}

// ============================================
// SECTION CONTAINER - Reusable wrapper
// ============================================

function SectionContainer({ title, accentColor, children }: { title: string; accentColor: string; children: React.ReactNode }) {
  return (
    <div style={{
      backgroundColor: '#ffffff',
      padding: '24px',
      borderRadius: '12px',
      marginBottom: '32px',
      border: '1px solid #e2e8f0'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <div style={{
          width: '4px',
          height: '24px',
          backgroundColor: accentColor,
          borderRadius: '2px'
        }}></div>
        <h2 style={{ margin: 0, fontSize: '20px', color: '#0f172a', fontWeight: 600 }}>
          {title}
        </h2>
      </div>
      {children}
    </div>
  );
}

// ============================================
// CRY DETECTION COMPONENT
// Backend: POST /api/cry-detection with audio stream
// ============================================

function CryDetectionCard({ cry }: { cry: any }) {
  const statusConfig: any = {
    normal: { color: '#10b981', bg: '#f0fdf4', icon: '🔇' },
    abnormal: { color: '#f59e0b', bg: '#fffbeb', icon: '🔔' },
    distress: { color: '#ef4444', bg: '#fef2f2', icon: '🚨' }
  };

  const config = statusConfig[cry.status];

  return (
    <div style={{
      backgroundColor: '#fafafa',
      borderRadius: '10px',
      padding: '24px',
      border: '2px solid #e2e8f0',
      borderLeftWidth: '5px',
      borderLeftColor: config.color
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '24px' }}>{config.icon}</span>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>Cry Detection</h3>
        </div>
        <div style={{
          backgroundColor: config.bg,
          padding: '6px 12px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 700,
          color: config.color
        }}>
          {cry.status.toUpperCase()}
        </div>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>Current Status</p>
        <p style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', margin: 0 }}>{cry.cryType}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
        <MetricBox label="Intensity" value={`${cry.intensity}`} unit="%" color={cry.intensity > 70 ? '#ef4444' : '#64748b'} />
        <MetricBox label="Duration" value={`${cry.duration}`} unit="sec" color="#64748b" />
      </div>

      <div style={{ backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
        <p style={{ fontSize: '12px', color: '#64748b', margin: 0 }}>
          <strong style={{ color: '#0f172a' }}>Last Detection:</strong> {cry.lastDetected}
        </p>
        <p style={{ fontSize: '12px', color: '#10b981', margin: 0, marginTop: '4px' }}>
          ✓ {cry.confidence}% Confidence
        </p>
      </div>
    </div>
  );
}

// ============================================
// SLEEP POSITION MONITORING
// Backend: POST /api/sleep-position with video frame
// ============================================

function SleepPositionCard({ sleep }: { sleep: any }) {
  const statusConfig: any = {
    safe: { color: '#10b981', bg: '#f0fdf4', icon: '✓' },
    warning: { color: '#f59e0b', bg: '#fffbeb', icon: '⚠' },
    unsafe: { color: '#ef4444', bg: '#fef2f2', icon: '✗' }
  };

  const config = statusConfig[sleep.status];

  return (
    <div style={{
      backgroundColor: '#fafafa',
      borderRadius: '10px',
      padding: '24px',
      border: '2px solid #e2e8f0',
      borderLeftWidth: '5px',
      borderLeftColor: config.color
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Brain size={24} color={config.color} />
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>Sleep Position</h3>
        </div>
        <div style={{
          backgroundColor: config.bg,
          padding: '6px 12px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 700,
          color: config.color
        }}>
          {config.icon} {sleep.status.toUpperCase()}
        </div>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>Current Position</p>
        <p style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', margin: 0 }}>{sleep.position}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
        <MetricBox label="Time in Position" value={`${sleep.timeInPosition}`} unit="min" color="#64748b" />
        <MetricBox label="Risk Level" value={sleep.riskLevel} unit="" color={config.color} />
      </div>

      <div style={{ backgroundColor: config.bg, padding: '10px', borderRadius: '8px', marginBottom: '12px' }}>
        <p style={{ fontSize: '12px', color: config.color, margin: 0, fontWeight: 500 }}>
          💡 {sleep.recommendations}
        </p>
      </div>

      <div style={{ backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
        <p style={{ fontSize: '11px', color: '#64748b', margin: 0, marginBottom: '6px' }}>
          <strong>Position History:</strong>
        </p>
        {sleep.positionHistory.slice(0, 3).map((h: any, idx: number) => (
          <div key={idx} style={{ fontSize: '11px', color: '#64748b', marginBottom: '2px' }}>
            {h.time} - {h.position}
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================
// BREATHING PATTERN ANALYSIS
// Backend: POST /api/breathing with video/sensor data
// ============================================

function BreathingAnalysisCard({ breathing }: { breathing: any }) {
  const statusConfig: any = {
    normal: { color: '#10b981', bg: '#f0fdf4' },
    concerning: { color: '#f59e0b', bg: '#fffbeb' },
    critical: { color: '#ef4444', bg: '#fef2f2' }
  };

  const config = statusConfig[breathing.status];

  return (
    <div style={{
      backgroundColor: '#fafafa',
      borderRadius: '10px',
      padding: '24px',
      border: '2px solid #e2e8f0',
      borderLeftWidth: '5px',
      borderLeftColor: config.color
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Activity size={24} color={config.color} />
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>Breathing Analysis</h3>
        </div>
        <div style={{
          backgroundColor: config.bg,
          padding: '6px 12px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 700,
          color: config.color
        }}>
          {breathing.status.toUpperCase()}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        <div>
          <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>Breathing Rate</p>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
            <p style={{ fontSize: '32px', fontWeight: 700, color: '#0f172a', margin: 0 }}>{breathing.rate}</p>
            <p style={{ fontSize: '14px', color: '#64748b' }}>bpm</p>
          </div>
        </div>
        <div>
          <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>O₂ Saturation</p>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
            <p style={{ fontSize: '32px', fontWeight: 700, color: '#10b981', margin: 0 }}>{breathing.oxygenLevel}</p>
            <p style={{ fontSize: '14px', color: '#64748b' }}>%</p>
          </div>
        </div>
      </div>

      <div style={{ backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '12px' }}>
        <p style={{ fontSize: '12px', color: '#64748b', margin: 0 }}>
          <strong style={{ color: '#0f172a' }}>Pattern:</strong> {breathing.pattern}
        </p>
        <p style={{ fontSize: '12px', color: '#64748b', margin: 0, marginTop: '4px' }}>
          <strong style={{ color: '#0f172a' }}>Trend:</strong> {breathing.trend}
        </p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#64748b' }}>
        <span>Irregularities: <strong style={{ color: config.color }}>{breathing.irregularities}</strong></span>
        <span>Confidence: <strong style={{ color: '#10b981' }}>{breathing.confidence}%</strong></span>
      </div>
    </div>
  );
}

// ============================================
// FACE & DISTRESS DETECTION
// Backend: POST /api/face-analysis with video frame
// ============================================

function FaceAnalysisCard({ face }: { face: any }) {
  const distressConfig: any = {
    none: { color: '#10b981', bg: '#f0fdf4', label: 'No Distress' },
    mild: { color: '#3b82f6', bg: '#eff6ff', label: 'Mild Fussiness' },
    moderate: { color: '#f59e0b', bg: '#fffbeb', label: 'Moderate Distress' },
    severe: { color: '#ef4444', bg: '#fef2f2', label: 'Severe Distress' }
  };

  const config = distressConfig[face.distressLevel];

  return (
    <div style={{
      backgroundColor: '#fafafa',
      borderRadius: '10px',
      padding: '24px',
      border: '2px solid #e2e8f0',
      borderLeftWidth: '5px',
      borderLeftColor: config.color
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '24px' }}>👁️</span>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>Face & Distress</h3>
        </div>
        <div style={{
          backgroundColor: config.bg,
          padding: '6px 12px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 700,
          color: config.color
        }}>
          {config.label}
        </div>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>Emotional State</p>
        <p style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', margin: 0, textTransform: 'capitalize' }}>
          {face.emotionalState}
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '10px',
        marginBottom: '16px'
      }}>
        <div style={{ backgroundColor: '#ffffff', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
          <p style={{ fontSize: '11px', color: '#64748b', margin: 0 }}>Face</p>
          <p style={{ fontSize: '16px', fontWeight: 700, color: face.faceDetected ? '#10b981' : '#ef4444', margin: 0 }}>
            {face.faceDetected ? '✓' : '✗'}
          </p>
        </div>
        <div style={{ backgroundColor: '#ffffff', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
          <p style={{ fontSize: '11px', color: '#64748b', margin: 0 }}>Eyes</p>
          <p style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            {face.eyesOpen ? 'Open' : 'Closed'}
          </p>
        </div>
        <div style={{ backgroundColor: '#ffffff', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
          <p style={{ fontSize: '11px', color: '#64748b', margin: 0 }}>Mouth</p>
          <p style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            {face.mouthOpen ? 'Open' : 'Closed'}
          </p>
        </div>
      </div>

      <div style={{ backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
        <p style={{ fontSize: '12px', color: '#64748b', margin: 0 }}>
          <strong style={{ color: '#0f172a' }}>Movement:</strong> {face.facialMovement}
        </p>
        <p style={{ fontSize: '12px', color: '#10b981', margin: 0, marginTop: '4px' }}>
          ✓ {face.confidence}% Confidence
        </p>
      </div>
    </div>
  );
}

// ============================================
// CAMERA MONITOR COMPONENT
// Handles getUserMedia and sends frames to backend
// ============================================

function CameraMonitor({ motionData }: { motionData: any }) {
  const videoRef = react.useRef<HTMLVideoElement>(null);
  const canvasRef = react.useRef<HTMLCanvasElement>(null);
  const [mediaStream, setMediaStream] = react.useState<MediaStream | null>(null);
  const [error, setError] = react.useState<string>("");
  const alarmAudio = react.useRef<HTMLAudioElement | null>(null);

  // Audio Alarm Logic
  react.useEffect(() => {
    if (!alarmAudio.current) {
      alarmAudio.current = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
      alarmAudio.current.loop = true;
    }

    if (motionData && motionData.status === 'UNSAFE') {
      alarmAudio.current.play().catch(e => console.log("Audio play failed", e));
    } else {
      if (alarmAudio.current) {
        alarmAudio.current.pause();
        alarmAudio.current.currentTime = 0;
      }
    }
  }, [motionData]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      setMediaStream(stream);
      setError("");
    } catch (err: any) {
      console.error("Camera Error:", err);
      setError(`Camera Error: ${err.name} - ${err.message}. Ensure you are on localhost or HTTPS.`);
    }
  };

  // Attach stream to video element when it becomes available
  react.useEffect(() => {
    if (videoRef.current && mediaStream) {
      videoRef.current.srcObject = mediaStream;
    }
  }, [mediaStream]);

  // Frame processing loop
  react.useEffect(() => {
    let interval: any;

    if (mediaStream) {
      interval = setInterval(() => {
        if (videoRef.current && canvasRef.current) {
          const video = videoRef.current;
          const canvas = canvasRef.current;

          // Check if video is ready and has valid dimensions
          if (video.readyState === video.HAVE_ENOUGH_DATA && video.videoWidth > 0) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
              try {
                // Draw video frame to canvas
                ctx.drawImage(video, 0, 0, 640, 480);

                // Convert to blob and send
                canvas.toBlob((blob) => {
                  if (blob) {
                    const formData = new FormData();
                    formData.append('file', blob, 'frame.jpg');

                    fetch(`${API_BASE_URL}/api/process_frame`, {
                      method: 'POST',
                      body: formData
                    }).catch(e => console.error("Upload error", e));
                  } else {
                    console.warn("Failed to create blob from canvas");
                  }
                }, 'image/jpeg', 0.5);
              } catch (err) {
                console.error("Frame capture error:", err);
              }
            } else {
              console.warn("Canvas context not available");
            }
          } else {
            // Video not ready
            if (video.readyState < video.HAVE_ENOUGH_DATA) {
              console.warn("Video not ready yet, readyState:", video.readyState);
            }
          }
        } else {
          console.warn("Video or canvas ref not available");
        }
      }, 500); // Send 2 frames per second
    }

    return () => clearInterval(interval);
  }, [mediaStream]);

  return (
    <div style={{
      width: '100%',
      height: '480px',
      backgroundColor: '#000',
      borderRadius: '12px',
      overflow: 'hidden',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      position: 'relative',
      border: motionData?.status === 'UNSAFE' ? '4px solid #ef4444' : 'none',
      boxShadow: motionData?.status === 'UNSAFE' ? '0 0 20px #ef4444' : 'none',
      transition: 'all 0.3s ease'
    }}>
      {!mediaStream ? (
        <div style={{ textAlign: 'center', color: 'white' }}>
          {error ? (
            <div style={{ marginBottom: '16px', color: '#ef4444' }}>
              <AlertCircle size={48} style={{ display: 'block', margin: '0 auto 8px' }} />
              <p>{error}</p>
            </div>
          ) : (
            <div style={{ marginBottom: '16px' }}>
              <p style={{ fontSize: '18px', marginBottom: '16px' }}>Camera access is required for monitoring</p>
            </div>
          )}
          <button
            onClick={startCamera}
            style={{
              padding: '12px 24px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              margin: '0 auto'
            }}
          >
            🎥 Enable Camera Access
          </button>
        </div>
      ) : (
        <>
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              willChange: 'transform',
              transform: 'translateZ(0)'
            }}
          />
          <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }} />

          {/* Live Indicator */}
          <div style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            backgroundColor: 'rgba(239, 68, 68, 0.9)',
            color: 'white',
            padding: '4px 12px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              backgroundColor: 'white',
              borderRadius: '50%'
            }}></div>
            LIVE MONITORING
          </div>

          {/* UNSAFE ALERT OVERLAY */}
          {motionData && motionData.status === 'UNSAFE' && (
            <div style={{
              position: 'absolute',
              top: 0, left: 0, right: 0, bottom: 0,
              backgroundColor: 'rgba(239, 68, 68, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'pulse 1s infinite'
            }}>
              <div style={{
                backgroundColor: '#ef4444',
                color: 'white',
                padding: '20px 40px',
                borderRadius: '12px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '12px',
                boxShadow: '0 10px 25px rgba(0,0,0,0.5)'
              }}>
                <AlertCircle size={48} />
                <span style={{ fontSize: '24px', fontWeight: 800 }}>CRITICAL ALERT</span>
                <span style={{ fontSize: '16px' }}>No movement detected!</span>
              </div>
            </div>
          )}

          {/* Real-time Motion & Status Overlay */}
          {motionData && (
            <div style={{
              position: 'absolute',
              bottom: '16px',
              left: '16px',
              right: '16px',
              display: 'flex',
              gap: '12px',
              justifyContent: 'center'
            }}>
              <div style={{
                backgroundColor: 'rgba(0,0,0,0.7)',
                backdropFilter: 'blur(4px)',
                padding: '8px 16px',
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                border: motionData.status === 'UNSAFE' ? '2px solid #ef4444' : '1px solid rgba(255,255,255,0.2)'
              }}>
                <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600 }}>STATUS</span>
                <span style={{
                  color: motionData.status === 'SAFE' ? '#4ade80' : motionData.status === 'UNSAFE' ? '#ef4444' : '#fbbf24',
                  fontWeight: 700
                }}>
                  {motionData.status}
                </span>
              </div>

              <div style={{
                backgroundColor: 'rgba(0,0,0,0.7)',
                backdropFilter: 'blur(4px)',
                padding: '8px 16px',
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                border: '1px solid rgba(255,255,255,0.2)'
              }}>
                <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600 }}>MOTION</span>
                <span style={{ color: 'white', fontWeight: 700 }}>{motionData.motion}</span>
              </div>

              <div style={{
                backgroundColor: 'rgba(0,0,0,0.7)',
                backdropFilter: 'blur(4px)',
                padding: '8px 16px',
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                border: '1px solid rgba(255,255,255,0.2)'
              }}>
                <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600 }}>STILL TIME</span>
                <span style={{ color: 'white', fontWeight: 700 }}>{motionData.stillTime}s</span>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}


// ============================================
// MOTION MONITORING COMPONENT
// Connects to your OpenCV Python backend
// ============================================

function MotionMonitoringCard({ motion }: { motion: any }) {
  const statusConfig: any = {
    SAFE: {
      color: '#10b981',
      bg: '#f0fdf4',
      label: '✓ SAFE',
      message: 'Baby is moving normally'
    },
    MONITOR: {
      color: '#f59e0b',
      bg: '#fffbeb',
      label: '⚠ MONITOR',
      message: 'Reduced movement detected'
    },
    ALERT: {
      color: '#ef4444',
      bg: '#fef2f2',
      label: '🚨 ALERT',
      message: 'Baby has been still too long!'
    },
    UNSAFE: {
      color: '#ef4444',
      bg: '#fef2f2',
      label: '🚨 CRITICAL',
      message: 'No movement detected for extended period!'
    }
  };

  const config = statusConfig[motion?.status] || statusConfig.SAFE;

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '16px',
      padding: '32px',
      boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
      borderLeft: `6px solid ${config.color}`,
      animation: motion.alertActive ? 'pulse 1s infinite' : 'none'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#0f172a' }}>
          Motion Detection System
        </h2>
        <div style={{
          backgroundColor: config.bg,
          padding: '12px 24px',
          borderRadius: '24px',
          border: `3px solid ${config.color}`,
          fontSize: '16px',
          fontWeight: 700,
          color: config.color
        }}>
          {config.label}
        </div>
      </div>

      <div style={{
        backgroundColor: config.bg,
        padding: '16px',
        borderRadius: '12px',
        marginBottom: '24px',
        borderLeft: `4px solid ${config.color}`
      }}>
        <p style={{ fontSize: '15px', color: '#0f172a', fontWeight: 500 }}>
          {config.message}
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '20px'
      }}>
        <MetricBox
          label="Still Time"
          value={`${motion.stillTime}`}
          unit="sec"
          color={motion.status === 'ALERT' ? '#ef4444' : '#64748b'}
        />
        <MetricBox
          label="Motion Level"
          value={motion.motion.toFixed(2)}
          unit=""
          color="#3b82f6"
        />
        <MetricBox
          label="Confidence"
          value={`${motion.confidence}`}
          unit="%"
          color="#10b981"
        />
        <MetricBox
          label="Alert Status"
          value={motion.alertActive ? "ON" : "OFF"}
          unit=""
          color={motion.alertActive ? '#ef4444' : '#10b981'}
        />
      </div>

      {motion.alertActive && (
        <div style={{
          marginTop: '20px',
          padding: '16px',
          backgroundColor: '#fef2f2',
          borderRadius: '8px',
          border: '2px solid #ef4444',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <p style={{ fontSize: '14px', fontWeight: 600, color: '#ef4444' }}>
            🚨 IMMEDIATE ATTENTION REQUIRED
          </p>
          <button style={{
            padding: '8px 16px',
            backgroundColor: '#ef4444',
            color: '#ffffff',
            border: 'none',
            borderRadius: '6px',
            fontWeight: 600,
            cursor: 'pointer'
          }}>
            Acknowledge Alert
          </button>
        </div>
      )}
    </div>
  );
}

function MetricBox({ label, value, unit, color }: any) {
  return (
    <div style={{
      backgroundColor: '#f8fafc',
      padding: '16px',
      borderRadius: '10px',
      textAlign: 'center'
    }}>
      <p style={{ fontSize: '12px', color: '#64748b', marginBottom: '8px' }}>{label}</p>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: '4px' }}>
        <p style={{ fontSize: '28px', fontWeight: 700, color }}>{value}</p>
        {unit && <p style={{ fontSize: '14px', color: '#94a3b8' }}>{unit}</p>}
      </div>
    </div>
  );
}

// ============================================
// COMPONENTS - All data-driven, ML-ready
// ============================================

function PatientInfoPanel({ patient }: { patient: any }) {
  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '28px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      border: '1px solid #e2e8f0',
      borderLeft: '6px solid #3b82f6'
    }}>
      <h2 style={{ fontSize: '18px', marginBottom: '20px', color: '#0f172a', fontWeight: 600 }}>
        Patient Information
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px' }}>
        <InfoItem label="Infant ID" value={patient.id} />
        <InfoItem label="Age" value={patient.age} />
        <InfoItem label="Weight" value={patient.weight} />
        <InfoItem label="Gestational Age" value={patient.gestationalAge} />
        <InfoItem label="Admission Date" value={patient.admissionDate} />
        <InfoItem label="Current Status" value={patient.status} valueColor="#10b981" />
      </div>
    </div>
  );
}

function InfoItem({ label, value, valueColor }: { label: string; value: string; valueColor?: string }) {
  return (
    <div style={{
      backgroundColor: '#f8fafc',
      padding: '16px',
      borderRadius: '8px',
      border: '1px solid #e2e8f0'
    }}>
      <p style={{ fontSize: '11px', color: '#64748b', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>{label}</p>
      <p style={{ fontSize: '17px', fontWeight: 600, color: valueColor || '#0f172a', margin: 0 }}>{value}</p>
    </div>
  );
}

function StatusCard({ title, value, confidence, note, status }: any) {
  const icons: any = {
    'Cry Pattern': <Activity size={24} color="#06b6d4" />,
    'Sleep Position': <Brain size={24} color="#8b5cf6" />,
    'Body Temperature': <Thermometer size={24} color="#ec4899" />
  };

  const borderColors = { normal: '#10b981', warning: '#f59e0b', alert: '#ef4444' };

  return (
    <div style={{
      backgroundColor: '#fafafa',
      borderRadius: '10px',
      padding: '24px',
      border: '2px solid #e2e8f0',
      borderLeftWidth: '5px',
      borderLeftColor: borderColors[status],
      transition: 'all 0.2s',
      cursor: 'pointer'
    }}
      onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
      onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {icons[title] || <Activity size={24} />}
          <p style={{ fontSize: '14px', color: '#64748b', fontWeight: 600, margin: 0 }}>{title}</p>
        </div>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: borderColors[status]
        }}></div>
      </div>
      <p style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px', color: '#0f172a', margin: 0 }}>{value}</p>
      <div style={{
        backgroundColor: '#ffffff',
        padding: '6px 12px',
        borderRadius: '6px',
        marginTop: '12px',
        marginBottom: '8px',
        display: 'inline-block'
      }}>
        <p style={{ fontSize: '12px', color: '#10b981', fontWeight: 600, margin: 0 }}>
          ✓ {confidence}% Confidence
        </p>
      </div>
      <p style={{ fontSize: '12px', color: '#64748b', margin: 0, marginTop: '8px' }}>{note}</p>
    </div>
  );
}

function VitalSignCard({ title, value, unit, normalRange, status }: any) {
  const borderColors = { normal: '#10b981', warning: '#f59e0b', alert: '#ef4444' };
  const bgColors = { normal: '#f0fdf4', warning: '#fffbeb', alert: '#fef2f2' };

  return (
    <div style={{
      backgroundColor: '#fafafa',
      borderRadius: '10px',
      padding: '24px',
      border: '2px solid #e2e8f0',
      borderLeftWidth: '5px',
      borderLeftColor: borderColors[status],
      transition: 'all 0.2s'
    }}
      onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
      onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Activity size={24} color={borderColors[status]} />
          <p style={{ fontSize: '14px', color: '#64748b', fontWeight: 600, margin: 0 }}>{title}</p>
        </div>
        <div style={{
          backgroundColor: bgColors[status],
          padding: '4px 10px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 700,
          color: borderColors[status],
          textTransform: 'uppercase'
        }}>
          {status}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '12px' }}>
        <p style={{ fontSize: '40px', fontWeight: 700, color: '#0f172a', margin: 0, lineHeight: 1 }}>{value}</p>
        <p style={{ fontSize: '18px', color: '#94a3b8', fontWeight: 500 }}>{unit}</p>
      </div>
      <div style={{
        backgroundColor: '#ffffff',
        padding: '8px 12px',
        borderRadius: '6px',
        border: '1px solid #e2e8f0'
      }}>
        <p style={{ fontSize: '12px', color: '#64748b', margin: 0 }}>
          <strong style={{ color: '#0f172a' }}>Normal Range:</strong> {normalRange} {unit}
        </p>
      </div>
      <p style={{ fontSize: '11px', color: '#94a3b8', margin: 0, marginTop: '12px' }}>
        📍 Last updated: 1 min ago
      </p>
    </div>
  );
}

function EventTimeline({ events }: { events: any[] }) {
  const eventIcons: any = {
    measurement: '📊',
    alert: '⚠️',
    activity: '🔄',
    care: '🍼'
  };

  const eventColors: any = {
    measurement: '#3b82f6',
    alert: '#ef4444',
    activity: '#10b981',
    care: '#8b5cf6'
  };

  return (
    <div style={{
      maxHeight: '360px',
      overflowY: 'auto',
      paddingRight: '8px'
    }}>
      {events.map((event, idx) => (
        <div key={idx} style={{
          display: 'flex',
          gap: '14px',
          paddingBottom: '20px',
          marginBottom: '20px',
          borderBottom: idx < events.length - 1 ? '1px solid #f1f5f9' : 'none',
          position: 'relative'
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            backgroundColor: '#f8fafc',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            border: '2px solid #e2e8f0',
            flexShrink: 0
          }}>
            {eventIcons[event.type]}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <p style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a', margin: 0 }}>
                {event.description}
              </p>
              <p style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>{event.time}</p>
            </div>
            <div style={{
              display: 'inline-block',
              backgroundColor: '#f8fafc',
              padding: '3px 10px',
              borderRadius: '12px',
              fontSize: '11px',
              color: eventColors[event.type],
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.3px'
            }}>
              {event.type}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function TrainingChart({ data }: { data: any[] }) {
  return (
    <div style={{ height: '360px' }}>
      <div style={{
        backgroundColor: '#f8fafc',
        padding: '12px 16px',
        borderRadius: '8px',
        marginBottom: '16px',
        border: '1px solid #e2e8f0'
      }}>
        <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>
          <strong style={{ color: '#0f172a' }}>Model Status:</strong> Training complete •
          <strong style={{ color: '#10b981', marginLeft: '8px' }}>✓ 88% Accuracy achieved</strong>
        </p>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="epoch"
            label={{ value: 'Training Epoch', position: 'insideBottom', offset: -5, style: { fontSize: 12, fill: '#64748b' } }}
            tick={{ fontSize: 12, fill: '#64748b' }}
          />
          <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '12px'
            }}
          />
          <Line
            type="monotone"
            dataKey="accuracy"
            stroke="#10b981"
            strokeWidth={3}
            name="Accuracy (%)"
            dot={{ fill: '#10b981', r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="loss"
            stroke="#ef4444"
            strokeWidth={3}
            name="Loss"
            dot={{ fill: '#ef4444', r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function AlertBox({ type, message, timestamp }: any) {
  const styles: any = {
    normal: { bg: '#f0fdf4', border: '#10b981', icon: <Activity size={20} color="#10b981" />, label: 'NORMAL' },
    warning: { bg: '#fffbeb', border: '#f59e0b', icon: <AlertCircle size={20} color="#f59e0b" />, label: 'WARNING' },
    alert: { bg: '#fef2f2', border: '#ef4444', icon: <AlertCircle size={20} color="#ef4444" />, label: 'ALERT' },
    critical: { bg: '#fef2f2', border: '#ef4444', icon: <AlertCircle size={20} color="#ef4444" />, label: 'CRITICAL' },
    info: { bg: '#eff6ff', border: '#3b82f6', icon: <Activity size={20} color="#3b82f6" />, label: 'INFO' }
  };

  const style = styles[type] || styles.info;

  return (
    <div style={{
      backgroundColor: style.bg,
      borderLeft: `5px solid ${style.border}`,
      padding: '16px 20px',
      borderRadius: '8px',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '12px'
    }}>
      {style.icon}
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span style={{ fontSize: '11px', fontWeight: 600, color: style.border }}>{style.label}</span>
          <span style={{ fontSize: '11px', color: '#64748b' }}>{timestamp}</span>
        </div>
        <span style={{ fontSize: '14px', color: '#0f172a' }}>{message}</span>
      </div>
    </div>
  );
}

function RiskLevelPanel({ risk }: { risk: any }) {
  const riskColors: any = {
    low: { bg: '#f0fdf4', border: '#10b981', text: '#10b981', label: 'LOW RISK' },
    medium: { bg: '#fffbeb', border: '#f59e0b', text: '#f59e0b', label: 'MEDIUM RISK' },
    high: { bg: '#fef2f2', border: '#ef4444', text: '#ef4444', label: 'HIGH RISK' }
  };

  const riskStyle = riskColors[risk.overall];

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '14px',
      padding: '24px',
      boxShadow: '0 6px 16px rgba(0,0,0,0.06)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ fontSize: '16px', color: '#0f172a', fontWeight: 600 }}>Overall Risk Level</h3>
        <div style={{
          backgroundColor: riskStyle.bg,
          padding: '8px 16px',
          borderRadius: '20px',
          border: `2px solid ${riskStyle.border}`
        }}>
          <p style={{ fontSize: '14px', fontWeight: 600, color: riskStyle.text }}>● {riskStyle.label}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        {risk.categories.map((cat: any, idx: number) => (
          <RiskItem key={idx} category={cat.name} level={cat.level} color={cat.color} />
        ))}
      </div>

      <div style={{ marginTop: '20px', padding: '12px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
        <p style={{ fontSize: '13px', color: '#475569' }}>
          <strong>AI Confidence:</strong> {risk.confidence}% • Based on continuous monitoring of vital signs and behavioral patterns
        </p>
      </div>
    </div>
  );
}

function RiskItem({ category, level, color }: any) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: color }}></div>
      <div>
        <p style={{ fontSize: '13px', color: '#64748b' }}>{category}</p>
        <p style={{ fontSize: '14px', fontWeight: 600, color }}>{level}</p>
      </div>
    </div>
  );
}

function SectionTitle({ title }: { title: string }) {
  return (
    <h2 style={{ margin: '0 0 16px', fontSize: '18px', color: '#0f172a', fontWeight: 600 }}>
      {title}
    </h2>
  );
}

export default App;