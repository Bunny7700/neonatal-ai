import { useState, useEffect, useRef } from 'react';
import { AlertCircle, Shield, Camera, Bell, Monitor, Activity, Heart, Wind, Zap, Mic, RefreshCcw } from 'lucide-react';
import { CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, XAxis, YAxis } from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5001";

// Robust history generator
const generateHistory = () => Array.from({ length: 30 }, (_, i) => ({ time: i, motion: 0, breathing: 0 }));

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [data, setData] = useState<any>(null);
  const [history, setHistory] = useState<any[]>(generateHistory());
  const [error, setError] = useState<string | null>(null);
  const [isCameraEnabled, setIsCameraEnabled] = useState<boolean>(true);

  // 0. Sync Camera Status with Backend
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/camera_status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: isCameraEnabled })
    }).catch(err => console.error("Camera sync error:", err));
  }, [isCameraEnabled]);

  // 1. Data Polling
  useEffect(() => {
    if (!isAuthenticated) return;

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/dashboard`);
        if (!res.ok) throw new Error("Backend Connection Failed");
        const json = await res.json();
        setData(json);
        setError(null);

        // Update Waveform Data
        setHistory(prev => {
          const newEntry = {
            time: prev.length,
            motion: json.motionMonitoring?.motion || 0,
            breathing: json.motionMonitoring?.breathingRate || 0
          };
          return [...prev.slice(-29), newEntry];
        });
      } catch (err: any) {
        console.error("Polling Error:", err);
        setError(err.message);
      }
    };

    const interval = setInterval(poll, 800);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  // 2. Apnea Alarm Logic
  useEffect(() => {
    let alarm: any;
    const isCrisis = isCameraEnabled && (data?.motionMonitoring?.status === 'UNSAFE' || data?.motionMonitoring?.status === 'WARNING' || (data?.motionMonitoring?.stillTime >= 20));

    if (isCrisis && isAuthenticated) {
      const playAlarm = () => {
        try {
          const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
          const osc = ctx.createOscillator();
          const g = ctx.createGain();
          osc.type = 'square';
          osc.frequency.setValueAtTime(1000, ctx.currentTime);
          g.gain.setValueAtTime(0.1, ctx.currentTime);
          g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.4);
          osc.connect(g);
          g.connect(ctx.destination);
          osc.start();
          osc.stop(ctx.currentTime + 0.5);
          setTimeout(() => ctx.close(), 1000);
        } catch (e) { }
      };
      playAlarm();
      alarm = setInterval(playAlarm, 1000);
    }
    return () => clearInterval(alarm);
  }, [data, isAuthenticated]);

  // 3. Render Handling with Crash Protection
  try {
    if (!isAuthenticated) return <AuthFlow onLogin={() => setIsAuthenticated(true)} />;

    if (!data) {
      return (
        <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Activity size={60} color="var(--primary)" style={{ animation: 'pulse-soft 1s infinite' }} />
            <h2 style={{ marginTop: '20px', fontWeight: 800, color: 'var(--text-muted)' }}>CONNECTING TO BABY MONITOR...</h2>
            {error && <p style={{ color: 'var(--secondary)', marginTop: '10px' }}>{error}</p>}
          </div>
        </div>
      );
    }

    const mm = data.motionMonitoring || {};
    const cd = data.cryDetection || {};
    const pt = data.patient || { id: 'NB-UNIT-01', status: 'In-Range' };
    const al = data.alerts || [];
    const isCritical = mm.status === 'UNSAFE' || mm.stillTime >= 20;
    const isWarning = mm.status === 'WARNING';
    const isCrisis = isCritical || isWarning;

    return (
      <div className={`fade-up ${isCrisis ? 'alert-pulse' : ''}`} style={{ minHeight: '100vh', padding: '40px', display: 'flex', gap: '40px' }}>
        {/* Sidebar Nav */}
        <aside className="premium-card" style={{ width: '320px', padding: '40px 30px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '40px' }}>
            <div style={{ width: '48px', height: '48px', background: 'var(--primary)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}><Heart fill="white" /></div>
            <div>
              <h1 style={{ fontSize: '20px', fontWeight: 900 }}>NEO-CARE</h1>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 800 }}>PRECISION ANALYTICS</span>
            </div>
          </div>

          <nav style={{ flex: 1 }}>
            <div className="sidebar-item active"><Monitor size={20} /> Dashboard</div>
            <div className="sidebar-item"><Activity size={20} /> Vitals History</div>
            <div className="sidebar-item"><Shield size={20} /> Admin Tools</div>
          </nav>

          <button onClick={() => window.location.reload()} className="vibrant-btn" style={{ width: '100%', height: '54px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
            <RefreshCcw size={18} /> RESET SESSION
          </button>
        </aside>

        {/* Main Dashboard */}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '40px' }}>
          <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ fontSize: '32px', fontWeight: 900 }}>Vitals Stream</h2>
              <p style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Real-time monitoring for Patient ID: {pt.id}</p>
            </div>
            <div style={{ padding: '15px 25px', borderRadius: '24px', background: 'white', border: '1px solid var(--surface-border)', boxShadow: '0 4px 15px rgba(0,0,0,0.02)' }}>
              <div style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)' }}>PATIENT STATUS</div>
              <div style={{ fontWeight: 900, color: isCritical ? 'var(--secondary)' : (isWarning ? 'var(--accent)' : 'var(--mint)') }}>
                {isCritical ? 'CRITICAL APNEA' : (isWarning ? (mm.breathingStatus === 'SLOW' ? 'SLOW BREATHING' : 'SHALLOW BREATHING') : 'STABLE BREATHING')}
              </div>
            </div>
          </header>

          {/* Stats Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px' }}>
            <StatCard
              label={`Breathing (${mm.breathingStatus || 'NORMAL'})`}
              value={mm.breathingRate || 0}
              unit="BPM"
              color={isWarning ? 'var(--accent)' : 'var(--primary)'}
              icon={<Wind />}
              isFlashing={isWarning}
            />
            <StatCard label="Motion" value={mm.motion || 0} unit="RAW" color="var(--lavender)" icon={<Zap />} />
            <StatCard label="Apnea Timer" value={mm.stillTime || 0} unit="SEC" color={mm.stillTime > 10 ? 'var(--secondary)' : 'var(--mint)'} icon={<Activity />} />
            <StatCard label="System Trust" value={mm.confidence || 98} unit="%" color="var(--primary)" icon={<Shield />} />
          </div>

          {/* Live Content */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '40px', flex: 1 }}>
            <div className="premium-card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ padding: '24px 30px', borderBottom: '1px solid var(--surface-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontWeight: 900, fontSize: '18px' }}>Vision Core Feed</h3>
                <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)' }}>CAMERA CONTROL</span>
                    <label className="switch">
                      <input
                        type="checkbox"
                        checked={isCameraEnabled}
                        onChange={() => setIsCameraEnabled(!isCameraEnabled)}
                      />
                      <span className="slider"></span>
                    </label>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <div style={{ width: '8px', height: '8px', background: isCameraEnabled ? 'var(--mint)' : 'var(--text-muted)', borderRadius: '50%', animation: isCameraEnabled ? 'pulse-soft 1s infinite' : 'none' }} />
                    <span style={{ fontSize: '11px', fontWeight: 800, color: isCameraEnabled ? 'var(--mint)' : 'var(--text-muted)' }}>{isCameraEnabled ? 'LIVE' : 'OFFLINE'}</span>
                  </div>
                </div>
              </div>
              <div style={{ flex: 1, position: 'relative' }}>
                <CameraPreview isAlert={isCritical} isEnabled={isCameraEnabled} />
              </div>
            </div>

            <div className="premium-card" style={{ padding: '30px', display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontWeight: 900, fontSize: '18px', marginBottom: '20px' }}>Breathing Waveform</h3>
              <div style={{ flex: 1 }}>
                <LiveWaveform data={history} />
              </div>
            </div>
          </div>

          {/* Bottom Analytics */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>
            <div className="premium-card" style={{ padding: '30px', display: 'flex', alignItems: 'center', gap: '30px' }}>
              <div style={{ width: '90px', height: '90px', borderRadius: '50%', background: cd.status === 'distress' ? 'var(--secondary)' : 'var(--mint)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', boxShadow: `0 10px 25px ${cd.status === 'distress' ? 'rgba(255,133,161,0.3)' : 'rgba(77,222,186,0.3)'}` }}>
                {cd.status === 'distress' ? <Bell size={40} /> : <Mic size={40} />}
              </div>
              <div>
                <h3 style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-muted)' }}>ACOUSTIC CLASSIFICATION</h3>
                <div style={{ fontSize: '28px', fontWeight: 900, color: cd.status === 'distress' ? 'var(--secondary)' : 'var(--primary)', marginTop: '4px' }}>{cd.cryType?.toUpperCase() || 'CALM'}</div>
                <div style={{ display: 'flex', gap: '15px', marginTop: '5px', fontSize: '12px', fontWeight: 700 }}>
                  <span style={{ color: 'var(--text-muted)' }}>Confidence: {cd.confidence || 0}%</span>
                  <span style={{ color: 'var(--mint)' }}>Neural Engine Link: Active</span>
                </div>
              </div>
            </div>

            <div className="premium-card" style={{ padding: '30px' }}>
              <h3 style={{ fontWeight: 900, fontSize: '16px', marginBottom: '15px' }}>Security & Events Log</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {al.length > 0 ? al.slice(0, 3).map((a: any, i: number) => (
                  <div key={i} style={{ padding: '12px 20px', background: '#F8FAFC', borderRadius: '14px', fontSize: '13px', fontWeight: 700, borderLeft: '4px solid var(--primary)', display: 'flex', justifyContent: 'space-between' }}>
                    <span>{a.message}</span>
                    <span style={{ opacity: 0.5 }}>{a.timestamp}</span>
                  </div>
                )) : <div style={{ textAlign: 'center', padding: '20px', opacity: 0.4 }}>No active security events</div>}
              </div>
            </div>
          </div>
        </main>

        {/* Apnea Overlay */}
        {isCritical && (
          <div style={{ position: 'fixed', inset: 0, zIndex: 1000, background: 'rgba(255, 133, 161, 0.2)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ padding: '60px 80px', background: 'var(--secondary)', color: 'white', borderRadius: '40px', textAlign: 'center', boxShadow: '0 40px 100px rgba(255,133,161,0.5)', animation: 'fadeUp 0.4s ease-out' }}>
              <AlertCircle size={80} style={{ marginBottom: '20px' }} />
              <h1 style={{ fontSize: '48px', fontWeight: 1000 }}>CRITICAL ALARM</h1>
              <p style={{ fontSize: '20px', fontWeight: 700, opacity: 0.9 }}>APNEA DETECTED: NO BREATHING MOTION</p>
            </div>
          </div>
        )}
      </div>
    );
  } catch (renderError: any) {
    console.error("Dashboard Render Failed:", renderError);
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#FFF1F2' }}>
        <div style={{ textAlign: 'center', maxWidth: '600px' }}>
          <h1 style={{ color: '#E11D48', fontWeight: 900 }}>DASHBOARD RENDER CRASH</h1>
          <pre style={{ background: 'white', padding: '20px', borderRadius: '15px', marginTop: '20px', color: '#64748B', overflow: 'auto' }}>{renderError.message}</pre>
          <button onClick={() => window.location.reload()} className="vibrant-btn" style={{ marginTop: '20px', padding: '15px 30px' }}>RECOVERY REBOOT</button>
        </div>
      </div>
    );
  }
}

// Stats Card Component
function StatCard({ label, value, unit, color, icon, isFlashing }: any) {
  return (
    <div className={`premium-card ${isFlashing ? 'alert-border-flash' : ''}`} style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
      <div style={{ width: '56px', height: '56px', borderRadius: '18px', background: `${color}15`, color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>{icon}</div>
      <div>
        <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{label}</div>
        <div style={{ fontSize: '24px', fontWeight: 900, color }}>{value} <span style={{ fontSize: '12px', fontWeight: 600, opacity: 0.5 }}>{unit}</span></div>
      </div>
    </div>
  );
}

// Waveform Chart Component
function LiveWaveform({ data }: any) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data}>
        <defs>
          <linearGradient id="breathGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
        <XAxis dataKey="time" hide />
        <YAxis hide domain={[0, 'auto']} />
        <Tooltip contentStyle={{ borderRadius: '15px', border: 'none', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }} />
        <Area type="monotone" dataKey="breathing" stroke="var(--primary)" fill="url(#breathGrad)" strokeWidth={4} isAnimationActive={false} />
        <Area type="monotone" dataKey="motion" stroke="var(--lavender)" fill="transparent" strokeWidth={2} strokeDasharray="5 5" isAnimationActive={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// Camera Feed Component
function CameraPreview({ isAlert, isEnabled }: any) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!isEnabled) {
      if (videoRef.current) videoRef.current.srcObject = null;
      return;
    }

    let stream: MediaStream | null = null;
    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (e) { }
    }
    start();

    const loop = setInterval(() => {
      if (videoRef.current && canvasRef.current && stream && isEnabled) {
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) {
          ctx.drawImage(videoRef.current, 0, 0, 640, 480);
          canvasRef.current.toBlob(blob => {
            if (blob) {
              const form = new FormData();
              form.append('file', blob, 'f.jpg');
              fetch(`${API_BASE_URL}/api/process_frame`, { method: 'POST', body: form }).catch(() => { });
            }
          }, 'image/jpeg', 0.5);
        }
      }
    }, 500);

    return () => {
      clearInterval(loop);
      stream?.getTracks().forEach(t => t.stop());
    };
  }, [isEnabled]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', background: '#000', overflow: 'hidden' }}>
      {!isEnabled && (
        <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'white', zIndex: 10, background: 'rgba(0,0,0,0.8)' }}>
          <Camera size={48} opacity={0.3} style={{ marginBottom: '15px' }} />
          <div style={{ fontSize: '12px', fontWeight: 900, letterSpacing: '2px', opacity: 0.5 }}>VISION SYSTEM OFFLINE</div>
        </div>
      )}
      <video ref={videoRef} autoPlay muted playsInline style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: isEnabled ? 0.9 : 0.2 }} />
      <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }} />
      {isEnabled && <div className="scanner" />}
      <div style={{ position: 'absolute', inset: 0, boxShadow: isAlert && isEnabled ? 'inset 0 0 50px rgba(255,133,161,0.5)' : 'none', border: isAlert && isEnabled ? '4px solid var(--secondary)' : 'none', transition: 'all 0.3s' }} />
    </div>
  );
}

// Auth Flow Component
function AuthFlow({ onLogin }: any) {
  const [id, setId] = useState('');
  return (
    <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="premium-card" style={{ width: '450px', padding: '60px', textAlign: 'center' }}>
        <div style={{ fontSize: '60px', marginBottom: '30px' }}>👶</div>
        <h2 style={{ fontSize: '32px', fontWeight: 900, marginBottom: '8px' }}>NEO-CARE</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '40px', fontWeight: 600 }}>Access Clinical Terminal</p>
        <form onSubmit={(e) => { e.preventDefault(); if (id === 'admin') onLogin(); }}>
          <input type="text" placeholder="SECURE ID" value={id} onChange={e => setId(e.target.value)} className="vibrant-input" style={{ width: '100%', marginBottom: '20px', textAlign: 'center' }} />
          <button type="submit" className="vibrant-btn" style={{ width: '100%', height: '60px', fontSize: '18px' }}>INITIALIZE LINK</button>
        </form>
      </div>
    </div>
  );
}

export default App;