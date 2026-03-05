import { useState, useEffect, useRef } from 'react';
import {
  User, Monitor, Shield, Activity, Wind,
  AlertCircle, Camera, Volume2, VolumeX,
  Fan, RotateCcw, Clock, Wifi, Search, Filter, Server, Settings, Power,
  ChevronRight, Calendar, Thermometer, Baby, FileText, Bell, LifeBuoy, LogOut, Home
} from 'lucide-react';
import {
  AreaChart, Area, ResponsiveContainer, YAxis, XAxis, CartesianGrid, Tooltip
} from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5001";

const generateDummyHistory = () =>
  Array.from({ length: 30 }, (_, i) => ({ time: i, breathing: 40, stillness: 0 }));

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [userRole, setUserRole] = useState<'doctor' | 'parent' | null>(null);
  const [data, setData] = useState<any>(null);
  const [history, setHistory] = useState<any[]>(generateDummyHistory());
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);

  const [isCameraEnabled, setIsCameraEnabled] = useState<boolean>(true);

  const [isCameraSimulated, setIsCameraSimulated] = useState<boolean>(false);
  // NEW: 3 Modules Navigation
  const [activeTab, setActiveTab] = useState<'dashboard' | 'logs' | 'system'>('dashboard');

  // Actuator Control State
  const [isFanOn, setIsFanOn] = useState<boolean>(false);
  const [isMuted, setIsMuted] = useState<boolean>(false);

  // Data Polling
  useEffect(() => {
    if (!isAuthenticated) return;
    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/dashboard`);
        if (!res.ok) throw new Error("Link Lost");
        const json = await res.json();
        setData(json);
        setIsOnline(true);

        setHistory(prev => {
          // Use 'motion' for the visual graph as it shows the real-time 'pattern'
          // much better than a static BPM number.
          const breathing = json.motionMonitoring?.motion || 0;
          const stillness = json.motionMonitoring?.stillTime || 0;
          const newEntry = { time: prev.length, breathing, stillness };
          return [...prev.slice(-44), newEntry];
        });
      } catch (err) {
        setIsOnline(false);
      }
    };
    const interval = setInterval(poll, 333);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  // Sync Camera Status to Backend
  useEffect(() => {
    if (!isAuthenticated) return;
    fetch(`${API_BASE_URL}/api/camera_status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: isCameraEnabled })
    }).catch(() => { });
  }, [isCameraEnabled, isAuthenticated]);

  // Buzzer Logic
  useEffect(() => {
    if (!isAuthenticated || isMuted) return;
    const isCrisis = data?.motionMonitoring?.status === 'UNSAFE' || data?.motionMonitoring?.stillTime >= 20;
    if (isCrisis) {
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      osc.type = 'sine'; osc.frequency.setValueAtTime(880, audioCtx.currentTime);
      const g = audioCtx.createGain(); g.gain.setValueAtTime(0.1, audioCtx.currentTime);
      osc.connect(g); g.connect(audioCtx.destination);
      osc.start(); osc.stop(audioCtx.currentTime + 0.2);
      setTimeout(() => audioCtx.close(), 500);
    }
  }, [data, isMuted]);

  const getRisk = () => {
    const s = data?.motionMonitoring?.status;
    const st = data?.motionMonitoring?.stillTime || 0;
    if (st >= 24 || s === 'UNSAFE') return { label: 'CRITICAL', color: 'red' };
    if (st >= 13) return { label: 'WARNING', color: 'orange' };
    return { label: 'NORMAL', color: 'green' };
  };

  const risk = getRisk();
  const mm = data?.motionMonitoring || {};
  const alerts = data?.alerts || [];
  const face = data?.faceAnalysis || {};

  const handleLogin = (role: 'doctor' | 'parent') => {
    setUserRole(role);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserRole(null);
  };

  if (!isAuthenticated) return <AuthFlow onLogin={handleLogin} />;

  return (
    <div className={`app-container ${risk.label === 'CRITICAL' ? 'critical-alert' : ''}`}>
      {userRole === 'doctor' ? (
        <DoctorView
          data={data}
          risk={risk}
          mm={mm}
          history={history}
          face={face}
          alerts={alerts}
          isOnline={isOnline}
          isCameraEnabled={isCameraEnabled}
          setIsCameraEnabled={setIsCameraEnabled}
          isCameraSimulated={isCameraSimulated}
          setIsCameraSimulated={setIsCameraSimulated}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isFanOn={isFanOn}
          setIsFanOn={setIsFanOn}
          isMuted={isMuted}
          setIsMuted={setIsMuted}
          onLogout={handleLogout}
        />
      ) : (
        <ParentView
          data={data}
          risk={risk}
          mm={mm}
          face={face}
          alerts={alerts}
          isOnline={isOnline}
          isCameraEnabled={isCameraEnabled}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

// --- PRINTABLE PATIENT REPORT FOR PDFs / PAPER ---
function PrintablePatientReport({ data, mm, face, lab, spo2, temp, alerts }: any) {
  if (!data?.patient) return null;
  return (
    <div className="print-only" style={{ padding: '20px', fontFamily: 'sans-serif', background: 'white', color: 'black' }}>
      <div style={{ borderBottom: '2px solid black', paddingBottom: '10px', marginBottom: '20px', textAlign: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 900, textTransform: 'uppercase' }}>NEOGUARD SURVIVAL ENGINE</h1>
        <h2 style={{ margin: '4px 0 0 0', fontSize: '18px', fontWeight: 600 }}>OFFICIAL CLINICAL PATIENT REPORT</h2>
        <p style={{ margin: '4px 0 0 0', fontSize: '12px' }}>Generated: {new Date().toLocaleString()}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
        <div>
          <h3 style={{ borderBottom: '1px solid black', paddingBottom: '5px', marginTop: 0, fontSize: '14px' }}>PATIENT DEMOGRAPHICS</h3>
          <table style={{ width: '100%', fontSize: '12px', border: 'none' }}>
            <tbody>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>ID:</strong></td><td style={{ border: 'none' }}>{data.patient.id}</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Age:</strong></td><td style={{ border: 'none' }}>{data.patient.age}</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Weight:</strong></td><td style={{ border: 'none' }}>{data.patient.weight}</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Gestational Age:</strong></td><td style={{ border: 'none' }}>{data.patient.gestationalAge}</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Ward:</strong></td><td style={{ border: 'none' }}>{data.patient.ward}</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Admission:</strong></td><td style={{ border: 'none' }}>{data.patient.admissionDate}</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <h3 style={{ borderBottom: '1px solid black', paddingBottom: '5px', marginTop: 0, fontSize: '14px' }}>CLINICAL STATUS SNAPSHOT</h3>
          <table style={{ width: '100%', fontSize: '12px', border: 'none' }}>
            <tbody>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Overall Risk (PHI):</strong></td><td style={{ border: 'none' }}>{data.riskAssessment?.phi || '--'} / 100</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Breathing Rate:</strong></td><td style={{ border: 'none' }}>{mm.breathingRate || '--'} BPM ({mm.breathingStatus})</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>SpO₂ Level:</strong></td><td style={{ border: 'none' }}>{spo2?.value}% ({spo2?.status})</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Temperature:</strong></td><td style={{ border: 'none' }}>{temp?.value}°C ({temp?.status})</td></tr>
              <tr><td style={{ border: 'none', padding: '2px 0' }}><strong>Skin / Cyanosis:</strong></td><td style={{ border: 'none' }}>Score {face.cyanosisScore} ({face.cyanosisStatus})</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ borderBottom: '1px solid black', paddingBottom: '5px', fontSize: '14px' }}>LABORATORY PANELS (Last Update: {lab?.lastUpdate})</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5' }}>
              <th style={{ border: '1px solid #ccc', padding: '6px' }}>Diagnostic Panel</th>
              <th style={{ border: '1px solid #ccc', padding: '6px' }}>Result Value</th>
              <th style={{ border: '1px solid #ccc', padding: '6px' }}>Physiological Status</th>
            </tr>
          </thead>
          <tbody>
            {(lab?.panels || []).map((p: any, i: number) => (
              <tr key={i}>
                <td style={{ border: '1px solid #ccc', padding: '6px' }}>{p.name}</td>
                <td style={{ border: '1px solid #ccc', padding: '6px' }}>{p.value} {p.unit}</td>
                <td style={{ border: '1px solid #ccc', padding: '6px', fontWeight: 'bold' }}>{p.status?.toUpperCase()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h3 style={{ borderBottom: '1px solid black', paddingBottom: '5px', fontSize: '14px' }}>RECENT CLINICAL HISTORY & EVENTS</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5' }}>
              <th style={{ border: '1px solid #ccc', padding: '6px' }}>Timestamp</th>
              <th style={{ border: '1px solid #ccc', padding: '6px' }}>Telemetry Source</th>
              <th style={{ border: '1px solid #ccc', padding: '6px' }}>Log Message</th>
              <th style={{ border: '1px solid #ccc', padding: '6px' }}>Severity Tag</th>
            </tr>
          </thead>
          <tbody>
            {alerts.slice(0, 20).map((a: any, i: number) => (
              <tr key={i}>
                <td style={{ border: '1px solid #ccc', padding: '6px' }}>{a.timestamp || '--:--:--'}</td>
                <td style={{ border: '1px solid #ccc', padding: '6px' }}>{a.source || 'Monitor'}</td>
                <td style={{ border: '1px solid #ccc', padding: '6px' }}>{a.message}</td>
                <td style={{ border: '1px solid #ccc', padding: '6px', fontWeight: 'bold' }}>{a.type?.toUpperCase()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '40px', paddingTop: '20px', borderTop: '1px dotted #ccc', display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#666' }}>
        <span>Authorized By: _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _</span>
        <span>NeoGuard AI Clinical Engine v2.0 - Page 1 of 1</span>
      </div>
    </div>
  );
}

// --- DOCTOR VIEW COMPONENT ---
function DoctorView({
  data, risk, mm, history, face, alerts, isOnline,
  isCameraEnabled, setIsCameraEnabled, isCameraSimulated, setIsCameraSimulated,
  activeTab, setActiveTab, isFanOn, setIsFanOn, isMuted, setIsMuted, onLogout
}: any) {
  const getVital = (title: string) => data?.vitals?.find((v: any) => v.title === title) || { value: 0, status: 'normal' };
  const spo2 = getVital('Oxygen Saturation');
  const temp = getVital('Body Temp');
  const lab = data?.labReports || { status: 'normal', lastUpdate: 'WAITING' };

  const handleGenerateReport = async () => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5001'}/api/generate_report`, { method: 'POST' });
      // Poll cycle is ~333ms. Delay 1000ms to ensure the newly generated API report appears in our HUD logs, then trigger browser print.
      setTimeout(() => {
        window.print();
      }, 1000);
    } catch (e) {
      console.error('Failed to generate report', e);
    }
  };
  return (
    <>
      <PrintablePatientReport data={data} mm={mm} face={face} lab={lab} spo2={spo2} temp={temp} alerts={alerts} />


      {/* SIDEBAR NAVIGATION */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <Activity size={24} strokeWidth={3} />
          </div>
          <div>
            <div className="sidebar-brand-text">NEOGUARD</div>
            <div style={{ fontWeight: 800, fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '1.5px' }}>AI-DRIVEN PREDICTIVE CARE</div>
          </div>

        </div>

        <nav style={{ flex: 1 }}>
          <div style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)', marginBottom: '16px', letterSpacing: '1px' }}>CLINICAL MODULES</div>
          <div className={`sidebar-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            <Monitor size={20} /> Dashboard
          </div>
          <div className={`sidebar-item ${activeTab === 'logs' ? 'active' : ''}`} onClick={() => setActiveTab('logs')}>
            <AlertCircle size={20} /> Logs & History
          </div>
          <div className={`sidebar-item ${activeTab === 'system' ? 'active' : ''}`} onClick={() => setActiveTab('system')}>
            <Shield size={20} /> System Admin
          </div>
        </nav>

        <div style={{ marginTop: 'auto', padding: '24px', background: 'white', borderRadius: '24px', border: '1px solid var(--surface-border)', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <div style={{ position: 'relative' }}>
              <div style={{ width: '44px', height: '44px', borderRadius: '14px', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 10px rgba(2, 132, 199, 0.3)' }}>
                <User size={22} color="#FFF" />
              </div>
              <div style={{ position: 'absolute', bottom: '-2px', right: '-2px', width: '12px', height: '12px', borderRadius: '50%', background: 'var(--mint)', border: '2px solid white' }}></div>
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 900, color: 'var(--text-main)' }}>Dr. Asawa</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--mint)', boxShadow: '0 0 8px var(--mint)' }}></div>
                <div style={{ fontSize: '9px', color: 'var(--clinical-blue)', fontWeight: 800, letterSpacing: '0.5px' }}>ON ACTIVE DUTY</div>
              </div>
            </div>

          </div>
          <button className="btn-ack" style={{ width: '100%', padding: '12px', fontSize: '10px', fontWeight: 800, color: 'var(--secondary)', borderColor: 'rgba(225, 29, 72, 0.2)' }} onClick={onLogout}>
            DE-AUTHORIZE SESSION
          </button>
        </div>

      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="main-content">
        <header className="status-bar">
          <div className="status-group">
            <div className="status-indicator">
              <div className={`status-dot ${isOnline ? 'online' : 'offline'}`} />
              <span style={{ fontWeight: 800 }}>ENGINE STATUS:</span> {isOnline ? 'ACTIVE' : 'DISCONNECTED'}
            </div>
            <div className="status-indicator" style={{ borderLeft: '1px solid var(--surface-border)', paddingLeft: '24px' }}>
              <Clock size={16} color="var(--primary)" />
              <span style={{ fontFamily: 'monospace', fontSize: '16px', fontWeight: 900, color: 'var(--text-main)', letterSpacing: '1px' }}>{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div className="status-indicator">
              <Wifi size={16} color={isCameraEnabled ? 'var(--mint)' : 'var(--text-muted)'} />
              {isCameraEnabled ? 'ENCRYPTED LINK' : 'LINK STANDBY'}
            </div>
            <div className={`risk-badge risk-${risk.color}`} style={{ padding: '10px 20px', fontSize: '12px' }}>{risk.label} ALERT</div>
          </div>
        </header>


        {/* --- MODULE 1: DASHBOARD --- */}
        {activeTab === 'dashboard' && (
          <div className="dashboard-viewport">
            {/* Patient Demographic Banner */}
            <div className="patient-banner">
              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(2, 132, 199, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
                  <User size={24} />
                </div>
                <div>
                  <h2 style={{ fontSize: '18px', fontWeight: 900 }}>B. INFANT #0821-A</h2>
                  <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                    <span className="risk-badge" style={{ fontSize: '9px', padding: '4px 8px' }}>NICU WARD 4</span>
                    <span className="risk-badge" style={{ fontSize: '9px', padding: '4px 8px', background: 'var(--surface-hover)', border: '1px solid var(--surface-border)', color: 'var(--text-muted)' }}>MALE</span>
                  </div>
                </div>
              </div>

              <div className="patient-info-group">
                <div className="patient-stat">
                  <span className="patient-stat-label">Gestational Age</span>
                  <span className="patient-stat-value">32 Weeks</span>
                </div>
                <div className="patient-stat" style={{ borderLeft: '1px solid var(--surface-border)', paddingLeft: '24px' }}>
                  <span className="patient-stat-label">Birth Weight</span>
                  <span className="patient-stat-value">1.85 kg</span>
                </div>
                <div className="patient-stat" style={{ borderLeft: '1px solid var(--surface-border)', paddingLeft: '24px' }}>
                  <span className="patient-stat-label">Blood Type</span>
                  <span className="patient-stat-value">O Positive</span>
                </div>
                <div className="patient-stat" style={{ borderLeft: '1px solid var(--surface-border)', paddingLeft: '24px' }}>
                  <span className="patient-stat-label">Attending</span>
                  <span className="patient-stat-value">Dr. Asawa</span>
                </div>
              </div>

              <button className="btn-ack" style={{ padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '8px' }} onClick={() => setActiveTab('logs')}>
                VIEW FULL CHART <ChevronRight size={14} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(350px, 1.2fr) minmax(300px, 1fr) minmax(300px, 1fr)', gap: '16px' }}>

              {/* Camera Video Block */}
              <div className="premium-card" style={{ padding: 0, position: 'relative' }}>
                <div style={{ position: 'absolute', top: '20px', left: '25px', zIndex: 30, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div className="pulse-dot"></div>
                  <span style={{ fontSize: '10px', fontWeight: 900, color: 'white', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>LIVE HUD FEED</span>
                </div>
                <div className="neural-overlay"></div>
                <div className="ai-data-stream">
                  {`> BUFFERING_STREAM_001 \n> NODE_SYNC_SUCCESS \n> AI_CORE_ACTIVE \n> LATENCY: 12ms`}
                </div>
                {isCameraSimulated && (
                  <div style={{ position: 'absolute', top: '15px', right: '15px', zIndex: 20, background: 'var(--primary)', color: 'white', fontSize: '9px', fontWeight: 900, padding: '4px 8px', borderRadius: '4px' }}>
                    SIMULATION ACTIVE
                  </div>
                )}
                <div className={`camera-box ${risk.label === 'CRITICAL' ? 'alerting' : ''}`} style={{ height: '300px' }}>
                  <div className="bio-grid-overlay"></div>
                  <div className="scanning-line"></div>

                  {face?.faceDetected && (
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', border: '2px solid var(--primary)', width: '150px', height: '150px', borderRadius: '20px', boxShadow: '0 0 20px rgba(2, 132, 199, 0.4)', zIndex: 5, pointerEvents: 'none' }}>
                      <div style={{ position: 'absolute', top: '-25px', left: '0', background: 'var(--primary)', color: 'white', fontSize: '9px', padding: '2px 8px', borderRadius: '4px', fontWeight: 900 }}>AI LOCKED</div>
                    </div>
                  )}
                  <CameraStream
                    isEnabled={isCameraEnabled}
                    isSimulated={isCameraSimulated}
                    onEnableSim={() => setIsCameraSimulated(true)}
                    onDisableSim={() => setIsCameraSimulated(false)}
                  />
                </div>
              </div>

              {/* Massive Risk Indicator */}
              <div className={`premium-card risk-panel-${risk.color}`} style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
                <div className="phi-gauge-container">
                  <div className="phi-score-circle" style={{ '--phi-val': data?.riskAssessment?.phi || 100 } as any}></div>
                  <div className="phi-value-center">
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '-4px' }}>PHI</div>
                    {data?.riskAssessment?.phi || 100}
                  </div>
                </div>
                <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '2px', marginBottom: '8px' }}>CLINICAL RISK THRESHOLD</div>
                <div style={{ fontSize: '32px', fontWeight: 900, color: `var(--${risk.color === 'orange' ? 'orange' : risk.color === 'red' ? 'secondary' : 'mint'})`, lineHeight: 1, letterSpacing: '-1.5px' }}>
                  {risk.label}
                </div>
                <div className="ai-reasoning-chip">AI_CONFIDENCE: {mm.confidence || 0}%</div>
              </div>



              {/* Professional Analytics Trend */}
              <div className="premium-card analytics-panel" style={{ display: 'flex', flexDirection: 'column', minHeight: '300px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                  <div>
                    <h3 style={{ fontSize: '13px', fontWeight: 900, color: 'var(--clinical-blue)', letterSpacing: '1px', textTransform: 'uppercase' }}>Waveform Analysis</h3>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 700 }}>SYNCHRONIZED_BIO_DATA_STREAM</div>
                  </div>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '9px', fontWeight: 800, color: 'var(--primary)' }}>BREATH_INTENSITY</div>
                      <div style={{ fontSize: '14px', fontWeight: 900, color: 'var(--text-main)' }}>{Math.round(mm.motion || 0)}%</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '9px', fontWeight: 800, color: 'var(--secondary)' }}>STILL_ACCUMULATION</div>
                      <div style={{ fontSize: '14px', fontWeight: 900, color: 'var(--text-main)' }}>{mm.stillTime || 0}s</div>
                    </div>
                  </div>
                </div>

                <div style={{ flex: 1, position: 'relative' }}>
                  <div style={{ position: 'absolute', top: 0, right: 0, fontSize: '9px', color: 'var(--mint)', fontWeight: 900, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <div style={{ width: '6px', height: '6px', background: 'var(--mint)', borderRadius: '50%', animation: 'pulse 1s infinite' }} /> LIVE_FEED
                  </div>
                  <LiveChart data={history} />
                </div>

                <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--surface-border)', paddingTop: '12px' }}>
                  <div style={{ fontSize: '9px', fontWeight: 800, color: 'var(--text-muted)' }}>HISTORICAL_WINDOW: 45 SEC</div>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px', fontWeight: 800 }}>
                      <div style={{ width: '10px', height: '10px', borderRadius: '2px', background: 'var(--primary)' }} /> BIOMETRIC
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px', fontWeight: 800 }}>
                      <div style={{ width: '10px', height: '10px', borderRadius: '2px', background: 'var(--secondary)' }} /> MOTION_LOSS
                    </span>
                  </div>
                </div>
              </div>


            </div>

            {/* Bottom Row: Detailed Metrics */}
            <div className="vitals-row" style={{ marginTop: '16px' }}>

              {/* Parameter 1: Breathing Rate */}
              <div className={`premium-card card-glow-${mm.breathingStatus === 'NORMAL' ? 'mint' : 'red'}`} style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="vital-label"><Wind size={14} /> Breathing Rate</div>
                <div className="vital-value heartbeat-pulse" style={{ color: mm.breathingStatus === 'NORMAL' ? 'var(--mint)' : 'var(--secondary)' }}>
                  {mm.breathingRate || 0} <span className="vital-unit">BPM</span>
                </div>
                <div className="vital-status-text">{mm.breathingStatus || 'WAITING...'}</div>
                <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid var(--surface-border)', fontSize: '9px', fontWeight: 700, color: 'var(--text-muted)' }}>
                  PRIMARY ID: <span style={{ color: 'var(--text-main)', fontWeight: 900 }}>RDS, Asphyxia</span>
                </div>
              </div>

              {/* Parameter 2: SpO2 */}
              <div className={`premium-card card-glow-${spo2.status === 'normal' ? 'mint' : 'red'}`} style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="vital-label"><Activity size={14} /> SpO₂ (Oxygen)</div>
                <div className="vital-value" style={{ color: spo2.status === 'normal' ? 'var(--mint)' : 'var(--secondary)' }}>
                  {spo2.value} <span className="vital-unit">%</span>
                </div>
                <div className="vital-status-text">{spo2.status === 'normal' ? 'OPTIMAL' : 'DESATURATION ALERT'}</div>
                <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid var(--surface-border)', fontSize: '9px', fontWeight: 700, color: 'var(--text-muted)' }}>
                  PRIMARY ID: <span style={{ color: 'var(--text-main)', fontWeight: 900 }}>RDS, Asphyxia</span>
                </div>
              </div>

              {/* Parameter 3: Skin Color */}
              <div className={`premium-card card-glow-${face.cyanosisScore >= 1 ? 'red' : 'mint'}`} style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="vital-label"><Shield size={14} /> Skin Color</div>
                <div className="vital-value" style={{ color: face.cyanosisScore >= 1 ? 'var(--secondary)' : 'var(--text-main)', fontSize: '32px' }}>
                  {face.cyanosisStatus || 'NORMAL'}
                </div>
                <div className="vital-status-text">Analytica: {face.cyanosisScore >= 1 ? 'Cyanosis Risk' : 'Clear'}</div>
                <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid var(--surface-border)', fontSize: '9px', fontWeight: 700, color: 'var(--text-muted)' }}>
                  PRIMARY ID: <span style={{ color: 'var(--text-main)', fontWeight: 900 }}>Jaundice, Sepsis, RDS</span>
                </div>
              </div>

              {/* Parameter 4: Temperature */}
              <div className={`premium-card card-glow-${temp.status === 'normal' ? 'mint' : 'red'}`} style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="vital-label"><Thermometer size={14} /> Temperature</div>
                <div className="vital-value" style={{ color: temp.status === 'normal' ? 'var(--mint)' : 'var(--secondary)' }}>
                  {temp.value} <span className="vital-unit">°C</span>
                </div>
                <div className="vital-status-text">{temp.status === 'normal' ? 'THERMONEUTRAL' : 'HYPOTHERMIA RISK'}</div>
                <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid var(--surface-border)', fontSize: '9px', fontWeight: 700, color: 'var(--text-muted)' }}>
                  PRIMARY ID: <span style={{ color: 'var(--text-main)', fontWeight: 900 }}>Sepsis, Hypothermia</span>
                </div>
              </div>

              {/* Parameter 5: Lab Reports */}
              <div className={`premium-card card-glow-${lab.status === 'normal' ? 'mint' : 'red'}`} style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="vital-label"><FileText size={14} /> Lab / Blood Panel</div>
                <div className="vital-value" style={{ color: lab.status === 'normal' ? 'var(--mint)' : 'var(--orange)', fontSize: '28px' }}>
                  SYNCED
                </div>
                <div className="vital-status-text">ABG, CRP, Glucose</div>
                <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid var(--surface-border)', fontSize: '9px', fontWeight: 700, color: 'var(--text-muted)' }}>
                  CORROBORATION: <span style={{ color: 'var(--text-main)', fontWeight: 900 }}>Metabolic, RDS, Sepsis</span>
                </div>
              </div>

            </div>

          </div>
        )}

        {/* --- MODULE 2: LOGS & HISTORY --- */}
        {activeTab === 'logs' && (
          <div className="dashboard-viewport">
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ fontSize: '24px', fontWeight: 900 }}>Clinical Logs</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Historical patient data and system alerts</p>
            </div>

            <div className="premium-card" style={{ padding: '20px', marginBottom: '16px', display: 'flex', gap: '16px', alignItems: 'center' }}>
              <div style={{ flex: 1, position: 'relative' }}>
                <Search size={16} style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', left: '16px', color: 'var(--text-muted)' }} />
                <input type="text" placeholder="Search logs by keyword..." style={{ width: '100%', padding: '12px 12px 12px 40px', background: 'var(--background)', border: '1px solid var(--surface-border)', borderRadius: '12px', outline: 'none', color: 'var(--text-main)', fontWeight: 600 }} />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px', background: 'var(--background)', border: '1px solid var(--surface-border)', borderRadius: '12px' }}>
                <Calendar size={16} /> <span style={{ fontSize: '13px', fontWeight: 700 }}>Today</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px', background: 'var(--background)', border: '1px solid var(--surface-border)', borderRadius: '12px', cursor: 'pointer' }}>
                <Filter size={16} /> <span style={{ fontSize: '13px', fontWeight: 700 }}>All Severities</span>
              </div>

              <button onClick={handleGenerateReport} style={{
                display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px',
                background: 'linear-gradient(45deg, var(--primary), var(--secondary))',
                color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer',
                fontWeight: 800, fontSize: '12px', letterSpacing: '1px',
                boxShadow: '0 4px 15px rgba(2, 132, 199, 0.3)'
              }}>
                <FileText size={16} /> GENERATE DIAGNOSTICS REPORT
              </button>
            </div>

            <div className="premium-card alerts-box" style={{ padding: 0, flex: 1, minHeight: '400px' }}>
              <table className="alerts-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Subsystem</th>
                    <th>Message</th>
                    <th>Severity Indicator</th>
                    <th>Action / Review</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.length > 0 ? alerts.map((a: any, i: number) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--text-muted)', fontWeight: 600 }}>{a.timestamp || new Date().toLocaleString()}</td>
                      <td style={{ fontWeight: 700 }}>{a.source || 'Monitor'}</td>
                      <td>{a.message}</td>
                      <td>
                        <span className={`risk-badge risk-${a.type === 'critical' ? 'red' : a.type === 'warning' ? 'orange' : 'green'}`}>
                          {a.type.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <button className="btn-ack" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          Review <ChevronRight size={12} />
                        </button>
                      </td>
                    </tr>
                  )) : (
                    Array.from({ length: 8 }).map((_, i) => (
                      <tr key={i}>
                        <td style={{ color: 'var(--text-muted)' }}>--/--/---- --:--</td>
                        <td>--</td>
                        <td style={{ color: 'var(--text-muted)' }}>No historical data logged in this block</td>
                        <td><span className="risk-badge" style={{ background: 'var(--background)' }}>NONE</span></td>
                        <td>--</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* --- MODULE 3: SYSTEM ADMINISTRATION --- */}
        {activeTab === 'system' && (
          <div className="dashboard-viewport">
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ fontSize: '24px', fontWeight: 900 }}>System Configuration</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Hardware status and algorithm thresholds</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) minmax(300px, 1fr)', gap: '24px' }}>

              <div className="premium-card">
                <h3 style={{ fontSize: '16px', fontWeight: 800, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Server size={18} color="var(--primary)" /> Hardware Capabilities
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--surface-border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--mint)', boxShadow: '0 0 10px var(--mint)' }}></div>
                      <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>Raspberry Pi Connection</span>
                    </div>
                    <span style={{ fontWeight: 800, color: 'var(--mint)' }}>CONNECTED</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--surface-border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: isCameraEnabled ? 'var(--mint)' : 'var(--orange)', boxShadow: `0 0 10px ${isCameraEnabled ? 'var(--mint)' : 'var(--orange)'}` }}></div>
                      <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>Camera Feed Setup</span>
                    </div>
                    <span style={{ fontWeight: 800, color: isCameraEnabled ? 'var(--mint)' : 'var(--orange)' }}>{isCameraEnabled ? 'ACTIVE' : 'BYPASS'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--surface-border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--mint)', boxShadow: '0 0 10px var(--mint)' }}></div>
                      <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>Microphone Array</span>
                    </div>
                    <span style={{ fontWeight: 800, color: 'var(--mint)' }}>LISTENING</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>API Latency</span>
                    <span style={{ fontWeight: 800, color: 'var(--text-main)' }}>42ms</span>
                  </div>
                </div>
              </div>

              <div className="premium-card">
                <h3 style={{ fontSize: '16px', fontWeight: 800, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Settings size={18} color="var(--primary)" /> Risk Thresholds
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 700 }}>Cry Sensitivity Level</span>
                      <span style={{ fontSize: '13px', fontWeight: 900 }}>High (85%)</span>
                    </div>
                    <div style={{ height: '8px', background: 'var(--background)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: '85%', background: 'var(--primary)', borderRadius: '4px' }} />
                    </div>
                  </div>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 700 }}>Motion Alert Timeout</span>
                      <span style={{ fontSize: '13px', fontWeight: 900 }}>24 Seconds</span>
                    </div>
                    <div style={{ height: '8px', background: 'var(--background)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: '60%', background: 'var(--warning)', borderRadius: '4px' }} />
                    </div>
                  </div>
                  <button className="vibrant-btn" style={{ marginTop: '12px', padding: '12px', background: 'var(--background)', color: 'var(--text-main)', border: '1px solid var(--surface-border)' }}>Modify Clinic Thresholds</button>
                </div>
              </div>

              <div className="premium-card" style={{ gridColumn: 'span 2' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 800, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Power size={18} color="var(--primary)" /> System Commands
                </h3>
                <div style={{ display: 'flex', gap: '16px' }}>
                  <button className="btn-ack" style={{ padding: '16px 24px', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }} onClick={() => window.location.reload()}>
                    <RotateCcw size={16} /> Restart Application
                  </button>
                  <button className="btn-ack" style={{ padding: '16px 24px', flex: 1 }}>Clear Cache Logic</button>
                  <button className="vibrant-btn" style={{ padding: '16px 24px', flex: 1, background: 'var(--secondary)' }} onClick={() => fetch(`${API_BASE_URL}/api/test_alert`, { method: 'POST' })}>
                    TRIGGER TEST ALERT
                  </button>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* QUICK CONTROLS FOOTER (Always Visible) */}
        <footer className="controls-panel">
          <div style={{ display: 'flex', gap: '24px' }}>
            <div className="control-item">
              <span className="vital-label" style={{ marginBottom: 0 }}><Camera size={14} /> Camera Feed</span>
              <label className="switch">
                <input type="checkbox" checked={isCameraEnabled} onChange={() => setIsCameraEnabled(!isCameraEnabled)} />
                <span className="slider"></span>
              </label>
            </div>
            <div className="control-item">
              <span className="vital-label" style={{ marginBottom: 0 }}><Fan size={14} /> Ward Fan</span>
              <label className="switch">
                <input type="checkbox" checked={isFanOn} onChange={() => setIsFanOn(!isFanOn)} />
                <span className="slider"></span>
              </label>
            </div>
            <div className="control-item">
              <span className="vital-label" style={{ marginBottom: 0 }}>{isMuted ? <VolumeX size={14} /> : <Volume2 size={14} />} Hardware Buzzer</span>
              <label className="switch">
                <input type="checkbox" checked={!isMuted} onChange={() => setIsMuted(!isMuted)} />
                <span className="slider"></span>
              </label>
            </div>
          </div>
          <button className="btn-reset" onClick={() => window.location.reload()}>
            Force Sync
          </button>
        </footer>
      </main>

      {/* EMERGENCY MODAL */}
      {risk.label === 'CRITICAL' && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 9999, background: 'rgba(225, 29, 72, 0.15)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: 'white', padding: '60px', borderRadius: '40px', textAlign: 'center', boxShadow: '0 40px 80px rgba(0,0,0,0.1)', border: '4px solid var(--secondary)' }}>
            <AlertCircle size={80} color="var(--secondary)" style={{ marginBottom: '20px' }} />
            <h1 style={{ fontSize: '48px', fontWeight: 900, color: 'var(--secondary)' }}>MEDICAL ALERT</h1>
            <p style={{ fontSize: '18px', fontWeight: 800, color: '#0F172A' }}>CRITICAL VITAL SIGNS DETECTED</p>
            <button className="vibrant-btn" style={{ marginTop: '30px', background: 'var(--secondary)' }} onClick={() => window.location.reload()}>ACKNOWLEDGE EMERGENCY</button>
          </div>
        </div>
      )}
    </>
  );
}

// --- PARENT VIEW COMPONENT ---
function ParentView({ data, risk, mm, face, alerts, isOnline, isCameraEnabled, onLogout }: any) {
  const [activeTab, setActiveTab] = useState<'monitor' | 'logs' | 'summary'>('monitor');
  const vitals = data?.vitals || [];
  const heartRate = vitals.find((v: any) => v.title === 'Heart Rate')?.value || '--';
  const temperature = vitals.find((v: any) => v.title === 'Body Temp')?.value || '--';
  const spo2 = vitals.find((v: any) => v.title === 'Oxygen Saturation')?.value || '--';

  return (
    <div className="parent-view" style={{ minHeight: '100vh', background: '#F8FAFC', display: 'flex', flexDirection: 'column' }}>
      {/* Mobile-Friendly Header */}
      <header style={{ background: 'white', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #E2E8F0', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
            <Baby size={24} />
          </div>
          <div>
            <div style={{ fontWeight: 900, fontSize: '18px', letterSpacing: '-0.5px' }}>NeoGuard <span style={{ color: 'var(--primary)', fontSize: '12px' }}>Parent</span></div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 800 }}>STATION B • INFANT #0821-A</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn-ack" style={{ padding: '8px', borderRadius: '10px' }}>
            <Bell size={20} />
          </button>
          <button className="btn-ack" style={{ padding: '8px', borderRadius: '10px', color: 'var(--secondary)' }} onClick={onLogout}>
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <main style={{ flex: 1, padding: '16px', maxWidth: '600px', margin: '0 auto', width: '100%' }}>
        {/* Connection Status */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', padding: '12px 16px', background: isOnline ? '#ECFDF5' : '#FEF2F2', borderRadius: '16px', border: `1px solid ${isOnline ? '#10B98133' : '#E11D4833'}` }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: isOnline ? '#10B981' : '#E11D48' }}></div>
            <span style={{ fontSize: '12px', fontWeight: 800, color: isOnline ? '#065F46' : '#991B1B' }}>{isOnline ? 'LIVE SECURE LINK' : 'LINK DISCONNECTED'}</span>
          </div>
          {risk.label !== 'NORMAL' && (
            <div style={{ padding: '4px 12px', background: risk.color === 'red' ? '#E11D48' : '#EA580C', color: 'white', borderRadius: '20px', fontSize: '10px', fontWeight: 900 }}>
              {risk.label} ALERT
            </div>
          )}
        </div>

        {activeTab === 'monitor' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Live Feed */}
            <div className="premium-card" style={{ padding: 0, overflow: 'hidden', height: '240px', position: 'relative' }}>
              <div style={{ position: 'absolute', top: '12px', right: '12px', zIndex: 10, background: 'rgba(0,0,0,0.5)', borderRadius: '4px', padding: '2px 8px', color: 'white', fontSize: '10px', fontWeight: 800 }}>LIVE</div>
              <CameraStream isEnabled={isCameraEnabled} isSimulated={false} />
            </div>

            {/* Quick Stats Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="premium-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <Activity size={24} color="var(--primary)" style={{ marginBottom: '8px' }} />
                <div style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)', marginBottom: '4px' }}>HEART RATE</div>
                <div style={{ fontSize: '28px', fontWeight: 900 }}>{heartRate}<span style={{ fontSize: '12px', marginLeft: '2px' }}>bpm</span></div>
              </div>
              <div className="premium-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <Thermometer size={24} color="#EA580C" style={{ marginBottom: '8px' }} />
                <div style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)', marginBottom: '4px' }}>TEMP</div>
                <div style={{ fontSize: '28px', fontWeight: 900 }}>{temperature}<span style={{ fontSize: '12px', marginLeft: '2px' }}>°C</span></div>
              </div>
              <div className="premium-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <Activity size={24} color="#065F46" style={{ marginBottom: '8px' }} />
                <div style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)', marginBottom: '4px' }}>OXYGEN (SpO2)</div>
                <div style={{ fontSize: '28px', fontWeight: 900, color: parseInt(spo2) < 90 ? 'var(--secondary)' : 'inherit' }}>{spo2}<span style={{ fontSize: '12px', marginLeft: '2px' }}>%</span></div>
              </div>
            </div>

            {/* Status Card */}
            <div className="premium-card" style={{ background: 'linear-gradient(135deg, white 0%, #F1F5F9 100%)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '20px' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)' }}>ACTIVITY STATUS</div>
                  <div style={{ fontSize: '18px', fontWeight: 900, color: 'var(--primary)', marginTop: '4px' }}>
                    {mm.motion > 5 ? 'ACTIVE & MOVING' : 'CALM & SLEEPING'}
                  </div>
                </div>
                <div style={{ flex: 1, textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)' }}>SKIN STATUS</div>
                  <div style={{ fontSize: '18px', fontWeight: 900, color: face.cyanosisScore >= 1 ? 'var(--secondary)' : '#059669', marginTop: '4px' }}>
                    {face.cyanosisStatus || 'NORMAL'}
                  </div>
                </div>
              </div>
            </div>

            {/* Emergency Button */}
            <button
              className="vibrant-btn"
              style={{ background: 'var(--secondary)', height: '64px', fontSize: '16px', borderRadius: '16px', marginTop: '12px', boxShadow: '0 8px 24px rgba(225, 29, 72, 0.3)' }}
              onClick={() => alert("EMERGENCY SIGNAL SENT TO NURSE STATION")}
            >
              <LifeBuoy size={20} /> SIGNAL ASSISTANCE
            </button>
          </div>
        )}

        {activeTab === 'logs' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 900, marginBottom: '8px' }}>Today's Activity</h3>
            {alerts.length > 0 ? alerts.map((a: any, i: number) => (
              <div key={i} className="premium-card" style={{ display: 'flex', gap: '16px', alignItems: 'center', padding: '16px' }}>
                <div style={{ padding: '8px', borderRadius: '10px', background: a.type === 'critical' ? '#FEF2F2' : '#F1F5F9', color: a.type === 'critical' ? 'var(--secondary)' : 'var(--primary)' }}>
                  {a.type === 'critical' ? <AlertCircle size={20} /> : <Activity size={20} />}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13px', fontWeight: 800 }}>{a.message}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>{a.timestamp || 'Just now'}</div>
                </div>
              </div>
            )) : (
              <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
                <Clock size={40} style={{ opacity: 0.2, marginBottom: '12px' }} />
                <p style={{ fontWeight: 700 }}>No significant events today</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'summary' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="premium-card">
              <h3 style={{ fontSize: '18px', fontWeight: 900, marginBottom: '12px' }}>Health Summary</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #F1F5F9', paddingBottom: '8px' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-muted)' }}>Weight Gain</span>
                  <span style={{ fontWeight: 900, color: '#059669' }}>+45g (Today)</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #F1F5F9', paddingBottom: '8px' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-muted)' }}>Sleep Duration</span>
                  <span style={{ fontWeight: 900 }}>18.5 hrs (Avg)</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-muted)' }}>Stability Index</span>
                  <span style={{ fontWeight: 900 }}>Excellent</span>
                </div>
              </div>
            </div>
            <div className="premium-card" style={{ background: '#EFF6FF', borderColor: '#BFDBFE' }}>
              <div style={{ display: 'flex', gap: '12px' }}>
                <FileText color="#1D4ED8" />
                <div>
                  <div style={{ fontWeight: 900, color: '#1E40AF' }}>Dr. Asawa's Note</div>
                  <div style={{ fontSize: '13px', color: '#1E40AF', marginTop: '4px', fontStyle: 'italic' }}>
                    "Infant is showing great progress with respiratory stability. Feeding volume increased today."
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Mobile Nav Bar */}
      <nav style={{ background: 'white', borderTop: '1px solid #E2E8F0', display: 'flex', padding: '8px 4px 24px', position: 'sticky', bottom: 0, zIndex: 100 }}>
        <button
          style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', background: 'none', border: 'none', color: activeTab === 'monitor' ? 'var(--primary)' : 'var(--text-muted)', cursor: 'pointer' }}
          onClick={() => setActiveTab('monitor')}
        >
          <Home size={20} fill={activeTab === 'monitor' ? 'var(--primary)' : 'none'} />
          <span style={{ fontSize: '10px', fontWeight: 800 }}>LIVE</span>
        </button>
        <button
          style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', background: 'none', border: 'none', color: activeTab === 'logs' ? 'var(--primary)' : 'var(--text-muted)', cursor: 'pointer' }}
          onClick={() => setActiveTab('logs')}
        >
          <Bell size={20} fill={activeTab === 'logs' ? 'var(--primary)' : 'none'} />
          <span style={{ fontSize: '10px', fontWeight: 800 }}>ALERTS</span>
        </button>
        <button
          style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', background: 'none', border: 'none', color: activeTab === 'summary' ? 'var(--primary)' : 'var(--text-muted)', cursor: 'pointer' }}
          onClick={() => setActiveTab('summary')}
        >
          <FileText size={20} fill={activeTab === 'summary' ? 'var(--primary)' : 'none'} />
          <span style={{ fontSize: '10px', fontWeight: 800 }}>HEALTH</span>
        </button>
      </nav>

      {/* EMERGENCY MODAL (Parent Version) */}
      {risk.label === 'CRITICAL' && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 9999, background: 'rgba(225, 29, 72, 0.4)', backdropFilter: 'blur(15px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
          <div style={{ background: 'white', padding: '40px 24px', borderRadius: '32px', textAlign: 'center', boxShadow: '0 40px 80px rgba(0,0,0,0.2)', border: '4px solid var(--secondary)', width: '100%' }}>
            <AlertCircle size={64} color="var(--secondary)" style={{ marginBottom: '16px' }} />
            <h1 style={{ fontSize: '32px', fontWeight: 900, color: 'var(--secondary)', lineHeight: 1.1 }}>CRITICAL ALERT</h1>
            <p style={{ fontSize: '16px', fontWeight: 800, color: '#0F172A', marginTop: '12px' }}>NURSING STAFF ALERTED</p>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '8px' }}>The monitoring system has detected an abnormality. Medical personnel are on their way.</p>
            <button className="vibrant-btn" style={{ marginTop: '30px', background: 'var(--secondary)' }} onClick={() => window.location.reload()}>ACKNOWLEDGE</button>
          </div>
        </div>
      )}
    </div>
  );
}

function LiveChart({ data }: any) {
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ background: 'rgba(15, 23, 42, 0.95)', padding: '12px 16px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', backdropFilter: 'blur(8px)' }}>
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '9px', fontWeight: 900, marginBottom: '8px', letterSpacing: '1px' }}>MARKER_DATA</div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <div>
              <div style={{ color: 'var(--primary)', fontWeight: 900, fontSize: '11px' }}>BREATHING</div>
              <div style={{ color: 'white', fontSize: '20px', fontWeight: 900 }}>{payload[0].value.toFixed(1)}%</div>
            </div>
            {payload[1] && (
              <div>
                <div style={{ color: 'var(--secondary)', fontWeight: 900, fontSize: '11px' }}>STILLNESS</div>
                <div style={{ color: 'white', fontSize: '20px', fontWeight: 900 }}>{payload[1].value}s</div>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorBreathing" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorStillness" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--secondary)" stopOpacity={0.2} />
            <stop offset="95%" stopColor="var(--secondary)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="1 5" vertical={true} stroke="#E2E8F0" />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.02)', strokeWidth: 1 }} />
        <XAxis dataKey="time" hide />
        <YAxis hide domain={[0, 'dataMax + 10']} />
        <Area
          type="monotone"
          dataKey="breathing"
          stroke="var(--primary)"
          strokeWidth={4}
          fillOpacity={1}
          fill="url(#colorBreathing)"
          isAnimationActive={false}
          activeDot={{ r: 6, stroke: 'white', strokeWidth: 2, fill: 'var(--primary)' }}
        />
        <Area
          type="monotone"
          dataKey="stillness"
          stroke="var(--secondary)"
          strokeWidth={3}
          fillOpacity={1}
          fill="url(#colorStillness)"
          isAnimationActive={false}
          activeDot={{ r: 4, stroke: 'white', strokeWidth: 2, fill: 'var(--secondary)' }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}


// Fixed the blinking by using a stable reference for the stream
function CameraStream({ isEnabled, isSimulated, onEnableSim }: { isEnabled: boolean, isSimulated?: boolean, onEnableSim?: () => void, onDisableSim?: () => void }) {

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isSimulated) {
      setError(null);
      return;
    }
    if (!isEnabled) {
      if (videoRef.current) videoRef.current.srcObject = null;
      setError(null);
      return;
    }

    let currentStream: MediaStream | null = null;
    let isActive = true;

    async function start() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        if (isActive) {
          currentStream = stream;
          if (videoRef.current) videoRef.current.srcObject = stream;
          setError(null);
        } else {
          stream.getTracks().forEach(t => t.stop());
        }
      } catch (e: any) {
        if (isActive) {
          if (e.name === 'NotAllowedError') setError('Permission Denied');
          else if (e.name === 'NotFoundError') setError('No Camera Detected');
          else setError('Initialization Failed');
        }
      }
    }

    start();

    const loop = setInterval(() => {
      if (isEnabled && videoRef.current && canvasRef.current && currentStream && !error) {
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) {
          ctx.drawImage(videoRef.current, 0, 0, 320, 240);
          canvasRef.current.toBlob(blob => {
            if (blob) {
              const form = new FormData();
              form.append('file', blob, 'f.jpg');
              fetch(`${API_BASE_URL}/api/process_frame`, { method: 'POST', body: form }).catch(() => { });
            }
          }, 'image/jpeg', 0.4);
        }
      }
    }, 333); // 3Hz for better motion/breathing resolution

    return () => {
      isActive = false;
      clearInterval(loop);
      if (currentStream) {
        currentStream.getTracks().forEach(t => t.stop());
      }
    };
  }, [isEnabled, isSimulated]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', background: '#111', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {(!isEnabled || error) && (
        <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'white', zIndex: 10, background: 'rgba(0,0,0,0.8)', padding: '20px', textAlign: 'center' }}>
          <Camera size={48} opacity={0.3} style={{ marginBottom: '12px' }} />
          <div style={{ fontSize: '11px', fontWeight: 900, letterSpacing: '1px', color: error ? 'var(--secondary)' : 'white' }}>
            {error ? error.toUpperCase() : 'MONITORING PAUSED'}
          </div>
          <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
            {error && <button onClick={() => window.location.reload()} style={{ padding: '8px 16px', border: '1px solid white', background: 'transparent', color: 'white', fontSize: '10px', fontWeight: 800, cursor: 'pointer' }}>RETRY</button>}
            <button onClick={() => onEnableSim?.()} style={{ padding: '8px 16px', background: 'white', border: 'none', color: '#000', fontSize: '10px', fontWeight: 800, cursor: 'pointer' }}>SIMULATE</button>
          </div>
        </div>
      )}
      {!isEnabled || error ? (
        <div style={{ width: '100%', height: '100%', background: '#0a0a0a' }} />
      ) : (
        <video ref={videoRef} autoPlay muted playsInline style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      )}
      <canvas ref={canvasRef} width="320" height="240" style={{ display: 'none' }} />
    </div>
  );
}

function AuthFlow({ onLogin }: any) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('Neonatal Specialist');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAuth = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || (isRegister && !fullName)) {
      setError('Required fields missing');
      return;
    }

    setError('');
    setLoading(true);

    setTimeout(() => {
      const users = JSON.parse(localStorage.getItem('vita_neo_users') || '[]');

      if (isRegister) {
        if (users.find((u: any) => u.email === email)) {
          setError('Account already exists');
          setLoading(false);
          return;
        }
        users.push({ email, password, fullName, role: role.includes('Specialist') ? 'doctor' : 'parent' });
        localStorage.setItem('vita_neo_users', JSON.stringify(users));
        setIsRegister(false);
        setLoading(false);
        alert('Credentials Registered Securely');
      } else {
        const user = users.find((u: any) => u.email === email && u.password === password);
        const selectedRole = role.includes('Specialist') ? 'doctor' : 'parent';

        if (user) {
          if (user.role === selectedRole) {
            onLogin(user.role);
          } else {
            setError(`Credential valid but for ${user.role.toUpperCase()} portal`);
            setLoading(false);
          }
        } else if (email === 'admin' && password === 'admin') {
          if (selectedRole === 'doctor') {
            onLogin('doctor');
          } else {
            setError('Admin credentials restricted to DOCTOR portal');
            setLoading(false);
          }
        } else if (email === 'parent' && password === 'parent') {
          if (selectedRole === 'parent') {
            onLogin('parent');
          } else {
            setError('Parent credentials restricted to PARENT portal');
            setLoading(false);
          }
        } else {
          setError('Security verification failed');
          setLoading(false);
        }
      }
    }, 2000);
  };

  return (
    <div className="auth-container">
      <div className="auth-medical-bg"></div>
      <div className="auth-bg-ecg"></div>
      <div className="auth-bg-particles"></div>


      <div className="login-card">
        <div className="auth-brand">
          <div className="sidebar-logo-icon" style={{
            margin: '0 auto 24px',
            width: '64px', height: '64px', borderRadius: '18px',
            boxShadow: '0 10px 30px rgba(2, 132, 199, 0.4)'
          }}>
            <Shield size={32} />
          </div>
          <h1 className="auth-title">NEOGUARD</h1>
          <p className="auth-subtitle">AI-Driven Predictive Neonatal Monitoring</p>
          <p className="auth-description">Non-Contact Multi-Parameter Survival Engine</p>
        </div>

        <div className="auth-role-selector" style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
          <button
            type="button"
            className={`role-btn ${role.includes('Specialist') ? 'active' : ''}`}
            style={{ flex: 1, padding: '16px', borderRadius: '16px', border: '1px solid var(--surface-border)', background: role.includes('Specialist') ? 'rgba(2, 132, 199, 0.1)' : 'white', cursor: 'pointer', transition: 'all 0.3s', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}
            onClick={() => setRole('Neonatal Specialist')}
          >
            <Monitor size={24} color={role.includes('Specialist') ? 'var(--primary)' : 'var(--text-muted)'} />
            <div style={{ fontSize: '11px', fontWeight: 900, color: role.includes('Specialist') ? 'var(--primary)' : 'var(--text-muted)' }}>DOCTOR</div>
          </button>
          <button
            type="button"
            className={`role-btn ${role.includes('Parent') ? 'active' : ''}`}
            style={{ flex: 1, padding: '16px', borderRadius: '16px', border: '1px solid var(--surface-border)', background: role.includes('Parent') ? 'rgba(2, 132, 199, 0.1)' : 'white', cursor: 'pointer', transition: 'all 0.3s', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}
            onClick={() => setRole('Parent / Guardian')}
          >
            <Baby size={24} color={role.includes('Parent') ? 'var(--primary)' : 'var(--text-muted)'} />
            <div style={{ fontSize: '11px', fontWeight: 900, color: role.includes('Parent') ? 'var(--primary)' : 'var(--text-muted)' }}>PARENT</div>
          </button>
        </div>

        <div className="auth-toggle" style={{ marginBottom: '24px' }}>
          <div className={`auth-toggle-slider ${isRegister ? 'right' : ''}`}></div>
          <button type="button" className={`auth-toggle-btn ${!isRegister ? 'active' : ''}`} onClick={() => { setIsRegister(false); setError(''); }}>Sign In</button>
          <button type="button" className={`auth-toggle-btn ${isRegister ? 'active' : ''}`} onClick={() => { setIsRegister(true); setError(''); }}>Provision</button>
        </div>

        <form onSubmit={handleAuth}>
          {isRegister && (
            <>
              <div className="auth-input-group">
                <label className="auth-label">Full Clinical Name</label>
                <input
                  type="text"
                  placeholder="Dr. Jane Smith"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  className="vibrant-input"
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="auth-input-group">
                  <label className="auth-label">Medical License #</label>
                  <input
                    type="text"
                    placeholder="ML-123456"
                    className="vibrant-input"
                  />
                </div>
                <div className="auth-input-group">
                  <label className="auth-label">Hospital ID</label>
                  <input
                    type="text"
                    placeholder="HOSP-990"
                    className="vibrant-input"
                  />
                </div>
              </div>
            </>
          )}




          <div className="auth-input-group">
            <label className="auth-label">User Identifier</label>
            <input
              type="text"
              placeholder="clinical_id@health.org"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="vibrant-input"
            />
          </div>

          <div className="auth-input-group">
            <label className="auth-label">Access Credentials</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="vibrant-input"
            />
          </div>

          {error && <p style={{ color: 'var(--secondary)', fontSize: '11px', fontWeight: 700, margin: '8px 0 16px', animation: 'shake 0.4s' }}>{error}</p>}

          <button
            type="submit"
            className="vibrant-btn"
            disabled={loading}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', marginTop: '12px' }}
          >
            {loading ? (
              <>
                <RotateCcw size={16} className="animate-spin" />
                Validating Secure Node...
              </>
            ) : (
              <>
                {isRegister ? <div style={{ width: 16 }}><User size={16} /></div> : <div style={{ width: 16 }}><Shield size={16} /></div>}
                {isRegister ? 'PROVISION ACCOUNT' : 'AUTHORIZE SESSION'}
              </>
            )}
          </button>
        </form>

        <div className="auth-status-panel">
          <div className="status-item">
            <p className="status-label">Engine</p>
            <p className="status-val"><div className="status-dot"></div> Active</p>
          </div>
          <div className="status-item">
            <p className="status-label">Node</p>
            <p className="status-val">Secure</p>
          </div>
          <div className="status-item">
            <p className="status-label">latency</p>
            <p className="status-val">12ms</p>
          </div>
        </div>

        <div className="hipaa-badge">
          <Shield size={10} />
          SECURE CLINICAL ENVIRONMENT
        </div>
      </div>

      <div className="auth-footer">
        FOR AUTHORIZED CLINICAL PERSONNEL ONLY • NEOGUARD SURVIVAL ENGINE v2.0.1
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .animate-spin { animation: spin 1s linear infinite; }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
      `}</style>
    </div>
  );
}

export default App;