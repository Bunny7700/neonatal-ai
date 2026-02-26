# Implementation Plan: PDF Report Generation

## Overview

This implementation plan breaks down the PDF report generation feature into discrete coding tasks. The feature will integrate with the existing Python Flask backend and web frontend to provide professional PDF reports of cry detection data, enhanced with AI insights from Google's Gemini API.

The implementation follows a bottom-up approach: first building core components (Gemini client, PDF generator), then the backend API endpoint, and finally the frontend integration.

## Tasks

- [x] 1. Set up dependencies and project structure
  - Install required Python packages: `reportlab`, `google-generativeai`, `PyPDF2`
  - Create new file `Hackthon/Hackthon/pdf_report_generator.py`
  - Create new file `Hackthon/Hackthon/gemini_client.py`
  - Add Gemini API key to environment configuration
  - _Requirements: 2.4, 7.2_

- [ ] 2. Implement Gemini API client
  - [ ] 2.1 Create GeminiInsightsClient class
    - Implement `__init__` method with API key initialization
    - Implement `generate_insights` method to call Gemini API
    - Format cry detection data into medical-appropriate prompt
    - Handle API responses and extract insights text
    - _Requirements: 2.1, 2.4, 2.5_
  
  - [ ]* 2.2 Write property test for Gemini client
    - **Property 7: Data Privacy in API Requests**
    - **Validates: Requirements 7.1**
    - Test that API requests contain no PII fields
  
  - [ ] 2.3 Implement error handling for Gemini API
    - Create custom `GeminiAPIError` exception class
    - Handle timeout errors, rate limits, authentication failures
    - Log errors with sufficient detail for debugging
    - _Requirements: 2.3, 8.1, 8.5_
  
  - [ ]* 2.4 Write unit tests for Gemini client
    - Test successful API call with mocked response
    - Test error handling for various failure modes
    - Test prompt formatting
    - _Requirements: 2.1, 2.3, 2.5_

- [ ] 3. Implement PDF generator core
  - [ ] 3.1 Create CryReportPDFGenerator class
    - Implement `__init__` with styling configuration
    - Set up ReportLab document template with medical report styling
    - Define fonts, colors, and spacing constants
    - _Requirements: 1.2, 4.5_
  
  - [ ] 3.2 Implement report header generation
    - Create `_add_header` method
    - Include report title "Neonatal Cry Detection Report"
    - Format and include generation timestamp
    - _Requirements: 1.3, 4.1_
  
  - [ ] 3.3 Implement detection summary section
    - Create `_add_summary_section` method
    - Include cry type with descriptive label
    - Include confidence score with interpretation guidance
    - Include detection timestamp in human-readable format
    - _Requirements: 4.2, 6.2, 6.3, 6.4_
  
  - [ ] 3.4 Implement detailed parameters section
    - Create `_add_parameters_section` method
    - Include all audio features (pitch, intensity, spectral features, etc.)
    - Format numerical values with appropriate precision and units
    - Organize in clear table or list format
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.3_
  
  - [ ] 3.5 Implement AI insights section
    - Create `_add_insights_section` method
    - Include Gemini-generated insights when available
    - Add fallback message when insights unavailable
    - _Requirements: 2.2, 4.4_
  
  - [ ] 3.6 Implement report footer
    - Create `_add_footer` method
    - Include disclaimer about AI-generated content
    - Add system information and version
    - _Requirements: 1.4_
  
  - [ ] 3.7 Implement main generate_report method
    - Orchestrate all section generation methods
    - Handle optional AI insights parameter
    - Return PDF as bytes
    - Implement temporary file cleanup
    - _Requirements: 1.1, 1.5, 7.4_

- [ ] 4. Implement data models and validation
  - [ ] 4.1 Create CryDetectionData dataclass
    - Define all required fields (cry_type, confidence, intensity, timestamp, features)
    - Implement `to_dict` and `from_dict` methods
    - Implement `validate` method with range checks
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ] 4.2 Create AudioFeatures dataclass
    - Define all audio feature fields
    - Add type hints and optional fields
    - _Requirements: 3.4_
  
  - [ ]* 4.3 Write property test for data validation
    - **Property 9: Error Message Descriptiveness**
    - **Validates: Requirements 8.2, 8.4**
    - Test that invalid data produces descriptive error messages

- [ ] 5. Checkpoint - Core components complete
  - Ensure all tests pass, ask the user if questions arise.

- [-] 6. Implement Flask API endpoint
  - [x] 6.1 Add /api/generate_report endpoint to Flask server
    - Create POST endpoint in `run_ml_server_3categories.py` or new routes file
    - Parse JSON request body
    - Validate cry detection data
    - _Requirements: 5.2_
  
  - [x] 6.2 Integrate Gemini client in endpoint
    - Initialize GeminiInsightsClient with API key from environment
    - Call `generate_insights` with cry data
    - Handle Gemini API failures gracefully
    - _Requirements: 2.1, 2.3_
  
  - [x] 6.3 Integrate PDF generator in endpoint
    - Initialize CryReportPDFGenerator
    - Call `generate_report` with cry data and insights
    - Return PDF as binary response with appropriate headers
    - _Requirements: 1.1, 1.5_
  
  - [x] 6.4 Implement error handling in endpoint
    - Validate input data and return 400 for invalid requests
    - Handle PDF generation errors and return 500
    - Log all errors appropriately
    - _Requirements: 8.2, 8.4, 8.5_
  
  - [ ]* 6.5 Write integration tests for API endpoint
    - Test successful report generation
    - Test with invalid input data
    - Test with Gemini API failure
    - Test response headers and content type
    - _Requirements: 1.1, 2.3, 8.2_

- [ ] 7. Write property-based tests for PDF generation
  - [ ]* 7.1 Write property test for complete report structure
    - **Property 1: Complete Report Structure**
    - **Validates: Requirements 1.1, 1.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3**
    - Test that all sections and parameters are present
  
  - [ ]* 7.2 Write property test for all audio features included
    - **Property 2: All Audio Features Included**
    - **Validates: Requirements 3.4**
    - Test that all N features appear in PDF
  
  - [ ]* 7.3 Write property test for Gemini failure resilience
    - **Property 3: Gemini API Failure Resilience**
    - **Validates: Requirements 2.3, 8.1**
    - Test PDF generation succeeds when Gemini fails
  
  - [ ]* 7.4 Write property test for valid PDF output
    - **Property 4: Valid PDF Output**
    - **Validates: Requirements 1.5**
    - Test PDF magic number and parseability
  
  - [ ]* 7.5 Write property test for timestamp formatting
    - **Property 5: Timestamp Formatting Consistency**
    - **Validates: Requirements 6.4**
    - Test timestamp format matches YYYY-MM-DD HH:MM:SS
  
  - [ ]* 7.6 Write property test for confidence precision
    - **Property 6: Confidence Score Precision**
    - **Validates: Requirements 3.5**
    - Test confidence displayed with one decimal place
  
  - [ ]* 7.7 Write property test for temporary file cleanup
    - **Property 8: Temporary File Cleanup**
    - **Validates: Requirements 7.4**
    - Test no orphaned files remain after generation

- [ ] 8. Checkpoint - Backend implementation complete
  - Ensure all tests pass, ask the user if questions arise.

- [-] 9. Implement frontend export button
  - [x] 9.1 Add Export PDF button to HTML
    - Add button element in `Hackthon/Hackthon/index.html`
    - Place in cry detection results section
    - Add appropriate styling classes
    - _Requirements: 5.1_
  
  - [x] 9.2 Implement data collection function
    - Create `collectCurrentDetectionData` function in `app.js`
    - Gather cry type, confidence, intensity, timestamp
    - Gather all audio features from current detection
    - _Requirements: 5.2_
  
  - [x] 9.3 Implement PDF export function
    - Create `exportPdfReport` function in `app.js`
    - Send POST request to `/api/generate_report`
    - Handle response as blob
    - Trigger download with timestamped filename
    - _Requirements: 5.2, 5.3_
  
  - [x] 9.4 Add loading state and error handling
    - Show loading indicator during PDF generation
    - Display error message on failure
    - Provide retry button
    - _Requirements: 5.4, 5.5_
  
  - [x] 9.5 Wire up button click handler
    - Add event listener to Export PDF button
    - Call `exportPdfReport` on click
    - Disable button during generation
    - _Requirements: 5.2_

- [ ] 10. Write frontend tests
  - [ ]* 10.1 Write property test for download trigger
    - **Property 10: Frontend Download Trigger**
    - **Validates: Requirements 5.3**
    - Test download triggered for successful responses
  
  - [ ]* 10.2 Write unit tests for data collection
    - Test all detection data is gathered correctly
    - Test feature object construction
    - _Requirements: 5.2_
  
  - [ ]* 10.3 Write unit tests for error handling
    - Test error message display
    - Test loading state management
    - Test retry functionality
    - _Requirements: 5.4, 5.5_

- [x] 11. Add CSS styling for export button
  - Style Export PDF button to match existing UI
  - Add loading spinner animation
  - Style error message display
  - Ensure responsive design
  - _Requirements: 5.1_

- [ ] 12. Final integration and testing
  - [ ] 12.1 Test end-to-end flow
    - Start cry detection
    - Click Export PDF button
    - Verify PDF downloads with correct filename
    - Open PDF and verify all sections present
    - _Requirements: 1.1, 5.3_
  
  - [ ] 12.2 Test with different cry types
    - Generate reports for hunger, sleep, discomfort
    - Verify cry type labels are correct
    - Verify all features are included
    - _Requirements: 3.1, 3.4, 6.2_
  
  - [ ] 12.3 Test error scenarios
    - Test with Gemini API disabled
    - Test with invalid detection data
    - Test with network errors
    - Verify graceful error handling
    - _Requirements: 2.3, 8.1, 8.2_
  
  - [ ] 12.4 Test PDF compatibility
    - Open generated PDFs in Adobe Reader
    - Open in Chrome PDF viewer
    - Open in Firefox PDF viewer
    - Verify formatting is consistent
    - _Requirements: 1.5_

- [ ] 13. Final checkpoint - Feature complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests should run minimum 100 iterations
- Gemini API key should be stored in environment variable `GEMINI_API_KEY`
- PDF generation should use ReportLab library for Python
- Frontend should handle PDF as blob and trigger download via URL.createObjectURL
- All temporary files must be cleaned up after PDF generation
- Error handling should be graceful - PDF generation should succeed even if Gemini fails
