import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import * as react from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Brain, Thermometer, AlertCircle } from 'lucide-react';
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001';
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
            status: "SAFE", // SAFE / MONITOR / ALERT
            stillTime: 6,
            motion: 1.24,
            confidence: 82,
            alertActive: false
        },
        // Cry Detection AI (new)
        cryDetection: {
            status: "normal", // normal / abnormal / distress
            cryType: "None detected", // hunger, pain, discomfort, none
            intensity: 0, // 0-100
            duration: 0, // seconds
            confidence: 95,
            lastDetected: "No cry in last 15 min",
            audioWaveform: [0.2, 0.5, 0.8, 1.2, 0.9, 0.4, 0.1] // For visualization
        },
        // Sleep Position Monitoring (new)
        sleepPosition: {
            position: "Back", // Back, Side, Stomach, Unknown
            status: "safe", // safe / warning / unsafe
            riskLevel: "low", // low / medium / high
            timeInPosition: 45, // minutes
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
            rate: 42, // breaths per minute
            pattern: "Regular", // Regular, Irregular, Apnea detected
            status: "normal", // normal / concerning / critical
            oxygenLevel: 98, // SpO2 percentage
            confidence: 89,
            irregularities: 0, // count in last hour
            trend: "stable" // improving / stable / declining
        },
        // Face & Distress Detection (new)
        faceAnalysis: {
            faceDetected: true,
            distressLevel: "none", // none / mild / moderate / severe
            emotionalState: "calm", // calm, fussy, crying, sleeping
            facialMovement: "minimal", // minimal, moderate, active
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
                { name: "Respiratory", level: "Low", color: "#059669" },
                { name: "Cardiac", level: "Low", color: "#059669" },
                { name: "Neurological", level: "Low", color: "#059669" },
                { name: "Thermal", level: "Low", color: "#059669" }
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
    const [data, setData] = react.useState(null);
    const [lastUpdated, setLastUpdated] = react.useState(new Date().toLocaleTimeString());
    // Load data on mount
    react.useEffect(() => {
        const loadData = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/dashboard`);
                if (!response.ok)
                    throw new Error('Failed to fetch');
                const dashboardData = await response.json();
                setData(dashboardData);
            }
            catch (error) {
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
        return (_jsx("div", {
            style: {
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                fontSize: '18px',
                color: '#64748b'
            }, children: "Loading dashboard data..."
        }));
    }
    return (_jsxs("div", {
        style: { minHeight: '100vh', backgroundColor: '#f1f5f9', fontFamily: 'system-ui, sans-serif' }, children: [_jsxs("div", {
            style: {
                backgroundColor: '#ffffff',
                padding: '24px 48px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                borderBottom: '3px solid #0284c7'
            }, children: [_jsxs("div", {
                style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' }, children: [_jsx("div", {
                    children: _jsxs("div", {
                        style: { display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }, children: [_jsx("div", {
                            style: {
                                width: '48px',
                                height: '48px',
                                backgroundColor: '#0284c7',
                                borderRadius: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '24px',
                                color: '#ffffff',
                                fontWeight: 700
                            }, children: "\uD83D\uDC76"
                        }), _jsxs("div", { children: [_jsx("h1", { style: { fontSize: '28px', margin: 0, color: '#1e293b', fontWeight: 700, letterSpacing: '-0.5px' }, children: "Neonatal AI Monitoring System" }), _jsx("p", { style: { color: '#64748b', fontSize: '14px', margin: 0, marginTop: '2px' }, children: "Real-time AI-assisted neonatal care & monitoring" })] })]
                    })
                }), _jsxs("div", {
                    style: { display: 'flex', gap: '12px', alignItems: 'center' }, children: [_jsx("div", {
                        style: {
                            backgroundColor: '#ecfdf5',
                            padding: '8px 16px',
                            borderRadius: '8px',
                            border: '1px solid #6ee7b7'
                        }, children: _jsx("p", { style: { fontSize: '12px', color: '#047857', margin: 0 }, children: "\uD83D\uDFE2 System Active" })
                    }), _jsx("button", {
                        style: {
                            padding: '10px 20px',
                            backgroundColor: '#0284c7',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '8px',
                            fontSize: '14px',
                            fontWeight: 600,
                            cursor: 'pointer',
                            boxShadow: '0 2px 4px rgba(2,132,199,0.3)'
                        }, children: "\uD83D\uDCCA Export Report"
                    }), _jsx("button", {
                        style: {
                            padding: '10px 20px',
                            backgroundColor: '#e11d48',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '8px',
                            fontSize: '14px',
                            fontWeight: 600,
                            cursor: 'pointer',
                            boxShadow: '0 2px 4px rgba(225,29,72,0.3)'
                        }, children: "\uD83D\uDEA8 Emergency Contact"
                    })]
                })]
            }), _jsxs("div", {
                style: {
                    marginTop: '16px',
                    paddingTop: '16px',
                    borderTop: '1px solid #e2e8f0',
                    display: 'flex',
                    gap: '32px',
                    fontSize: '13px'
                }, children: [_jsxs("span", { style: { color: '#64748b' }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Last Updated:" }), " ", lastUpdated] }), _jsxs("span", { style: { color: '#64748b' }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Monitoring Since:" }), " Jan 21, 2026 08:30 AM"] }), _jsxs("span", { style: { color: '#64748b' }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Session Duration:" }), " 5h 22m"] })]
            })]
        }), _jsxs("div", {
            style: { padding: '32px 48px', maxWidth: '1600px', margin: '0 auto' }, children: [_jsxs("div", {
                style: {
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '24px',
                    marginBottom: '32px'
                }, children: [_jsx(SectionContainer, { title: "Live Baby Monitor", accentColor: "#0284c7", children: _jsx(CameraMonitor, { motionData: data.motionMonitoring }) }), _jsx(SectionContainer, { title: "Real-Time Motion Monitoring", accentColor: "#0284c7", children: _jsx(MotionMonitoringCard, { motion: data.motionMonitoring }) })]
            }), _jsx(PatientInfoPanel, { patient: data.patient }), _jsx("div", { style: { height: '32px' } }), _jsx(SectionContainer, { title: "AI Detection Systems", accentColor: "#0369a1", children: _jsxs("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }, children: [_jsx(CryDetectionCard, { cry: data.cryDetection }), _jsx(SleepPositionCard, { sleep: data.sleepPosition }), _jsx(BreathingAnalysisCard, { breathing: data.breathingAnalysis }), _jsx(FaceAnalysisCard, { face: data.faceAnalysis })] }) }), _jsxs("div", {
                style: {
                    backgroundColor: '#ffffff',
                    padding: '24px',
                    borderRadius: '12px',
                    marginBottom: '32px',
                    border: '1px solid #e2e8f0'
                }, children: [_jsxs("div", {
                    style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }, children: [_jsx("div", {
                        style: {
                            width: '4px',
                            height: '24px',
                            backgroundColor: '#0369a1',
                            borderRadius: '2px'
                        }
                    }), _jsx("h2", { style: { margin: 0, fontSize: '20px', color: '#1e293b', fontWeight: 600 }, children: "AI-Powered Health Monitoring" })]
                }), _jsx("div", {
                    style: {
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                        gap: '20px'
                    }, children: data.aiStatus.map((item, idx) => (_jsx(StatusCard, { ...item }, idx)))
                })]
            }), _jsxs("div", {
                style: {
                    backgroundColor: '#ffffff',
                    padding: '24px',
                    borderRadius: '12px',
                    marginBottom: '32px',
                    border: '1px solid #e2e8f0'
                }, children: [_jsxs("div", {
                    style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }, children: [_jsx("div", {
                        style: {
                            width: '4px',
                            height: '24px',
                            backgroundColor: '#e11d48',
                            borderRadius: '2px'
                        }
                    }), _jsx("h2", { style: { margin: 0, fontSize: '20px', color: '#1e293b', fontWeight: 600 }, children: "Vital Signs Monitoring" })]
                }), _jsx("div", {
                    style: {
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                        gap: '20px'
                    }, children: data.vitals.map((vital, idx) => (_jsx(VitalSignCard, { ...vital }, idx)))
                })]
            }), _jsxs("div", {
                style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }, children: [_jsxs("div", {
                    style: {
                        backgroundColor: '#ffffff',
                        padding: '24px',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0'
                    }, children: [_jsxs("div", {
                        style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }, children: [_jsx("div", {
                            style: {
                                width: '4px',
                                height: '24px',
                                backgroundColor: '#059669',
                                borderRadius: '2px'
                            }
                        }), _jsx("h2", { style: { margin: 0, fontSize: '20px', color: '#1e293b', fontWeight: 600 }, children: "Recent Events" })]
                    }), _jsx(EventTimeline, { events: data.events })]
                }), _jsxs("div", {
                    style: {
                        backgroundColor: '#ffffff',
                        padding: '24px',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0'
                    }, children: [_jsxs("div", {
                        style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }, children: [_jsx("div", {
                            style: {
                                width: '4px',
                                height: '24px',
                                backgroundColor: '#d97706',
                                borderRadius: '2px'
                            }
                        }), _jsx("h2", { style: { margin: 0, fontSize: '20px', color: '#1e293b', fontWeight: 600 }, children: "AI Model Performance" })]
                    }), _jsx(TrainingChart, { data: data.trainingData })]
                })]
            }), _jsxs("div", {
                style: {
                    backgroundColor: '#ffffff',
                    padding: '24px',
                    borderRadius: '12px',
                    marginBottom: '32px',
                    border: '1px solid #e2e8f0'
                }, children: [_jsxs("div", {
                    style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }, children: [_jsx("div", {
                        style: {
                            width: '4px',
                            height: '24px',
                            backgroundColor: '#0891b2',
                            borderRadius: '2px'
                        }
                    }), _jsx("h2", { style: { margin: 0, fontSize: '20px', color: '#1e293b', fontWeight: 600 }, children: "System Alerts & Notifications" })]
                }), _jsx("div", { style: { display: 'flex', flexDirection: 'column', gap: '12px' }, children: data.alerts.map((alert, idx) => (_jsx(AlertBox, { ...alert }, idx))) })]
            }), _jsxs("div", {
                style: {
                    backgroundColor: '#ffffff',
                    padding: '24px',
                    borderRadius: '12px',
                    border: '1px solid #e2e8f0'
                }, children: [_jsxs("div", {
                    style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }, children: [_jsx("div", {
                        style: {
                            width: '4px',
                            height: '24px',
                            backgroundColor: '#4f46e5',
                            borderRadius: '2px'
                        }
                    }), _jsx("h2", { style: { margin: 0, fontSize: '20px', color: '#1e293b', fontWeight: 600 }, children: "Risk Assessment" })]
                }), _jsx(RiskLevelPanel, { risk: data.riskAssessment })]
            })]
        })]
    }));
}
// ============================================
// SECTION CONTAINER - Reusable wrapper
// ============================================
function SectionContainer({ title, accentColor, children }) {
    return (_jsxs("div", {
        style: {
            backgroundColor: '#ffffff',
            padding: '24px',
            borderRadius: '12px',
            marginBottom: '32px',
            border: '1px solid #e2e8f0'
        }, children: [_jsxs("div", {
            style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }, children: [_jsx("div", {
                style: {
                    width: '4px',
                    height: '24px',
                    backgroundColor: accentColor,
                    borderRadius: '2px'
                }
            }), _jsx("h2", { style: { margin: 0, fontSize: '20px', color: '#1e293b', fontWeight: 600 }, children: title })]
        }), children]
    }));
}
// ============================================
// CRY DETECTION COMPONENT
// Backend: POST /api/cry-detection with audio stream
// ============================================
function CryDetectionCard({ cry }) {
    const statusConfig = {
        normal: { color: '#059669', bg: '#ecfdf5', icon: '🔇' },
        abnormal: { color: '#d97706', bg: '#fffbeb', icon: '🔔' },
        distress: { color: '#e11d48', bg: '#fff1f2', icon: '🚨' }
    };
    const config = statusConfig[cry.status];
    return (_jsxs("div", {
        style: {
            backgroundColor: '#fafafa',
            borderRadius: '10px',
            padding: '24px',
            border: '2px solid #e2e8f0',
            borderLeftWidth: '5px',
            borderLeftColor: config.color
        }, children: [_jsxs("div", {
            style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '10px' }, children: [_jsx("span", { style: { fontSize: '24px' }, children: config.icon }), _jsx("h3", { style: { margin: 0, fontSize: '16px', fontWeight: 600 }, children: "Cry Detection" })] }), _jsx("div", {
                style: {
                    backgroundColor: config.bg,
                    padding: '6px 12px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: config.color
                }, children: cry.status.toUpperCase()
            })]
        }), _jsxs("div", { style: { marginBottom: '16px' }, children: [_jsx("p", { style: { fontSize: '13px', color: '#64748b', marginBottom: '4px' }, children: "Current Status" }), _jsx("p", { style: { fontSize: '24px', fontWeight: 700, color: '#1e293b', margin: 0 }, children: cry.cryType })] }), _jsxs("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }, children: [_jsx(MetricBox, { label: "Intensity", value: `${cry.intensity}`, unit: "%", color: cry.intensity > 70 ? '#e11d48' : '#64748b' }), _jsx(MetricBox, { label: "Duration", value: `${cry.duration}`, unit: "sec", color: "#64748b" })] }), _jsxs("div", { style: { backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }, children: [_jsxs("p", { style: { fontSize: '12px', color: '#64748b', margin: 0 }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Last Detection:" }), " ", cry.lastDetected] }), _jsxs("p", { style: { fontSize: '12px', color: '#059669', margin: 0, marginTop: '4px' }, children: ["\u2713 ", cry.confidence, "% Confidence"] })] })]
    }));
}
// ============================================
// SLEEP POSITION MONITORING
// Backend: POST /api/sleep-position with video frame
// ============================================
function SleepPositionCard({ sleep }) {
    const statusConfig = {
        safe: { color: '#059669', bg: '#ecfdf5', icon: '✓' },
        warning: { color: '#d97706', bg: '#fffbeb', icon: '⚠' },
        unsafe: { color: '#e11d48', bg: '#fff1f2', icon: '✗' }
    };
    const config = statusConfig[sleep.status];
    return (_jsxs("div", {
        style: {
            backgroundColor: '#fafafa',
            borderRadius: '10px',
            padding: '24px',
            border: '2px solid #e2e8f0',
            borderLeftWidth: '5px',
            borderLeftColor: config.color
        }, children: [_jsxs("div", {
            style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '10px' }, children: [_jsx(Brain, { size: 24, color: config.color }), _jsx("h3", { style: { margin: 0, fontSize: '16px', fontWeight: 600 }, children: "Sleep Position" })] }), _jsxs("div", {
                style: {
                    backgroundColor: config.bg,
                    padding: '6px 12px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: config.color
                }, children: [config.icon, " ", sleep.status.toUpperCase()]
            })]
        }), _jsxs("div", { style: { marginBottom: '16px' }, children: [_jsx("p", { style: { fontSize: '13px', color: '#64748b', marginBottom: '4px' }, children: "Current Position" }), _jsx("p", { style: { fontSize: '24px', fontWeight: 700, color: '#1e293b', margin: 0 }, children: sleep.position })] }), _jsxs("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }, children: [_jsx(MetricBox, { label: "Time in Position", value: `${sleep.timeInPosition}`, unit: "min", color: "#64748b" }), _jsx(MetricBox, { label: "Risk Level", value: sleep.riskLevel, unit: "", color: config.color })] }), _jsx("div", { style: { backgroundColor: config.bg, padding: '10px', borderRadius: '8px', marginBottom: '12px' }, children: _jsxs("p", { style: { fontSize: '12px', color: config.color, margin: 0, fontWeight: 500 }, children: ["\uD83D\uDCA1 ", sleep.recommendations] }) }), _jsxs("div", { style: { backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }, children: [_jsx("p", { style: { fontSize: '11px', color: '#64748b', margin: 0, marginBottom: '6px' }, children: _jsx("strong", { children: "Position History:" }) }), sleep.positionHistory.slice(0, 3).map((h, idx) => (_jsxs("div", { style: { fontSize: '11px', color: '#64748b', marginBottom: '2px' }, children: [h.time, " - ", h.position] }, idx)))] })]
    }));
}
// ============================================
// BREATHING PATTERN ANALYSIS
// Backend: POST /api/breathing with video/sensor data
// ============================================
function BreathingAnalysisCard({ breathing }) {
    const statusConfig = {
        normal: { color: '#059669', bg: '#ecfdf5' },
        concerning: { color: '#d97706', bg: '#fffbeb' },
        critical: { color: '#e11d48', bg: '#fff1f2' }
    };
    const config = statusConfig[breathing.status];
    return (_jsxs("div", {
        style: {
            backgroundColor: '#fafafa',
            borderRadius: '10px',
            padding: '24px',
            border: '2px solid #e2e8f0',
            borderLeftWidth: '5px',
            borderLeftColor: config.color
        }, children: [_jsxs("div", {
            style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '10px' }, children: [_jsx(Activity, { size: 24, color: config.color }), _jsx("h3", { style: { margin: 0, fontSize: '16px', fontWeight: 600 }, children: "Breathing Analysis" })] }), _jsx("div", {
                style: {
                    backgroundColor: config.bg,
                    padding: '6px 12px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: config.color
                }, children: breathing.status.toUpperCase()
            })]
        }), _jsxs("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }, children: [_jsxs("div", { children: [_jsx("p", { style: { fontSize: '13px', color: '#64748b', marginBottom: '4px' }, children: "Breathing Rate" }), _jsxs("div", { style: { display: 'flex', alignItems: 'baseline', gap: '4px' }, children: [_jsx("p", { style: { fontSize: '32px', fontWeight: 700, color: '#1e293b', margin: 0 }, children: breathing.rate }), _jsx("p", { style: { fontSize: '14px', color: '#64748b' }, children: "bpm" })] })] }), _jsxs("div", { children: [_jsx("p", { style: { fontSize: '13px', color: '#64748b', marginBottom: '4px' }, children: "O\u2082 Saturation" }), _jsxs("div", { style: { display: 'flex', alignItems: 'baseline', gap: '4px' }, children: [_jsx("p", { style: { fontSize: '32px', fontWeight: 700, color: '#059669', margin: 0 }, children: breathing.oxygenLevel }), _jsx("p", { style: { fontSize: '14px', color: '#64748b' }, children: "%" })] })] })] }), _jsxs("div", { style: { backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '12px' }, children: [_jsxs("p", { style: { fontSize: '12px', color: '#64748b', margin: 0 }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Pattern:" }), " ", breathing.pattern] }), _jsxs("p", { style: { fontSize: '12px', color: '#64748b', margin: 0, marginTop: '4px' }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Trend:" }), " ", breathing.trend] })] }), _jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#64748b' }, children: [_jsxs("span", { children: ["Irregularities: ", _jsx("strong", { style: { color: config.color }, children: breathing.irregularities })] }), _jsxs("span", { children: ["Confidence: ", _jsxs("strong", { style: { color: '#059669' }, children: [breathing.confidence, "%"] })] })] })]
    }));
}
// ============================================
// FACE & DISTRESS DETECTION
// Backend: POST /api/face-analysis with video frame
// ============================================
function FaceAnalysisCard({ face }) {
    const distressConfig = {
        none: { color: '#059669', bg: '#ecfdf5', label: 'No Distress' },
        mild: { color: '#0284c7', bg: '#eff6ff', label: 'Mild Fussiness' },
        moderate: { color: '#d97706', bg: '#fffbeb', label: 'Moderate Distress' },
        severe: { color: '#e11d48', bg: '#fff1f2', label: 'Severe Distress' }
    };
    const config = distressConfig[face.distressLevel];
    return (_jsxs("div", {
        style: {
            backgroundColor: '#fafafa',
            borderRadius: '10px',
            padding: '24px',
            border: '2px solid #e2e8f0',
            borderLeftWidth: '5px',
            borderLeftColor: config.color
        }, children: [_jsxs("div", {
            style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '10px' }, children: [_jsx("span", { style: { fontSize: '24px' }, children: "\uD83D\uDC41\uFE0F" }), _jsx("h3", { style: { margin: 0, fontSize: '16px', fontWeight: 600 }, children: "Face & Distress" })] }), _jsx("div", {
                style: {
                    backgroundColor: config.bg,
                    padding: '6px 12px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: config.color
                }, children: config.label
            })]
        }), _jsxs("div", { style: { marginBottom: '16px' }, children: [_jsx("p", { style: { fontSize: '13px', color: '#64748b', marginBottom: '4px' }, children: "Emotional State" }), _jsx("p", { style: { fontSize: '24px', fontWeight: 700, color: '#1e293b', margin: 0, textTransform: 'capitalize' }, children: face.emotionalState })] }), _jsxs("div", {
            style: {
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '10px',
                marginBottom: '16px'
            }, children: [_jsxs("div", { style: { backgroundColor: '#ffffff', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }, children: [_jsx("p", { style: { fontSize: '11px', color: '#64748b', margin: 0 }, children: "Face" }), _jsx("p", { style: { fontSize: '16px', fontWeight: 700, color: face.faceDetected ? '#059669' : '#e11d48', margin: 0 }, children: face.faceDetected ? '✓' : '✗' })] }), _jsxs("div", { style: { backgroundColor: '#ffffff', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }, children: [_jsx("p", { style: { fontSize: '11px', color: '#64748b', margin: 0 }, children: "Eyes" }), _jsx("p", { style: { fontSize: '16px', fontWeight: 700, color: '#1e293b', margin: 0 }, children: face.eyesOpen ? 'Open' : 'Closed' })] }), _jsxs("div", { style: { backgroundColor: '#ffffff', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }, children: [_jsx("p", { style: { fontSize: '11px', color: '#64748b', margin: 0 }, children: "Mouth" }), _jsx("p", { style: { fontSize: '16px', fontWeight: 700, color: '#1e293b', margin: 0 }, children: face.mouthOpen ? 'Open' : 'Closed' })] })]
        }), _jsxs("div", { style: { backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }, children: [_jsxs("p", { style: { fontSize: '12px', color: '#64748b', margin: 0 }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Movement:" }), " ", face.facialMovement] }), _jsxs("p", { style: { fontSize: '12px', color: '#059669', margin: 0, marginTop: '4px' }, children: ["\u2713 ", face.confidence, "% Confidence"] })] })]
    }));
}
// ============================================
// CAMERA MONITOR COMPONENT
// Handles getUserMedia and sends frames to backend
// ============================================
function CameraMonitor({ motionData }) {
    const videoRef = react.useRef(null);
    const canvasRef = react.useRef(null);
    const [mediaStream, setMediaStream] = react.useState(null);
    const [error, setError] = react.useState("");
    const alarmAudio = react.useRef(null);
    // Audio Alarm Logic
    react.useEffect(() => {
        if (!alarmAudio.current) {
            alarmAudio.current = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
            alarmAudio.current.loop = true;
        }
        if (motionData && motionData.status === 'UNSAFE') {
            alarmAudio.current.play().catch(e => console.log("Audio play failed", e));
        }
        else {
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
        }
        catch (err) {
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
        let interval;
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
                                    }
                                    else {
                                        console.warn("Failed to create blob from canvas");
                                    }
                                }, 'image/jpeg', 0.5);
                            }
                            catch (err) {
                                console.error("Frame capture error:", err);
                            }
                        }
                        else {
                            console.warn("Canvas context not available");
                        }
                    }
                    else {
                        // Video not ready
                        if (video.readyState < video.HAVE_ENOUGH_DATA) {
                            console.warn("Video not ready yet, readyState:", video.readyState);
                        }
                    }
                }
                else {
                    console.warn("Video or canvas ref not available");
                }
            }, 500); // Send 2 frames per second
        }
        return () => clearInterval(interval);
    }, [mediaStream]);
    return (_jsx("div", {
        style: {
            width: '100%',
            height: '480px',
            backgroundColor: '#000',
            borderRadius: '12px',
            overflow: 'hidden',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            position: 'relative',
            border: motionData?.status === 'UNSAFE' ? '4px solid #e11d48' : 'none',
            boxShadow: motionData?.status === 'UNSAFE' ? '0 0 20px #e11d48' : 'none',
            transition: 'all 0.3s ease'
        }, children: !mediaStream ? (_jsxs("div", {
            style: { textAlign: 'center', color: 'white' }, children: [error ? (_jsxs("div", { style: { marginBottom: '16px', color: '#e11d48' }, children: [_jsx(AlertCircle, { size: 48, style: { display: 'block', margin: '0 auto 8px' } }), _jsx("p", { children: error })] })) : (_jsx("div", { style: { marginBottom: '16px' }, children: _jsx("p", { style: { fontSize: '18px', marginBottom: '16px' }, children: "Camera access is required for monitoring" }) })), _jsx("button", {
                onClick: startCamera, style: {
                    padding: '12px 24px',
                    backgroundColor: '#0284c7',
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
                }, children: "\uD83C\uDFA5 Enable Camera Access"
            })]
        })) : (_jsxs(_Fragment, {
            children: [_jsx("video", {
                ref: videoRef, autoPlay: true, muted: true, playsInline: true, style: {
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    willChange: 'transform',
                    transform: 'translateZ(0)'
                }
            }), _jsx("canvas", { ref: canvasRef, width: "640", height: "480", style: { display: 'none' } }), _jsxs("div", {
                style: {
                    position: 'absolute',
                    top: '16px',
                    left: '16px',
                    backgroundColor: 'rgba(225, 29, 72, 0.9)',
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                }, children: [_jsx("div", {
                    style: {
                        width: '8px',
                        height: '8px',
                        backgroundColor: 'white',
                        borderRadius: '50%'
                    }
                }), "LIVE MONITORING"]
            }), motionData && motionData.status === 'UNSAFE' && (_jsx("div", {
                style: {
                    position: 'absolute',
                    top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(225, 29, 72, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    animation: 'pulse 1s infinite'
                }, children: _jsxs("div", {
                    style: {
                        backgroundColor: '#e11d48',
                        color: 'white',
                        padding: '20px 40px',
                        borderRadius: '12px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '12px',
                        boxShadow: '0 10px 25px rgba(0,0,0,0.5)'
                    }, children: [_jsx(AlertCircle, { size: 48 }), _jsx("span", { style: { fontSize: '24px', fontWeight: 800 }, children: "CRITICAL ALERT" }), _jsx("span", { style: { fontSize: '16px' }, children: "No movement detected!" })]
                })
            })), motionData && (_jsxs("div", {
                style: {
                    position: 'absolute',
                    bottom: '16px',
                    left: '16px',
                    right: '16px',
                    display: 'flex',
                    gap: '12px',
                    justifyContent: 'center'
                }, children: [_jsxs("div", {
                    style: {
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        backdropFilter: 'blur(4px)',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        border: motionData.status === 'UNSAFE' ? '2px solid #e11d48' : '1px solid rgba(255,255,255,0.2)'
                    }, children: [_jsx("span", { style: { fontSize: '11px', color: '#94a3b8', fontWeight: 600 }, children: "STATUS" }), _jsx("span", {
                        style: {
                            color: motionData.status === 'SAFE' ? '#4ade80' : motionData.status === 'UNSAFE' ? '#e11d48' : '#fbbf24',
                            fontWeight: 700
                        }, children: motionData.status
                    })]
                }), _jsxs("div", {
                    style: {
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        backdropFilter: 'blur(4px)',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        border: '1px solid rgba(255,255,255,0.2)'
                    }, children: [_jsx("span", { style: { fontSize: '11px', color: '#94a3b8', fontWeight: 600 }, children: "MOTION" }), _jsx("span", { style: { color: 'white', fontWeight: 700 }, children: motionData.motion })]
                }), _jsxs("div", {
                    style: {
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        backdropFilter: 'blur(4px)',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        border: '1px solid rgba(255,255,255,0.2)'
                    }, children: [_jsx("span", { style: { fontSize: '11px', color: '#94a3b8', fontWeight: 600 }, children: "STILL TIME" }), _jsxs("span", { style: { color: 'white', fontWeight: 700 }, children: [motionData.stillTime, "s"] })]
                })]
            }))]
        }))
    }));
}
// ============================================
// MOTION MONITORING COMPONENT
// Connects to your OpenCV Python backend
// ============================================
function MotionMonitoringCard({ motion }) {
    const statusConfig = {
        SAFE: {
            color: '#059669',
            bg: '#ecfdf5',
            label: '✓ SAFE',
            message: 'Baby is moving normally'
        },
        MONITOR: {
            color: '#d97706',
            bg: '#fffbeb',
            label: '⚠ MONITOR',
            message: 'Reduced movement detected'
        },
        ALERT: {
            color: '#e11d48',
            bg: '#fff1f2',
            label: '🚨 ALERT',
            message: 'Baby has been still too long!'
        },
        UNSAFE: {
            color: '#e11d48',
            bg: '#fff1f2',
            label: '🚨 CRITICAL',
            message: 'No movement detected for extended period!'
        }
    };
    const config = statusConfig[motion?.status] || statusConfig.SAFE;
    return (_jsxs("div", {
        style: {
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            padding: '32px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
            borderLeft: `6px solid ${config.color}`,
            animation: motion.alertActive ? 'pulse 1s infinite' : 'none'
        }, children: [_jsxs("div", {
            style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }, children: [_jsx("h2", { style: { fontSize: '20px', fontWeight: 600, color: '#1e293b' }, children: "Motion Detection System" }), _jsx("div", {
                style: {
                    backgroundColor: config.bg,
                    padding: '12px 24px',
                    borderRadius: '24px',
                    border: `3px solid ${config.color}`,
                    fontSize: '16px',
                    fontWeight: 700,
                    color: config.color
                }, children: config.label
            })]
        }), _jsx("div", {
            style: {
                backgroundColor: config.bg,
                padding: '16px',
                borderRadius: '12px',
                marginBottom: '24px',
                borderLeft: `4px solid ${config.color}`
            }, children: _jsx("p", { style: { fontSize: '15px', color: '#1e293b', fontWeight: 500 }, children: config.message })
        }), _jsxs("div", {
            style: {
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '20px'
            }, children: [_jsx(MetricBox, { label: "Still Time", value: `${motion.stillTime}`, unit: "sec", color: motion.status === 'ALERT' ? '#e11d48' : '#64748b' }), _jsx(MetricBox, { label: "Motion Level", value: motion.motion.toFixed(2), unit: "", color: "#0284c7" }), _jsx(MetricBox, { label: "Confidence", value: `${motion.confidence}`, unit: "%", color: "#059669" }), _jsx(MetricBox, { label: "Alert Status", value: motion.alertActive ? "ON" : "OFF", unit: "", color: motion.alertActive ? '#e11d48' : '#059669' })]
        }), motion.alertActive && (_jsxs("div", {
            style: {
                marginTop: '20px',
                padding: '16px',
                backgroundColor: '#fff1f2',
                borderRadius: '8px',
                border: '2px solid #e11d48',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }, children: [_jsx("p", { style: { fontSize: '14px', fontWeight: 600, color: '#e11d48' }, children: "\uD83D\uDEA8 IMMEDIATE ATTENTION REQUIRED" }), _jsx("button", {
                style: {
                    padding: '8px 16px',
                    backgroundColor: '#e11d48',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '6px',
                    fontWeight: 600,
                    cursor: 'pointer'
                }, children: "Acknowledge Alert"
            })]
        }))]
    }));
}
function MetricBox({ label, value, unit, color }) {
    return (_jsxs("div", {
        style: {
            backgroundColor: '#f1f5f9',
            padding: '16px',
            borderRadius: '10px',
            textAlign: 'center'
        }, children: [_jsx("p", { style: { fontSize: '12px', color: '#64748b', marginBottom: '8px' }, children: label }), _jsxs("div", { style: { display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: '4px' }, children: [_jsx("p", { style: { fontSize: '28px', fontWeight: 700, color }, children: value }), unit && _jsx("p", { style: { fontSize: '14px', color: '#94a3b8' }, children: unit })] })]
    }));
}
// ============================================
// COMPONENTS - All data-driven, ML-ready
// ============================================
function PatientInfoPanel({ patient }) {
    return (_jsxs("div", {
        style: {
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            padding: '28px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0',
            borderLeft: '6px solid #0284c7'
        }, children: [_jsx("h2", { style: { fontSize: '18px', marginBottom: '20px', color: '#1e293b', fontWeight: 600 }, children: "Patient Information" }), _jsxs("div", { style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px' }, children: [_jsx(InfoItem, { label: "Infant ID", value: patient.id }), _jsx(InfoItem, { label: "Age", value: patient.age }), _jsx(InfoItem, { label: "Weight", value: patient.weight }), _jsx(InfoItem, { label: "Gestational Age", value: patient.gestationalAge }), _jsx(InfoItem, { label: "Admission Date", value: patient.admissionDate }), _jsx(InfoItem, { label: "Current Status", value: patient.status, valueColor: "#059669" })] })]
    }));
}
function InfoItem({ label, value, valueColor }) {
    return (_jsxs("div", {
        style: {
            backgroundColor: '#f1f5f9',
            padding: '16px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0'
        }, children: [_jsx("p", { style: { fontSize: '11px', color: '#64748b', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }, children: label }), _jsx("p", { style: { fontSize: '17px', fontWeight: 600, color: valueColor || '#1e293b', margin: 0 }, children: value })]
    }));
}
function StatusCard({ title, value, confidence, note, status }) {
    const icons = {
        'Cry Pattern': _jsx(Activity, { size: 24, color: "#0891b2" }),
        'Sleep Position': _jsx(Brain, { size: 24, color: "#0369a1" }),
        'Body Temperature': _jsx(Thermometer, { size: 24, color: "#4f46e5" })
    };
    const borderColors = { normal: '#059669', warning: '#d97706', alert: '#e11d48' };
    return (_jsxs("div", {
        style: {
            backgroundColor: '#fafafa',
            borderRadius: '10px',
            padding: '24px',
            border: '2px solid #e2e8f0',
            borderLeftWidth: '5px',
            borderLeftColor: borderColors[status],
            transition: 'all 0.2s',
            cursor: 'pointer'
        }, onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-2px)', onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)', children: [_jsxs("div", {
            style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '10px' }, children: [icons[title] || _jsx(Activity, { size: 24 }), _jsx("p", { style: { fontSize: '14px', color: '#64748b', fontWeight: 600, margin: 0 }, children: title })] }), _jsx("div", {
                style: {
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: borderColors[status]
                }
            })]
        }), _jsx("p", { style: { fontSize: '32px', fontWeight: 700, marginBottom: '8px', color: '#1e293b', margin: 0 }, children: value }), _jsx("div", {
            style: {
                backgroundColor: '#ffffff',
                padding: '6px 12px',
                borderRadius: '6px',
                marginTop: '12px',
                marginBottom: '8px',
                display: 'inline-block'
            }, children: _jsxs("p", { style: { fontSize: '12px', color: '#059669', fontWeight: 600, margin: 0 }, children: ["\u2713 ", confidence, "% Confidence"] })
        }), _jsx("p", { style: { fontSize: '12px', color: '#64748b', margin: 0, marginTop: '8px' }, children: note })]
    }));
}
function VitalSignCard({ title, value, unit, normalRange, status }) {
    const borderColors = { normal: '#059669', warning: '#d97706', alert: '#e11d48' };
    const bgColors = { normal: '#ecfdf5', warning: '#fffbeb', alert: '#fff1f2' };
    return (_jsxs("div", {
        style: {
            backgroundColor: '#fafafa',
            borderRadius: '10px',
            padding: '24px',
            border: '2px solid #e2e8f0',
            borderLeftWidth: '5px',
            borderLeftColor: borderColors[status],
            transition: 'all 0.2s'
        }, onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-2px)', onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)', children: [_jsxs("div", {
            style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '10px' }, children: [_jsx(Activity, { size: 24, color: borderColors[status] }), _jsx("p", { style: { fontSize: '14px', color: '#64748b', fontWeight: 600, margin: 0 }, children: title })] }), _jsx("div", {
                style: {
                    backgroundColor: bgColors[status],
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: borderColors[status],
                    textTransform: 'uppercase'
                }, children: status
            })]
        }), _jsxs("div", { style: { display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '12px' }, children: [_jsx("p", { style: { fontSize: '40px', fontWeight: 700, color: '#1e293b', margin: 0, lineHeight: 1 }, children: value }), _jsx("p", { style: { fontSize: '18px', color: '#94a3b8', fontWeight: 500 }, children: unit })] }), _jsx("div", {
            style: {
                backgroundColor: '#ffffff',
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #e2e8f0'
            }, children: _jsxs("p", { style: { fontSize: '12px', color: '#64748b', margin: 0 }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Normal Range:" }), " ", normalRange, " ", unit] })
        }), _jsx("p", { style: { fontSize: '11px', color: '#94a3b8', margin: 0, marginTop: '12px' }, children: "\uD83D\uDCCD Last updated: 1 min ago" })]
    }));
}
function EventTimeline({ events }) {
    const eventIcons = {
        measurement: '📊',
        alert: '⚠️',
        activity: '🔄',
        care: '🍼'
    };
    const eventColors = {
        measurement: '#0284c7',
        alert: '#e11d48',
        activity: '#059669',
        care: '#0369a1'
    };
    return (_jsx("div", {
        style: {
            maxHeight: '360px',
            overflowY: 'auto',
            paddingRight: '8px'
        }, children: events.map((event, idx) => (_jsxs("div", {
            style: {
                display: 'flex',
                gap: '14px',
                paddingBottom: '20px',
                marginBottom: '20px',
                borderBottom: idx < events.length - 1 ? '1px solid #f1f5f9' : 'none',
                position: 'relative'
            }, children: [_jsx("div", {
                style: {
                    width: '36px',
                    height: '36px',
                    backgroundColor: '#f1f5f9',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '18px',
                    border: '2px solid #e2e8f0',
                    flexShrink: 0
                }, children: eventIcons[event.type]
            }), _jsxs("div", {
                style: { flex: 1 }, children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }, children: [_jsx("p", { style: { fontSize: '14px', fontWeight: 600, color: '#1e293b', margin: 0 }, children: event.description }), _jsx("p", { style: { fontSize: '12px', color: '#94a3b8', fontWeight: 600 }, children: event.time })] }), _jsx("div", {
                    style: {
                        display: 'inline-block',
                        backgroundColor: '#f1f5f9',
                        padding: '3px 10px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        color: eventColors[event.type],
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        letterSpacing: '0.3px'
                    }, children: event.type
                })]
            })]
        }, idx)))
    }));
}
function TrainingChart({ data }) {
    return (_jsxs("div", {
        style: { height: '360px' }, children: [_jsx("div", {
            style: {
                backgroundColor: '#f1f5f9',
                padding: '12px 16px',
                borderRadius: '8px',
                marginBottom: '16px',
                border: '1px solid #e2e8f0'
            }, children: _jsxs("p", { style: { fontSize: '13px', color: '#64748b', margin: 0 }, children: [_jsx("strong", { style: { color: '#1e293b' }, children: "Model Status:" }), " Training complete \u2022", _jsx("strong", { style: { color: '#059669', marginLeft: '8px' }, children: "\u2713 88% Accuracy achieved" })] })
        }), _jsx(ResponsiveContainer, {
            width: "100%", height: 280, children: _jsxs(LineChart, {
                data: data, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "#e2e8f0" }), _jsx(XAxis, { dataKey: "epoch", label: { value: 'Training Epoch', position: 'insideBottom', offset: -5, style: { fontSize: 12, fill: '#64748b' } }, tick: { fontSize: 12, fill: '#64748b' } }), _jsx(YAxis, { tick: { fontSize: 12, fill: '#64748b' } }), _jsx(Tooltip, {
                    contentStyle: {
                        backgroundColor: '#ffffff',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        fontSize: '12px'
                    }
                }), _jsx(Line, { type: "monotone", dataKey: "accuracy", stroke: "#059669", strokeWidth: 3, name: "Accuracy (%)", dot: { fill: '#059669', r: 4 } }), _jsx(Line, { type: "monotone", dataKey: "loss", stroke: "#e11d48", strokeWidth: 3, name: "Loss", dot: { fill: '#e11d48', r: 4 } })]
            })
        })]
    }));
}
function AlertBox({ type, message, timestamp }) {
    const styles = {
        normal: { bg: '#ecfdf5', border: '#059669', icon: _jsx(Activity, { size: 20, color: "#059669" }), label: 'NORMAL' },
        warning: { bg: '#fffbeb', border: '#d97706', icon: _jsx(AlertCircle, { size: 20, color: "#d97706" }), label: 'WARNING' },
        alert: { bg: '#fff1f2', border: '#e11d48', icon: _jsx(AlertCircle, { size: 20, color: "#e11d48" }), label: 'ALERT' },
        critical: { bg: '#fff1f2', border: '#e11d48', icon: _jsx(AlertCircle, { size: 20, color: "#e11d48" }), label: 'CRITICAL' },
        info: { bg: '#eff6ff', border: '#0284c7', icon: _jsx(Activity, { size: 20, color: "#0284c7" }), label: 'INFO' }
    };
    const style = styles[type] || styles.info;
    return (_jsxs("div", {
        style: {
            backgroundColor: style.bg,
            borderLeft: `5px solid ${style.border}`,
            padding: '16px 20px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
        }, children: [style.icon, _jsxs("div", { style: { flex: 1 }, children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }, children: [_jsx("span", { style: { fontSize: '11px', fontWeight: 600, color: style.border }, children: style.label }), _jsx("span", { style: { fontSize: '11px', color: '#64748b' }, children: timestamp })] }), _jsx("span", { style: { fontSize: '14px', color: '#1e293b' }, children: message })] })]
    }));
}
function RiskLevelPanel({ risk }) {
    const riskColors = {
        low: { bg: '#ecfdf5', border: '#059669', text: '#059669', label: 'LOW RISK' },
        medium: { bg: '#fffbeb', border: '#d97706', text: '#d97706', label: 'MEDIUM RISK' },
        high: { bg: '#fff1f2', border: '#e11d48', text: '#e11d48', label: 'HIGH RISK' }
    };
    const riskStyle = riskColors[risk.overall];
    return (_jsxs("div", {
        style: {
            backgroundColor: '#ffffff',
            borderRadius: '14px',
            padding: '24px',
            boxShadow: '0 6px 16px rgba(0,0,0,0.06)'
        }, children: [_jsxs("div", {
            style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }, children: [_jsx("h3", { style: { fontSize: '16px', color: '#1e293b', fontWeight: 600 }, children: "Overall Risk Level" }), _jsx("div", {
                style: {
                    backgroundColor: riskStyle.bg,
                    padding: '8px 16px',
                    borderRadius: '20px',
                    border: `2px solid ${riskStyle.border}`
                }, children: _jsxs("p", { style: { fontSize: '14px', fontWeight: 600, color: riskStyle.text }, children: ["\u25CF ", riskStyle.label] })
            })]
        }), _jsx("div", { style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }, children: risk.categories.map((cat, idx) => (_jsx(RiskItem, { category: cat.name, level: cat.level, color: cat.color }, idx))) }), _jsx("div", { style: { marginTop: '20px', padding: '12px', backgroundColor: '#f1f5f9', borderRadius: '8px' }, children: _jsxs("p", { style: { fontSize: '13px', color: '#475569' }, children: [_jsx("strong", { children: "AI Confidence:" }), " ", risk.confidence, "% \u2022 Based on continuous monitoring of vital signs and behavioral patterns"] }) })]
    }));
}
function RiskItem({ category, level, color }) {
    return (_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '12px' }, children: [_jsx("div", { style: { width: '8px', height: '8px', borderRadius: '50%', backgroundColor: color } }), _jsxs("div", { children: [_jsx("p", { style: { fontSize: '13px', color: '#64748b' }, children: category }), _jsx("p", { style: { fontSize: '14px', fontWeight: 600, color }, children: level })] })] }));
}
function SectionTitle({ title }) {
    return (_jsx("h2", { style: { margin: '0 0 16px', fontSize: '18px', color: '#1e293b', fontWeight: 600 }, children: title }));
}
export default App;
