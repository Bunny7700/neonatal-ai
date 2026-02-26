# Design Document: PDF Report Generation

## Overview

This design document specifies the implementation of a PDF report generation feature for the neonatal cry detection system. The feature will create professional medical-style reports from cry detection data, enhanced with AI-generated insights from Google's Gemini API. The system will integrate seamlessly with the existing Python backend and web-based frontend, providing caregivers with downloadable, shareable documentation of cry detection events.

The implementation will use Python's ReportLab library for PDF generation, integrate with the Gemini API for AI insights, and add a frontend export button that triggers the report generation and download process.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Browser)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Cry Detection UI                                      │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  [Export PDF] Button                             │ │ │
│  │  │  - Collects current detection data               │ │ │
│  │  │  - Sends to backend                              │ │ │
│  │  │  - Triggers download on response                 │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP POST /api/generate_report
                           │ { cry_detection_data }
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Flask Server)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Report Generation Endpoint                            │ │
│  │  - Validates input data                                │ │
│  │  - Orchestrates report generation                      │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                            │
│                 ▼                                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Gemini API Client                                     │ │
│  │  - Formats cry data for Gemini                         │ │
│  │  - Requests AI insights                                │ │
│  │  - Handles API errors gracefully                       │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                            │
│                 ▼                                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  PDF Generator                                         │ │
│  │  - Creates PDF document structure                      │ │
│  │  - Formats medical report layout                       │ │
│  │  - Includes all detection parameters                   │ │
│  │  - Adds AI insights section                            │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                            │
│                 ▼                                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Response Handler                                      │ │
│  │  - Returns PDF as binary stream                        │ │
│  │  - Sets appropriate headers                            │ │
│  │  - Cleans up temporary files                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Gemini API     │
                  │  (External)     │
                  └─────────────────┘
```

### Data Flow

1. **User Action**: User clicks "Export PDF" button in the frontend
2. **Data Collection**: Frontend gathers current cry detection data (type, confidence, features, timestamp)
3. **API Request**: Frontend sends POST request to `/api/generate_report` with detection data
4. **Backend Processing**:
   - Validates incoming data
   - Sends cry data to Gemini API for insights
   - Generates PDF document with all information
   - Returns PDF as binary response
5. **Frontend Download**: Browser receives PDF and triggers download to user's device

## Components and Interfaces

### 1. Frontend Export Button Component

**Location**: `Hackthon/Hackthon/index.html` and `Hackthon/Hackthon/app.js`

**HTML Structure**:
```html
<button id="exportPdfBtn" class="btn-export">
    📄 Export PDF Report
</button>
```

**JavaScript Interface**:
```javascript
async function exportPdfReport() {
    // Collect current detection data
    const reportData = {
        cry_type: currentCryType,
        confidence: currentConfidence,
        intensity: currentIntensity,
        timestamp: currentTimestamp,
        features: {
            pitch: currentPitch,
            pitch_std: currentPitchStd,
            intensity_db: currentIntensityDb,
            spectral_centroid: currentSpectralCentroid,
            zero_crossing_rate: currentZCR,
            duration: currentDuration
        }
    };
    
    // Send to backend
    const response = await fetch(`${API_BASE_URL}/api/generate_report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportData)
    });
    
    // Trigger download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cry_report_${Date.now()}.pdf`;
    a.click();
}
```

### 2. Backend Report Generation Endpoint

**Location**: New file `Hackthon/Hackthon/pdf_report_generator.py`

**Flask Endpoint**:
```python
@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """
    Generate PDF report from cry detection data
    
    Request Body:
    {
        "cry_type": "hunger",
        "confidence": 85.5,
        "intensity": 65,
        "timestamp": 1234567890,
        "features": {
            "pitch": 425.3,
            "pitch_std": 32.1,
            "intensity_db": -25.4,
            "spectral_centroid": 1850.2,
            "zero_crossing_rate": 0.08,
            "duration": 2.5
        }
    }
    
    Response: PDF file (application/pdf)
    """
```

### 3. Gemini API Client

**Class**: `GeminiInsightsClient`

**Interface**:
```python
class GeminiInsightsClient:
    def __init__(self, api_key: str):
        """Initialize with Gemini API key"""
        
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
```

**API Request Format**:
```python
{
    "contents": [{
        "parts": [{
            "text": """Analyze this infant cry detection data and provide insights:
            
            Cry Type: {cry_type}
            Confidence: {confidence}%
            Audio Features:
            - Pitch: {pitch} Hz
            - Pitch Variation: {pitch_std} Hz
            - Intensity: {intensity_db} dB
            - Spectral Centroid: {spectral_centroid} Hz
            - Duration: {duration} seconds
            
            Please provide:
            1. Analysis of the cry pattern
            2. Possible causes and interpretations
            3. Recommended caregiver responses
            4. Any notable patterns in the audio features
            
            Keep the language clear and appropriate for caregivers."""
        }]
    }]
}
```

### 4. PDF Generator Component

**Class**: `CryReportPDFGenerator`

**Interface**:
```python
class CryReportPDFGenerator:
    def __init__(self):
        """Initialize PDF generator with styling configuration"""
        
    def generate_report(
        self,
        cry_data: Dict[str, Any],
        ai_insights: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF report from cry detection data
        
        Args:
            cry_data: Dictionary containing all detection parameters
            ai_insights: Optional AI-generated insights from Gemini
            
        Returns:
            PDF document as bytes
        """
```

## Data Models

### Cry Detection Data Model

```python
@dataclass
class CryDetectionData:
    """Complete cry detection data for report generation"""
    
    # Classification results
    cry_type: str  # One of: hunger, sleep, discomfort
    confidence: float  # 0-100
    intensity: int  # 0-100
    timestamp: float  # Unix timestamp
    
    # Audio features
    features: AudioFeatures
    
    # Optional metadata
    detection_confidence: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CryDetectionData':
        """Create from dictionary (from API request)"""
        
    def validate(self) -> bool:
        """Validate all fields are present and within valid ranges"""

@dataclass
class AudioFeatures:
    """Audio feature measurements"""
    
    pitch: float  # Hz
    pitch_std: float  # Hz (variation)
    intensity_db: float  # dB
    spectral_centroid: float  # Hz
    spectral_rolloff: Optional[float] = None  # Hz
    zero_crossing_rate: float = 0.0
    duration: float = 0.0  # seconds
    rms_energy: Optional[float] = None
```

### PDF Report Structure Model

```python
@dataclass
class ReportSection:
    """Represents a section in the PDF report"""
    
    title: str
    content: List[str]  # Paragraphs or bullet points
    style: str  # 'heading', 'body', 'table', 'bullet'

class PDFReport:
    """Complete PDF report structure"""
    
    def __init__(self):
        self.sections: List[ReportSection] = []
        self.metadata: Dict[str, Any] = {}
        
    def add_header(self, title: str, timestamp: datetime):
        """Add report header with title and generation time"""
        
    def add_summary_section(self, cry_data: CryDetectionData):
        """Add detection summary section"""
        
    def add_parameters_section(self, cry_data: CryDetectionData):
        """Add detailed parameters section"""
        
    def add_insights_section(self, insights: str):
        """Add AI-generated insights section"""
        
    def add_footer(self):
        """Add report footer with disclaimers"""
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Complete Report Structure

*For any* valid cry detection data, the generated PDF SHALL contain all required sections (header with title and timestamp, detection summary, detailed parameters with all prediction data, and footer) and all prediction parameters (cry type, confidence, timestamp, and all audio features).

**Validates: Requirements 1.1, 1.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3**

### Property 2: All Audio Features Included

*For any* cry detection data with N audio features, the generated PDF SHALL include all N features in the detailed parameters section with their values.

**Validates: Requirements 3.4**

### Property 3: Gemini API Failure Resilience

*For any* cry detection data, if the Gemini API request fails, the PDF generation SHALL complete successfully without AI insights and SHALL log the error.

**Validates: Requirements 2.3, 8.1**

### Property 4: Valid PDF Output

*For any* generated report, the output SHALL be a valid PDF file that starts with the PDF magic number (%PDF) and can be parsed by standard PDF libraries.

**Validates: Requirements 1.5**

### Property 5: Timestamp Formatting Consistency

*For any* timestamp value, the PDF SHALL format it in a human-readable format (YYYY-MM-DD HH:MM:SS) in the report header and detection details.

**Validates: Requirements 6.4**

### Property 6: Confidence Score Precision

*For any* confidence score value, the PDF SHALL display it with exactly one decimal place (e.g., 85.5%).

**Validates: Requirements 3.5**

### Property 7: Data Privacy in API Requests

*For any* Gemini API request, the request payload SHALL NOT contain personally identifiable information fields (name, email, phone, address) beyond the cry detection parameters.

**Validates: Requirements 7.1**

### Property 8: Temporary File Cleanup

*For any* PDF generation request, all temporary files created during generation SHALL be deleted after the response is sent, leaving no orphaned files.

**Validates: Requirements 7.4**

### Property 9: Error Message Descriptiveness

*For any* error condition (invalid input, API failure, PDF generation failure), the error response SHALL contain a descriptive message with at least 10 characters indicating the specific failure reason.

**Validates: Requirements 8.2, 8.4**

### Property 10: Frontend Download Trigger

*For any* successful PDF generation response, the frontend SHALL automatically trigger a file download with a filename matching the pattern "cry_report_[timestamp].pdf".

**Validates: Requirements 5.3**

## Error Handling

### Input Validation Errors

**Scenario**: Invalid or missing cry detection data in request

**Handling**:
- Validate all required fields are present
- Check value ranges (confidence 0-100, valid cry types)
- Return HTTP 400 with descriptive error message
- Log validation failure details

**Example Response**:
```json
{
    "error": "Invalid cry detection data",
    "details": "Missing required field: cry_type",
    "status": 400
}
```

### Gemini API Errors

**Scenario**: Gemini API request fails (timeout, rate limit, authentication error)

**Handling**:
- Catch all API exceptions
- Log error with full details
- Continue PDF generation without AI insights
- Include note in PDF: "AI insights unavailable at generation time"
- Return successful PDF response

**Fallback Behavior**:
```python
try:
    insights = gemini_client.generate_insights(cry_data)
except GeminiAPIError as e:
    logger.error(f"Gemini API failed: {e}")
    insights = None  # Continue without insights
```

### PDF Generation Errors

**Scenario**: ReportLab fails to generate PDF (memory error, invalid data)

**Handling**:
- Catch PDF generation exceptions
- Log full error details and stack trace
- Return HTTP 500 with error message
- Clean up any partial files

**Example Response**:
```json
{
    "error": "PDF generation failed",
    "details": "Internal error during report creation",
    "status": 500
}
```

### File System Errors

**Scenario**: Cannot write temporary files or clean up after generation

**Handling**:
- Use try-finally blocks to ensure cleanup
- Log file system errors
- Continue operation if cleanup fails (don't block response)
- Implement periodic cleanup job for orphaned files

### Frontend Network Errors

**Scenario**: Network request fails or times out

**Handling**:
- Show user-friendly error message
- Provide retry button
- Log error to console
- Don't leave UI in loading state

**Example UI Message**:
```
"Failed to generate PDF report. Please check your connection and try again."
[Retry Button]
```

## Testing Strategy

### Unit Testing

**Test Framework**: pytest for Python backend, Jest for JavaScript frontend

**Backend Unit Tests** (`test_pdf_report_generator.py`):

1. **Test PDF Structure**:
   - Verify all sections are created
   - Check header contains title and timestamp
   - Validate footer is present

2. **Test Data Formatting**:
   - Verify confidence scores formatted to 1 decimal
   - Check timestamp conversion to readable format
   - Validate cry type labels are human-readable

3. **Test Input Validation**:
   - Test with missing required fields
   - Test with out-of-range values
   - Test with invalid cry types

4. **Test Gemini Client**:
   - Mock API responses
   - Test request formatting
   - Test error handling

5. **Test Error Conditions**:
   - Test with invalid audio features
   - Test with missing optional fields
   - Test cleanup on errors

**Frontend Unit Tests** (`test_pdf_export.js`):

1. **Test Data Collection**:
   - Verify all current detection data is gathered
   - Check feature object construction
   - Validate timestamp generation

2. **Test Download Trigger**:
   - Mock fetch response with blob
   - Verify download link creation
   - Check filename format

3. **Test Error Handling**:
   - Test network error display
   - Test retry functionality
   - Verify loading state management

### Property-Based Testing

**Test Framework**: Hypothesis (Python)

**Configuration**: Minimum 100 iterations per property test

**Property Test 1: PDF Generation Completeness**
```python
@given(cry_detection_data=st.builds(CryDetectionData, ...))
def test_pdf_contains_all_sections(cry_detection_data):
    """
    Feature: pdf-report-generation, Property 1:
    For any valid cry detection data, the generated PDF SHALL contain
    all required sections.
    """
    pdf_bytes = generator.generate_report(cry_detection_data.to_dict())
    pdf_text = extract_text_from_pdf(pdf_bytes)
    
    assert "Neonatal Cry Detection Report" in pdf_text
    assert "Detection Summary" in pdf_text
    assert "Detailed Parameters" in pdf_text
    assert "Report generated on" in pdf_text
```

**Property Test 2: Parameter Inclusion Completeness**
```python
@given(cry_detection_data=st.builds(CryDetectionData, ...))
def test_all_features_included(cry_detection_data):
    """
    Feature: pdf-report-generation, Property 2:
    For any cry detection data with N features, the generated PDF SHALL
    include all N features.
    """
    pdf_bytes = generator.generate_report(cry_detection_data.to_dict())
    pdf_text = extract_text_from_pdf(pdf_bytes)
    
    features = cry_detection_data.features
    assert f"Pitch: {features.pitch}" in pdf_text
    assert f"Pitch Variation: {features.pitch_std}" in pdf_text
    assert f"Intensity: {features.intensity_db}" in pdf_text
    assert f"Spectral Centroid: {features.spectral_centroid}" in pdf_text
```

**Property Test 3: Gemini API Failure Resilience**
```python
@given(cry_detection_data=st.builds(CryDetectionData, ...))
def test_pdf_generation_without_gemini(cry_detection_data):
    """
    Feature: pdf-report-generation, Property 3:
    For any cry detection data, if Gemini API fails, PDF generation
    SHALL complete successfully.
    """
    # Mock Gemini API to raise error
    with patch.object(gemini_client, 'generate_insights', side_effect=GeminiAPIError):
        pdf_bytes = generator.generate_report(cry_detection_data.to_dict())
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        # Verify it's a valid PDF
        assert pdf_bytes[:4] == b'%PDF'
```

**Property Test 4: Valid PDF Output**
```python
@given(cry_detection_data=st.builds(CryDetectionData, ...))
def test_valid_pdf_output(cry_detection_data):
    """
    Feature: pdf-report-generation, Property 4:
    For any generated report, the output SHALL be a valid PDF file.
    """
    pdf_bytes = generator.generate_report(cry_detection_data.to_dict())
    
    # Check PDF magic number
    assert pdf_bytes[:4] == b'%PDF'
    
    # Verify can be opened by PyPDF2
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    assert len(pdf_reader.pages) > 0
```

**Property Test 5: Timestamp Formatting Consistency**
```python
@given(timestamp=st.floats(min_value=0, max_value=2e9))
def test_timestamp_formatting(timestamp):
    """
    Feature: pdf-report-generation, Property 5:
    For any timestamp value, the PDF SHALL format it in human-readable format.
    """
    cry_data = create_cry_data_with_timestamp(timestamp)
    pdf_bytes = generator.generate_report(cry_data.to_dict())
    pdf_text = extract_text_from_pdf(pdf_bytes)
    
    # Check format matches YYYY-MM-DD HH:MM:SS
    import re
    timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    assert re.search(timestamp_pattern, pdf_text) is not None
```

**Property Test 6: Confidence Score Precision**
```python
@given(confidence=st.floats(min_value=0, max_value=100))
def test_confidence_precision(confidence):
    """
    Feature: pdf-report-generation, Property 6:
    For any confidence score, the PDF SHALL display it with one decimal place.
    """
    cry_data = create_cry_data_with_confidence(confidence)
    pdf_bytes = generator.generate_report(cry_data.to_dict())
    pdf_text = extract_text_from_pdf(pdf_bytes)
    
    # Check confidence appears with exactly 1 decimal place
    import re
    confidence_pattern = rf'{confidence:.1f}%'
    assert confidence_pattern in pdf_text
```

**Property Test 7: Data Privacy in API Requests**
```python
@given(cry_detection_data=st.builds(CryDetectionData, ...))
def test_no_pii_in_gemini_request(cry_detection_data):
    """
    Feature: pdf-report-generation, Property 7:
    For any Gemini API request, the payload SHALL NOT contain PII.
    """
    with patch('requests.post') as mock_post:
        gemini_client.generate_insights(cry_detection_data.to_dict())
        
        request_body = mock_post.call_args[1]['json']
        request_text = str(request_body)
        
        # Verify no common PII fields
        assert 'name' not in request_text.lower()
        assert 'email' not in request_text.lower()
        assert 'phone' not in request_text.lower()
        assert 'address' not in request_text.lower()
```

**Property Test 8: Temporary File Cleanup**
```python
@given(cry_detection_data=st.builds(CryDetectionData, ...))
def test_temp_file_cleanup(cry_detection_data):
    """
    Feature: pdf-report-generation, Property 8:
    For any PDF generation, temporary files SHALL be cleaned up.
    """
    temp_dir = tempfile.gettempdir()
    files_before = set(os.listdir(temp_dir))
    
    pdf_bytes = generator.generate_report(cry_detection_data.to_dict())
    
    files_after = set(os.listdir(temp_dir))
    new_files = files_after - files_before
    
    # No new files should remain
    assert len(new_files) == 0
```

**Property Test 9: Error Message Descriptiveness**
```python
@given(invalid_data=st.dictionaries(st.text(), st.text()))
def test_descriptive_error_messages(invalid_data):
    """
    Feature: pdf-report-generation, Property 9:
    For any error condition, the error response SHALL contain descriptive message.
    """
    try:
        generator.generate_report(invalid_data)
        assert False, "Should have raised validation error"
    except ValueError as e:
        error_message = str(e)
        # Error message should be non-empty and descriptive
        assert len(error_message) > 10
        assert any(word in error_message.lower() for word in ['missing', 'invalid', 'required'])
```

**Property Test 10: Frontend Download Trigger**
```python
# This would be a JavaScript test using Jest
test('download trigger for any successful response', async () => {
    // Mock fetch to return PDF blob
    const mockBlob = new Blob(['fake pdf'], { type: 'application/pdf' });
    global.fetch = jest.fn(() =>
        Promise.resolve({
            ok: true,
            blob: () => Promise.resolve(mockBlob)
        })
    );
    
    // Mock URL.createObjectURL
    const mockUrl = 'blob:mock-url';
    global.URL.createObjectURL = jest.fn(() => mockUrl);
    
    // Mock createElement and click
    const mockLink = { click: jest.fn(), href: '', download: '' };
    document.createElement = jest.fn(() => mockLink);
    
    await exportPdfReport();
    
    // Verify download was triggered
    expect(mockLink.click).toHaveBeenCalled();
    expect(mockLink.download).toMatch(/cry_report_\d+\.pdf/);
});
```

### Integration Testing

**Test Scenarios**:

1. **End-to-End Report Generation**:
   - Start with real cry detection data
   - Call API endpoint
   - Verify PDF is generated and downloadable
   - Check all sections are present

2. **Gemini API Integration**:
   - Test with real Gemini API (in staging)
   - Verify insights are included in PDF
   - Test rate limiting behavior

3. **Frontend Integration**:
   - Test button click triggers API call
   - Verify loading state during generation
   - Check download initiates automatically
   - Test error display on failure

4. **Error Recovery**:
   - Test with Gemini API unavailable
   - Verify PDF still generates
   - Check error is logged but not shown to user

### Manual Testing Checklist

- [ ] Generate PDF with all cry types (hunger, sleep, discomfort)
- [ ] Verify PDF opens in Adobe Reader, Chrome, Firefox
- [ ] Check all sections are properly formatted
- [ ] Verify AI insights are relevant and helpful
- [ ] Test with Gemini API disabled (should still work)
- [ ] Check PDF filename includes timestamp
- [ ] Verify download works on different browsers
- [ ] Test with various confidence levels and feature values
- [ ] Check report is readable and professional-looking
- [ ] Verify no sensitive data leaks in logs or API requests
