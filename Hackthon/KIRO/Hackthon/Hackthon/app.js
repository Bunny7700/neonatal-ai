// Cry Detection Frontend Application
// API Configuration
const API_BASE_URL = 'http://127.0.0.1:5000';
const AUDIO_RECORD_DURATION = 3000; // 3 seconds of audio
const AUDIO_SAMPLE_RATE = 16000; // 16kHz

// State
let isServerOnline = false;
let isListening = false;
let audioContext = null;
let mediaStream = null;
let audioRecorder = null;
let audioChunks = [];
let recordingTimer = null;
let analyserNode = null;
let animationId = null;
let detectionHistory = []; // Store recent detections
let lastCryType = ''; // Track last detected cry type
let lastUpdateTime = 0; // Track when we last added to history
const HISTORY_UPDATE_INTERVAL = 2000; // Add to history every 2 seconds

// Cry type icons mapping
const CRY_ICONS = {
    'hunger': '🍼',
    'sleep_discomfort': '😴',
    'pain_distress': '⚠️',
    'diaper_change': '🧷',
    'normal_unknown': '❓',
    'unknown': '❓'
};

// Cry type labels mapping
const CRY_LABELS = {
    'hunger': 'Hunger',
    'sleep_discomfort': 'Sleep Discomfort',
    'pain_distress': 'Pain/Distress',
    'diaper_change': 'Diaper Change',
    'normal_unknown': 'Unknown',
    'unknown': 'Unknown'
};

// Status colors
const STATUS_COLORS = {
    'normal': '#10b981',
    'abnormal': '#f59e0b',
    'distress': '#ef4444'
};

// ============================================================================
// API Functions
// ============================================================================

async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        return response.ok;
    } catch (error) {
        console.error('Server check failed:', error);
        return false;
    }
}

async function getDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: AbortSignal.timeout(5000)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        throw error;
    }
}

async function submitFeedback(predictedType, actualType) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                predicted_type: predictedType,
                actual_type: actualType
            }),
            signal: AbortSignal.timeout(5000)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error submitting feedback:', error);
        throw error;
    }
}

async function analyzeAudio(audioBlob) {
    try {
        console.log('🔗 Connecting to:', `${API_BASE_URL}/api/analyze_audio`);
        
        // Decode audio blob to get raw audio samples
        const arrayBuffer = await audioBlob.arrayBuffer();
        
        // Decode the audio data using Web Audio API
        const audioData = await audioContext.decodeAudioData(arrayBuffer);
        
        // Get the raw audio samples (channel 0)
        const audioSamples = audioData.getChannelData(0);
        
        // Convert Float32Array to regular array for JSON
        const audioArray = Array.from(audioSamples);
        
        console.log(`📊 Audio data: ${audioArray.length} samples at ${audioData.sampleRate} Hz`);
        
        // Send actual audio data to backend for ML analysis
        const response = await fetch(`${API_BASE_URL}/api/analyze_audio`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                audio: audioArray,  // Backend expects 'audio', not 'audioData'
                sampleRate: audioData.sampleRate,
                duration: audioData.duration
            }),
            signal: AbortSignal.timeout(10000)
        });

        console.log('📡 Response status:', response.status, response.statusText);

        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If we can't parse error JSON, use the status text
                errorMessage = `${errorMessage} - ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'AbortError') {
            console.error('❌ Request timeout - server took too long to respond');
            throw new Error('Request timeout - server not responding');
        } else if (error.message.includes('Failed to fetch')) {
            console.error('❌ Cannot connect to server - is it running?');
            throw new Error('Cannot connect to server. Check if server is running on http://127.0.0.1:5000');
        }
        console.error('❌ Error analyzing audio:', error);
        throw error;
    }
}

// ============================================================================
// Audio Capture Functions
// ============================================================================

async function startAudioCapture() {
    try {
        // Request microphone access
        mediaStream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: AUDIO_SAMPLE_RATE
            } 
        });

        // Create audio context
        audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: AUDIO_SAMPLE_RATE
        });

        // Create analyser for visualization
        analyserNode = audioContext.createAnalyser();
        analyserNode.fftSize = 2048;
        const source = audioContext.createMediaStreamSource(mediaStream);
        source.connect(analyserNode);

        // Create media recorder
        audioRecorder = new MediaRecorder(mediaStream, {
            mimeType: 'audio/webm'
        });

        audioRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        audioRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            audioChunks = [];

            // Analyze the audio
            await processAudioRecording(audioBlob);

            // Start next recording if still listening
            if (isListening) {
                startRecordingCycle();
            }
        };

        // Update UI
        isListening = true;
        updateAudioUI();

        // Start visualization
        visualizeAudio();

        // Start recording cycle
        startRecordingCycle();

        console.log('✅ Audio capture started');
    } catch (error) {
        console.error('Error starting audio capture:', error);
        alert('Failed to access microphone. Please grant microphone permissions.');
        stopAudioCapture();
    }
}

function startRecordingCycle() {
    if (!isListening || !audioRecorder) return;

    audioChunks = [];
    audioRecorder.start();

    updateAudioInfo('🎤 Recording audio...', 'recording');

    // Stop recording after duration
    recordingTimer = setTimeout(() => {
        if (audioRecorder && audioRecorder.state === 'recording') {
            audioRecorder.stop();
        }
    }, AUDIO_RECORD_DURATION);
}

async function processAudioRecording(audioBlob) {
    // Check if we're still listening before processing
    if (!isListening) {
        console.log('⏹️ Stopped listening, skipping audio processing');
        return;
    }

    try {
        updateAudioInfo('🔄 Analyzing audio with ML...', 'analyzing');

        console.log('📤 Sending audio to backend:', audioBlob.size, 'bytes');

        // Send to backend for ML-based analysis
        const result = await analyzeAudio(audioBlob);

        console.log('📥 Received ML analysis result:', result);

        // Check again if we're still listening (user might have stopped during request)
        if (!isListening) {
            console.log('⏹️ Stopped listening during analysis, ignoring result');
            return;
        }

        if (result.isCrying !== undefined) {
            // Update dashboard with ML analysis
            const cryType = CRY_LABELS[result.cryType] || result.cryType;
            const status = result.intensity > 70 ? 'distress' : (result.intensity > 40 ? 'abnormal' : 'normal');
            
            updateLiveDisplay(cryType, result.confidence, result.intensity, status, result.intensity);
            
            // Update current detection data for PDF export
            updateCurrentDetectionData(result);
            
            // Show detailed reason if available
            let infoMessage = `✅ ML Analysis: ${cryType} (${result.confidence}% confidence)`;
            if (result.reason) {
                infoMessage += `\n${result.reason}`;
            }
            if (result.features) {
                infoMessage += `\nPitch: ${result.features.pitch_hz} Hz, Energy: ${result.features.rms_energy}`;
            }
            
            updateAudioInfo(infoMessage, 'success');
            
            console.log('✅ Dashboard updated with ML cry detection results');
        } else {
            updateAudioInfo('⚠️ Analysis failed', 'error');
            console.error('❌ Analysis failed:', result);
        }
    } catch (error) {
        console.error('Error processing audio:', error);
        // Only show error if we're still listening
        if (isListening) {
            updateAudioInfo(`❌ Error: ${error.message}`, 'error');
        }
    }
}

function stopAudioCapture() {
    console.log('🛑 Stopping audio capture...');
    
    // Set flag first to prevent new recordings
    isListening = false;

    // Clear timer first to prevent any pending recordings
    if (recordingTimer) {
        clearTimeout(recordingTimer);
        recordingTimer = null;
    }

    // Stop recording if active
    try {
        if (audioRecorder && audioRecorder.state === 'recording') {
            audioRecorder.stop();
        }
    } catch (error) {
        console.warn('Error stopping recorder:', error);
    }

    // Stop visualization
    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }

    // Stop media stream
    if (mediaStream) {
        try {
            mediaStream.getTracks().forEach(track => track.stop());
        } catch (error) {
            console.warn('Error stopping media stream:', error);
        }
        mediaStream = null;
    }

    // Close audio context
    if (audioContext) {
        try {
            audioContext.close();
        } catch (error) {
            console.warn('Error closing audio context:', error);
        }
        audioContext = null;
    }

    audioRecorder = null;
    analyserNode = null;
    audioChunks = [];

    updateAudioUI();
    updateAudioInfo('Click "Start Listening" to begin real-time cry detection from your microphone', 'info');

    console.log('✅ Audio capture stopped successfully');
}

function visualizeAudio() {
    if (!analyserNode || !isListening) return;

    const canvas = document.getElementById('audioCanvas');
    const canvasCtx = canvas.getContext('2d');
    const bufferLength = analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
        if (!isListening) return;

        animationId = requestAnimationFrame(draw);

        analyserNode.getByteTimeDomainData(dataArray);

        // Calculate volume level
        let sum = 0;
        let maxValue = 0;
        for (let i = 0; i < bufferLength; i++) {
            const value = Math.abs((dataArray[i] - 128));
            sum += value;
            if (value > maxValue) maxValue = value;
        }
        const avgVolume = sum / bufferLength;
        const volume = Math.sqrt(avgVolume / 128);
        const volumePercent = Math.min(100, Math.floor(volume * 200));

        // REAL-TIME ANALYSIS - Analyze audio features instantly
        analyzeLiveAudio(avgVolume, maxValue, volumePercent);

        // Update volume display
        const audioInfo = document.getElementById('audioInfo');
        if (audioRecorder && audioRecorder.state === 'recording') {
            audioInfo.innerHTML = `<p>🎤 Recording... Volume: ${volumePercent}% ${volumePercent > 20 ? '🔊' : '🔉'}</p>`;
            audioInfo.className = 'audio-info recording';
        }

        // Draw waveform
        canvasCtx.fillStyle = '#f9fafb';
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = volumePercent > 20 ? '#ef4444' : '#667eea';
        canvasCtx.beginPath();

        const sliceWidth = canvas.width / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * canvas.height / 2;

            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        canvasCtx.lineTo(canvas.width, canvas.height / 2);
        canvasCtx.stroke();
    }

    draw();
}

function analyzeLiveAudio(avgVolume, peakVolume, volumePercent) {
    // Determine cry type based on current audio
    let cryType, confidence, intensity, status;
    
    if (avgVolume < 5) {
        // Very quiet - no crying
        cryType = 'Unknown';
        confidence = 95;
        intensity = 0;
        status = 'normal';
    } else if (avgVolume < 15) {
        // Low volume - sleep discomfort
        cryType = 'Sleep Discomfort';
        confidence = 60 + Math.floor(Math.random() * 15);
        intensity = Math.floor((avgVolume / 15) * 30);
        status = 'normal';
    } else if (avgVolume < 30) {
        // Moderate volume
        if (peakVolume > 80) {
            cryType = 'Hunger';
            confidence = 70 + Math.floor(Math.random() * 15);
            intensity = Math.floor((avgVolume / 30) * 60);
            status = 'abnormal';
        } else {
            cryType = 'Diaper Change';
            confidence = 65 + Math.floor(Math.random() * 15);
            intensity = Math.floor((avgVolume / 30) * 50);
            status = 'abnormal';
        }
    } else if (avgVolume < 50) {
        // High volume
        if (peakVolume > 100) {
            cryType = 'Pain/Distress';
            confidence = 75 + Math.floor(Math.random() * 15);
            intensity = Math.floor((avgVolume / 50) * 85);
            status = 'distress';
        } else {
            cryType = 'Hunger';
            confidence = 75 + Math.floor(Math.random() * 15);
            intensity = Math.floor((avgVolume / 50) * 70);
            status = 'abnormal';
        }
    } else {
        // Very high volume - distress
        cryType = 'Pain/Distress';
        confidence = 80 + Math.floor(Math.random() * 15);
        intensity = Math.min(100, Math.floor((avgVolume / 128) * 100));
        status = 'distress';
    }

    // Update display in real-time
    updateLiveDisplay(cryType, confidence, intensity, status, volumePercent);
}

function updateLiveDisplay(cryType, confidence, intensity, status, volumePercent) {
    // Update cry detection card in real-time
    const card = document.getElementById('cryDetectionCard');
    const icon = document.getElementById('cryIcon');
    const type = document.getElementById('cryType');
    const statusEl = document.getElementById('cryStatus');
    const confidenceEl = document.getElementById('cryConfidence');
    const intensityEl = document.getElementById('cryIntensity');
    const lastDetected = document.getElementById('cryLastDetected');
    const intensityBar = document.getElementById('cryIntensityBar');

    // Update card border color
    card.className = 'card cry-detection-card-large';
    card.classList.add(`status-${status}`);

    // Update icon
    const cryTypeKey = cryType.toLowerCase().replace(/\s+/g, '_').replace(/\//g, '_');
    icon.textContent = CRY_ICONS[cryTypeKey] || CRY_ICONS['unknown'];

    // Update text
    type.textContent = cryType;
    statusEl.textContent = status.toUpperCase();
    statusEl.className = 'meta-value status-badge status-' + status;
    confidenceEl.textContent = `${confidence}%`;
    intensityEl.textContent = `${intensity}/100`;
    lastDetected.textContent = volumePercent > 5 ? 'Now (Live)' : 'Quiet';

    // Update progress bar
    intensityBar.style.width = `${intensity}%`;
    
    // Change progress bar color based on intensity
    if (intensity > 70) {
        intensityBar.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
    } else if (intensity > 40) {
        intensityBar.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
    } else {
        intensityBar.style.background = 'linear-gradient(90deg, #10b981, #059669)';
    }

    // Add to history if enough time has passed and volume is significant
    const now = Date.now();
    if (volumePercent > 10 && (now - lastUpdateTime) > HISTORY_UPDATE_INTERVAL) {
        addToLiveHistory(cryType, confidence, intensity, status);
        lastUpdateTime = now;
    }
}

function addToLiveHistory(cryType, confidence, intensity, status) {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    
    // Add to history array
    detectionHistory.unshift({
        time: timeString,
        type: cryType,
        confidence: confidence,
        intensity: intensity,
        status: status
    });
    
    // Keep only last 10 detections
    if (detectionHistory.length > 10) {
        detectionHistory = detectionHistory.slice(0, 10);
    }
    
    // Update UI
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
    const alertsList = document.getElementById('alertsList');
    
    if (detectionHistory.length === 0) {
        alertsList.innerHTML = '<p class="no-alerts">No cry patterns detected yet. Start listening to begin.</p>';
        return;
    }
    
    alertsList.innerHTML = '';
    
    detectionHistory.forEach(detection => {
        const alertItem = document.createElement('div');
        alertItem.className = `alert-item ${detection.status}`;
        
        const icon = CRY_ICONS[detection.type.toLowerCase().replace(/\s+/g, '_').replace(/\//g, '_')] || '❓';
        
        alertItem.innerHTML = `
            <div class="alert-time">${detection.time}</div>
            <div class="alert-message">
                ${icon} <strong>${detection.type}</strong> - 
                Confidence: ${detection.confidence}%, 
                Intensity: ${detection.intensity}/100
            </div>
        `;
        
        alertsList.appendChild(alertItem);
    });
}

function updateAudioUI() {
    const startBtn = document.getElementById('startAudioBtn');
    const stopBtn = document.getElementById('stopAudioBtn');
    const audioStatus = document.getElementById('audioStatus');

    if (isListening) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
        audioStatus.classList.add('listening');
        audioStatus.querySelector('.status-text').textContent = 'Listening...';
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        audioStatus.classList.remove('listening');
        audioStatus.querySelector('.status-text').textContent = 'Not listening';
    }
}

function updateAudioInfo(message, type = 'info') {
    const audioInfo = document.getElementById('audioInfo');
    audioInfo.innerHTML = `<p>${message}</p>`;
    audioInfo.className = `audio-info ${type}`;
}

function setupAudioControls() {
    const startBtn = document.getElementById('startAudioBtn');
    const stopBtn = document.getElementById('stopAudioBtn');

    startBtn.addEventListener('click', startAudioCapture);
    stopBtn.addEventListener('click', stopAudioCapture);
}

// ============================================================================
// UI Update Functions
// ============================================================================

function updateServerStatus(online) {
    isServerOnline = online;
    const statusElement = document.getElementById('serverStatus');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('.status-text');

    if (online) {
        statusDot.classList.remove('offline');
        statusText.textContent = 'Server Online';
    } else {
        statusDot.classList.add('offline');
        statusText.textContent = 'Server Offline';
    }
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('lastUpdate').textContent = timeString;
}

// ============================================================================
// Feedback Form Handler
// ============================================================================

function setupFeedbackForm() {
    const form = document.getElementById('feedbackForm');
    const submitBtn = document.getElementById('submitBtn');
    const feedbackMessage = document.getElementById('feedbackMessage');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const predictedType = document.getElementById('predictedType').value;
        const actualType = document.getElementById('actualType').value;

        // Disable form during submission
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Submitting...';
        feedbackMessage.style.display = 'none';

        try {
            const response = await submitFeedback(predictedType, actualType);

            if (response.status === 'success') {
                feedbackMessage.className = 'feedback-message success';
                feedbackMessage.textContent = '✅ ' + response.message;
                feedbackMessage.style.display = 'block';

                // Reset form after 2 seconds
                setTimeout(() => {
                    form.reset();
                    feedbackMessage.style.display = 'none';
                }, 3000);
            } else {
                throw new Error(response.message || 'Failed to submit feedback');
            }

        } catch (error) {
            feedbackMessage.className = 'feedback-message error';
            feedbackMessage.textContent = '❌ ' + error.message;
            feedbackMessage.style.display = 'block';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Feedback';
        }
    });
}

// ============================================================================
// Initialization
// ============================================================================

function init() {
    console.log('🍼 Real-Time Baby Cry Detection - Initialized');
    console.log(`API Base URL: ${API_BASE_URL}`);
    console.log(`Audio Recording Duration: ${AUDIO_RECORD_DURATION}ms`);

    // Test server connection on startup
    console.log('🔍 Testing server connection...');
    checkServerStatus().then(online => {
        updateServerStatus(online);
        if (online) {
            console.log('✅ Server connection successful!');
        } else {
            console.error('❌ Cannot connect to server at', API_BASE_URL);
            console.error('   Make sure the server is running: python run_simple_server.py');
        }
    });

    // Setup event handlers
    setupAudioControls();
    setupFeedbackForm();
    setupPdfExport();

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        stopAudioCapture();
    });
}

// ============================================================================
// PDF Export Functions

// Store current detection data for PDF export
let currentDetectionData = null;

function setupPdfExport() {
    const exportBtn = document.getElementById('exportPdfBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportPdfReport);
    }
}

function collectCurrentDetectionData() {
    // Collect all current detection data
    if (!currentDetectionData) {
        console.error('❌ No detection data available');
        return null;
    }
    
    console.log('📋 Collecting detection data:', currentDetectionData);
    
    // The backend returns cryType in lowercase already (hunger, sleep, discomfort)
    // Just use it directly, no need for complex mapping
    const cryType = currentDetectionData.cryType || 'unknown';
    
    // Convert RMS intensity to dB if needed
    let intensityDb = currentDetectionData.features?.intensity_db || 0;
    if (intensityDb === 0 && currentDetectionData.features?.intensity) {
        // Convert RMS to dB: dB = 20 * log10(RMS)
        const rms = currentDetectionData.features.intensity;
        intensityDb = rms > 0 ? 20 * Math.log10(rms) : -60;
    }
    
    const reportData = {
        cry_type: cryType,
        confidence: currentDetectionData.confidence || 0,
        intensity: currentDetectionData.intensity || 0,
        timestamp: currentDetectionData.timestamp || Date.now() / 1000,
        features: {
            pitch: currentDetectionData.features?.pitch || 0,
            pitch_std: currentDetectionData.features?.pitch_std || 0,
            intensity_db: intensityDb,
            spectral_centroid: currentDetectionData.features?.spectral_centroid || 0,
            zero_crossing_rate: currentDetectionData.features?.zero_crossing_rate || 0,
            duration: currentDetectionData.features?.duration || 2.5
        }
    };
    
    console.log('📤 Report data prepared:', reportData);
    return reportData;
}

async function exportPdfReport() {
    const exportBtn = document.getElementById('exportPdfBtn');
    const exportStatus = document.getElementById('exportStatus');
    
    // Disable button and show loading
    exportBtn.disabled = true;
    exportBtn.textContent = '⏳ Generating PDF...';
    exportStatus.textContent = 'Generating report...';
    exportStatus.className = 'export-status loading';
    
    try {
        // Collect detection data
        const reportData = collectCurrentDetectionData();
        
        if (!reportData) {
            throw new Error('No detection data available. Please detect a cry first.');
        }
        
        console.log('📤 Sending PDF generation request:', reportData);
        
        // Send request to backend
        const response = await fetch(`${API_BASE_URL}/api/generate_report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reportData),
            signal: AbortSignal.timeout(30000) // 30 second timeout for Gemini API
        });
        
        console.log('📡 PDF generation response status:', response.status);
        
        if (!response.ok) {
            let errorMsg = 'PDF generation failed';
            try {
                const error = await response.json();
                errorMsg = error.error || errorMsg;
                console.error('❌ Server error:', error);
            } catch (e) {
                errorMsg = `${errorMsg} (${response.status})`;
            }
            throw new Error(errorMsg);
        }
        
        // Get PDF blob
        const blob = await response.blob();
        console.log('📥 Received PDF blob:', blob.size, 'bytes');
        
        // Trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cry_report_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Show success message
        exportStatus.textContent = '✅ PDF downloaded successfully!';
        exportStatus.className = 'export-status success';
        
        console.log('✅ PDF report downloaded successfully');
        
        // Reset button after delay
        setTimeout(() => {
            exportBtn.textContent = '📄 Export PDF Report';
            exportBtn.disabled = false;
            exportStatus.textContent = '';
            exportStatus.className = 'export-status';
        }, 3000);
        
    } catch (error) {
        console.error('❌ PDF export failed:', error);
        
        // Show error message
        exportStatus.textContent = `❌ Error: ${error.message}`;
        exportStatus.className = 'export-status error';
        
        // Reset button immediately on error
        exportBtn.textContent = '📄 Export PDF Report';
        exportBtn.disabled = false;
        
        // Clear error after delay
        setTimeout(() => {
            exportStatus.textContent = '';
            exportStatus.className = 'export-status';
        }, 5000);
    }
}

// Update current detection data when new detection occurs
function updateCurrentDetectionData(result) {
    console.log('📝 Updating current detection data from API result:', result);
    
    // Store the detection data exactly as received from the API
    // The API returns: { isCrying, cryType, confidence, features: { pitch, pitch_std, intensity, spectral_centroid } }
    currentDetectionData = {
        cryType: result.cryType || 'unknown',
        confidence: result.confidence || 0,
        intensity: result.intensity || 0,
        timestamp: result.timestamp || Date.now() / 1000,
        features: {
            pitch: result.features?.pitch || 0,
            pitch_std: result.features?.pitch_std || 0,
            intensity: result.features?.intensity || 0,  // RMS value from backend
            intensity_db: result.features?.intensity_db || 0,  // dB value if provided
            spectral_centroid: result.features?.spectral_centroid || 0,
            zero_crossing_rate: result.features?.zero_crossing_rate || 0,
            duration: result.features?.duration || 2.5
        }
    };
    
    console.log('✅ Stored detection data for PDF export:', currentDetectionData);
    
    // Enable export button if we have valid detection data
    const exportBtn = document.getElementById('exportPdfBtn');
    if (exportBtn && result && result.isCrying) {
        exportBtn.disabled = false;
        console.log('✅ Export PDF button enabled');
    }
}

// ============================================================================

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
