# PDF Report Export Feature

## Overview

The neonatal cry detection system now includes professional PDF report generation with AI-powered insights from Google's Gemini API.

## Features

✅ **Professional Medical Reports**: Generate formatted PDF reports with all cry detection data
✅ **AI-Generated Insights**: Gemini API provides analysis and caregiver recommendations
✅ **Complete Data Capture**: Includes cry type, confidence, audio features, and timestamps
✅ **One-Click Export**: Simple button in the UI to download reports
✅ **Graceful Fallback**: Reports generate even if Gemini API is unavailable

## How to Use

### 1. Detect a Cry
- Start the server: `python run_ml_server_3categories.py`
- Open `index.html` in your browser
- Click "Start Listening" to begin cry detection
- Wait for a cry to be detected

### 2. Export PDF Report
- Once a cry is detected, the "Export PDF Report" button will be enabled
- Click the button to generate and download the PDF
- The PDF will include:
  - Detection summary (cry type, confidence, timestamp)
  - Detailed audio parameters
  - AI-generated insights and recommendations
  - Professional medical report formatting

### 3. View the Report
- Open the downloaded PDF in any PDF reader
- Review the analysis and AI insights
- Share with healthcare providers if needed

## API Endpoint

### POST `/api/generate_report`

Generate a PDF report from cry detection data.

**Request Body:**
```json
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
```

**Response:**
- Content-Type: `application/pdf`
- Binary PDF file download

## Configuration

### Gemini API Key

The system uses the Gemini API key for AI insights. The key is configured in the server:

```python
GEMINI_API_KEY = 'AIzaSyDCl6YJQPi2RDwKKLcWHUzI7gcsT9__l10'
```

You can also set it as an environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Technical Details

### Backend Components

1. **gemini_client.py**: Handles Gemini API communication
   - Formats cry data into medical-appropriate prompts
   - Generates AI insights and recommendations
   - Handles API errors gracefully

2. **pdf_report_generator.py**: Creates PDF documents
   - Uses ReportLab for PDF generation
   - Professional medical report styling
   - Includes all detection parameters
   - Adds AI insights when available

3. **Flask Endpoint**: `/api/generate_report`
   - Validates input data
   - Calls Gemini API for insights
   - Generates PDF with all information
   - Returns PDF as downloadable file

### Frontend Components

1. **Export Button** (index.html):
   - Disabled until cry is detected
   - Shows loading state during generation
   - Displays success/error messages

2. **JavaScript Functions** (app.js):
   - `collectCurrentDetectionData()`: Gathers detection data
   - `exportPdfReport()`: Sends request and triggers download
   - `updateCurrentDetectionData()`: Stores latest detection

3. **CSS Styling** (styles.css):
   - Professional button design
   - Loading animations
   - Status message styling

## Error Handling

The system handles errors gracefully:

- **Gemini API Unavailable**: Report generates without AI insights
- **Invalid Data**: Returns descriptive error message
- **Network Errors**: Shows user-friendly error in UI
- **PDF Generation Failure**: Logs error and notifies user

## Dependencies

```bash
pip install reportlab google-generativeai PyPDF2
```

## File Structure

```
Hackthon/Hackthon/
├── gemini_client.py           # Gemini API client
├── pdf_report_generator.py    # PDF generation
├── run_ml_server_3categories.py  # Flask server with endpoint
├── index.html                 # UI with export button
├── app.js                     # Frontend logic
└── styles.css                 # Button styling
```

## Example Report Contents

### Report Header
- Title: "Neonatal Cry Detection Report"
- Generation timestamp

### Detection Summary
- Cry Type: Hunger
- Confidence: 85.5% (High confidence)
- Detection Time: 2026-02-09 14:30:45

### Detailed Audio Parameters
| Parameter | Value | Unit |
|-----------|-------|------|
| Pitch (Mean) | 425.3 | Hz |
| Pitch Variation | 32.1 | Hz |
| Intensity | -25.4 | dB |
| Spectral Centroid | 1850.2 | Hz |
| Zero Crossing Rate | 0.080 | |
| Duration | 2.5 | seconds |

### AI-Generated Insights
*Analysis of the cry pattern, possible causes, recommended responses, and notable audio features*

### Footer
- Disclaimer about AI-generated content
- System version information

## Troubleshooting

### Button is Disabled
- Make sure a cry has been detected first
- Check that the server is running
- Verify browser console for errors

### PDF Generation Fails
- Check server logs for detailed error messages
- Verify Gemini API key is valid
- Ensure all dependencies are installed

### No AI Insights in PDF
- This is normal if Gemini API is unavailable
- Check server logs for Gemini API errors
- Report will still generate with detection data

## Future Enhancements

- [ ] Batch report generation for multiple detections
- [ ] Custom report templates
- [ ] Email delivery of reports
- [ ] Report history and storage
- [ ] Multi-language support

## Support

For issues or questions, check the server logs and browser console for detailed error messages.
