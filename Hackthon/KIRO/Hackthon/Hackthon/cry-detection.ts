/**
 * Cry Detection Frontend Integration
 * 
 * TypeScript module for integrating the Neonatal Cry Detection System
 * with frontend applications.
 * 
 * API Endpoints:
 * - GET  /api/dashboard - Get complete dashboard data
 * - POST /api/feedback  - Submit caregiver feedback
 */

// ============================================================================
// Type Definitions
// ============================================================================

export interface CryDetectionData {
  status: 'normal' | 'abnormal' | 'distress';
  cryType: string;
  intensity: number;
  duration: number;
  confidence: number;
  lastDetected: string;
  audioWaveform: number[];
}

export interface MotionMonitoringData {
  status: 'SAFE' | 'MONITOR' | 'ALERT';
  stillTime: number;
  motion: number;
  confidence: number;
  alertActive: boolean;
}

export interface SleepPositionData {
  position: string;
  status: string;
  riskLevel: string;
  timeInPosition: number;
  confidence: number;
  recommendations: string;
  positionHistory: Array<{ time: string; position: string }>;
}

export interface BreathingAnalysisData {
  rate: number;
  pattern: string;
  status: string;
  oxygenLevel: number;
  confidence: number;
  irregularities: number;
  trend: string;
}

export interface FaceAnalysisData {
  faceDetected: boolean;
  distressLevel: string;
  emotionalState: string;
  facialMovement: string;
  eyesOpen: boolean;
  mouthOpen: boolean;
  confidence: number;
  alerts: string[];
}

export interface PatientInfo {
  id: string;
  age: string;
  weight: string;
  gestationalAge: string;
  admissionDate: string;
  status: string;
}

export interface AIStatus {
  title: string;
  value: string;
  confidence: number;
  note: string;
  status: string;
}

export interface Vital {
  title: string;
  value: number;
  unit: string;
  normalRange: string;
  status: string;
}

export interface Alert {
  time?: string;
  type: string;
  message?: string;
  description?: string;
  timestamp?: string;
  color?: string;
}

export interface RiskCategory {
  name: string;
  level: string;
  color: string;
}

export interface RiskAssessment {
  overall: 'low' | 'medium' | 'high';
  confidence: number;
  categories: RiskCategory[];
}

export interface TrainingDataPoint {
  epoch: number;
  accuracy: number;
  loss: number;
}

export interface Event {
  time: string;
  type: string;
  description: string;
}

export interface DashboardData {
  motionMonitoring: MotionMonitoringData;
  cryDetection: CryDetectionData;
  sleepPosition: SleepPositionData;
  breathingAnalysis: BreathingAnalysisData;
  faceAnalysis: FaceAnalysisData;
  patient: PatientInfo;
  aiStatus: AIStatus[];
  vitals: Vital[];
  alerts: Alert[];
  riskAssessment: RiskAssessment;
  trainingData: TrainingDataPoint[];
  events: Event[];
}

export interface FeedbackRequest {
  predicted_type: 'hunger' | 'sleep_discomfort' | 'pain_distress' | 'diaper_change' | 'normal_unknown';
  actual_type: 'hunger' | 'sleep_discomfort' | 'pain_distress' | 'diaper_change' | 'normal_unknown';
}

export interface FeedbackResponse {
  status: 'success' | 'error';
  message: string;
  feedback?: {
    predicted_type: string;
    actual_type: string;
    confidence: number;
    timestamp: number;
  };
  error?: string;
}

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE_URL = 'http://127.0.0.1:5000';

const API_ENDPOINTS = {
  dashboard: `${API_BASE_URL}/api/dashboard`,
  feedback: `${API_BASE_URL}/api/feedback`,
  status: `${API_BASE_URL}/`,
} as const;

// ============================================================================
// API Client Class
// ============================================================================

export class CryDetectionAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get complete dashboard data including cry detection, vitals, alerts, etc.
   * 
   * @returns Promise<DashboardData>
   * @throws Error if request fails
   */
  async getDashboardData(): Promise<DashboardData> {
    try {
      const response = await fetch(`${this.baseUrl}/api/dashboard`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: DashboardData = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  /**
   * Get only cry detection data
   * 
   * @returns Promise<CryDetectionData>
   */
  async getCryDetectionData(): Promise<CryDetectionData> {
    const dashboard = await this.getDashboardData();
    return dashboard.cryDetection;
  }

  /**
   * Submit caregiver feedback for cry classification
   * 
   * @param feedback - Feedback data with predicted and actual cry types
   * @returns Promise<FeedbackResponse>
   * @throws Error if request fails
   */
  async submitFeedback(feedback: FeedbackRequest): Promise<FeedbackResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedback),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: FeedbackResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  }

  /**
   * Check if the server is online
   * 
   * @returns Promise<boolean>
   */
  async checkServerStatus(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/`, {
        method: 'GET',
      });
      return response.ok;
    } catch (error) {
      console.error('Server is offline:', error);
      return false;
    }
  }

  /**
   * Get system status information
   * 
   * @returns Promise<any>
   */
  async getSystemStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching system status:', error);
      throw error;
    }
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Format cry type for display
 */
export function formatCryType(cryType: string): string {
  const typeMap: Record<string, string> = {
    'hunger': 'Hunger',
    'sleep_discomfort': 'Sleep Discomfort',
    'pain_distress': 'Pain/Distress',
    'diaper_change': 'Diaper Change',
    'normal_unknown': 'Unknown',
  };
  return typeMap[cryType] || cryType;
}

/**
 * Get color for cry status
 */
export function getCryStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    'normal': '#10b981',    // Green
    'abnormal': '#f59e0b',  // Yellow
    'distress': '#ef4444',  // Red
  };
  return colorMap[status] || '#6b7280'; // Gray default
}

/**
 * Get icon for cry type
 */
export function getCryTypeIcon(cryType: string): string {
  const iconMap: Record<string, string> = {
    'hunger': '🍼',
    'sleep_discomfort': '😴',
    'pain_distress': '⚠️',
    'diaper_change': '🧷',
    'normal_unknown': '❓',
  };
  return iconMap[cryType] || '❔';
}

/**
 * Get severity level for cry type
 */
export function getCrySeverity(cryType: string): 'low' | 'medium' | 'high' {
  if (cryType === 'pain_distress') return 'high';
  if (cryType === 'normal_unknown') return 'low';
  return 'medium';
}

/**
 * Format timestamp to readable string
 */
export function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp * 1000);
  return date.toLocaleTimeString();
}

/**
 * Calculate time ago from timestamp
 */
export function timeAgo(timestamp: number): string {
  const now = Date.now() / 1000;
  const diff = Math.floor(now - timestamp);
  
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

// ============================================================================
// React Hook (Optional)
// ============================================================================

/**
 * Custom React hook for cry detection data
 * 
 * Usage:
 * ```tsx
 * const { data, loading, error, refresh } = useCryDetection();
 * ```
 */
export function useCryDetection(refreshInterval: number = 3000) {
  // This is a template - implement with your React state management
  // Example implementation:
  /*
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const api = new CryDetectionAPI();

  const refresh = async () => {
    try {
      setLoading(true);
      const dashboardData = await api.getDashboardData();
      setData(dashboardData);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  return { data, loading, error, refresh };
  */
}

// ============================================================================
// Export Default Instance
// ============================================================================

export default new CryDetectionAPI();
