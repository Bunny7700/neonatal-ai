# Implementation Plan: Neonatal Cry Detection and Classification

## Overview

This implementation plan extends the existing cry detection system in `Hackthon/Hackthon/` with enhanced audio preprocessing, comprehensive feature extraction, multi-class cry classification, rich alert generation, and caregiver feedback collection. The implementation builds on the existing YAMNet-based detection while maintaining backward compatibility with `main.py` and `shared_data.py`.

## Tasks

- [x] 1. Set up project dependencies and testing framework
  - Add required libraries to `requirements.txt`: librosa, scipy, hypothesis, pytest
  - Install dependencies and verify imports work correctly
  - Set up pytest configuration for unit and property-based tests
  - _Requirements: All (foundation for implementation)_

- [ ] 2. Implement Audio Preprocessing Module
  - [x] 2.1 Create `audio_preprocessor.py` with AudioPreprocessor class
    - Implement noise reduction using spectral subtraction
    - Implement audio segmentation based on energy thresholds
    - Implement amplitude normalization to [-1, 1] range
    - Implement main `preprocess()` method that chains all operations
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 2.2 Write property test for noise reduction effectiveness
    - **Property 2: Noise Reduction Effectiveness**
    - **Validates: Requirements 2.1**

  - [ ]* 2.3 Write property test for silence segmentation
    - **Property 3: Silence Segmentation**
    - **Validates: Requirements 2.2**

  - [ ]* 2.4 Write property test for audio normalization range
    - **Property 4: Audio Normalization Range**
    - **Validates: Requirements 2.3**

  - [ ]* 2.5 Write property test for preprocessing performance
    - **Property 5: Preprocessing Performance**
    - **Validates: Requirements 2.5**

  - [ ]* 2.6 Write unit tests for edge cases
    - Test empty audio (silence)
    - Test very short audio (< 100ms)
    - Test audio with NaN/Inf values
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 3. Implement Feature Extraction Module
  - [x] 3.1 Create `feature_extractor.py` with FeatureExtractor class
    - Implement pitch extraction using autocorrelation or librosa
    - Implement frequency spectrum analysis
    - Implement intensity (RMS energy) calculation
    - Implement MFCC extraction (13 coefficients)
    - Implement duration calculation
    - Implement `extract_all_features()` returning complete feature dictionary
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]* 3.2 Write property test for complete feature extraction
    - **Property 6: Complete Feature Extraction**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

  - [ ]* 3.3 Write unit tests for feature extraction edge cases
    - Test feature extraction on silence
    - Test feature extraction on very loud audio
    - Test feature extraction on extreme pitch audio
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Checkpoint - Verify preprocessing and feature extraction
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Cry Classification Module
  - [x] 5.1 Create `cry_classifier.py` with CryClassifier class
    - Load YAMNet model for initial cry detection
    - Implement feature-based cry type classifier (Random Forest or small neural network)
    - Implement confidence thresholding logic (< 60% → normal_unknown)
    - Implement `detect_cry()` method using YAMNet
    - Implement `classify_cry_type()` method for 5-category classification
    - Implement main `predict()` method combining detection and classification
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ]* 5.2 Write property test for valid cry classification categories
    - **Property 7: Valid Cry Classification Categories**
    - **Validates: Requirements 4.1**

  - [ ]* 5.3 Write property test for confidence score range
    - **Property 8: Confidence Score Range**
    - **Validates: Requirements 4.2**

  - [ ]* 5.4 Write property test for low confidence classification
    - **Property 9: Low Confidence Classification**
    - **Validates: Requirements 4.3, 10.3**

  - [ ]* 5.5 Write property test for high confidence classification
    - **Property 10: High Confidence Classification**
    - **Validates: Requirements 4.4**

  - [ ]* 5.6 Write property test for classification performance
    - **Property 11: Classification Performance**
    - **Validates: Requirements 4.5**

  - [ ]* 5.7 Write unit tests for classification edge cases
    - Test confidence scores at exact thresholds (59.9%, 60.0%, 60.1%)
    - Test model loading failure handling
    - Test inference timeout handling
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 6. Implement Alert Management Module
  - [x] 6.1 Create `alert_manager.py` with AlertManager class
    - Implement cry type to message mapping for all 5 categories
    - Implement cry type to color code mapping (red, yellow, green)
    - Implement cry type to icon mapping
    - Implement `generate_alert()` method returning complete alert structure
    - Implement `update_dashboard()` method to update shared_data
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.9_

  - [ ]* 6.2 Write property test for alert message mapping
    - **Property 12: Alert Message Mapping**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

  - [ ]* 6.3 Write property test for complete alert structure
    - **Property 13: Complete Alert Structure**
    - **Validates: Requirements 5.6, 5.7, 5.9**

  - [ ]* 6.4 Write property test for dashboard update completeness
    - **Property 19: Dashboard Update Completeness**
    - **Validates: Requirements 11.2**

  - [ ]* 6.5 Write unit tests for alert generation
    - Test each cry type generates correct message
    - Test color coding for each severity level
    - Test alert structure completeness
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.9_

- [ ] 7. Implement Feedback System Module
  - [x] 7.1 Create `feedback_system.py` with FeedbackSystem class
    - Implement feedback storage to JSON files (features + labels only, no raw audio)
    - Implement `record_feedback()` method
    - Implement `get_feedback_data()` method for retrieval
    - Implement `export_feedback()` method for model retraining
    - _Requirements: 6.3, 6.4_

  - [ ]* 7.2 Write property test for feedback data completeness
    - **Property 14: Feedback Data Completeness**
    - **Validates: Requirements 6.3**

  - [ ]* 7.3 Write property test for feedback retrieval
    - **Property 15: Feedback Retrieval**
    - **Validates: Requirements 6.4**

  - [ ]* 7.4 Write property test for feedback privacy
    - **Property 17: Feedback Privacy**
    - **Validates: Requirements 8.3**

  - [ ]* 7.5 Write unit tests for feedback system
    - Test feedback storage with complete data
    - Test feedback retrieval
    - Test disk full error handling
    - Test that no raw audio is stored
    - _Requirements: 6.3, 6.4, 8.3_

- [x] 8. Checkpoint - Verify all modules work independently
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Integrate modules into enhanced CryDetector
  - [x] 9.1 Update `cry_detection_yamnet.py` to use new modules
    - Import and instantiate AudioPreprocessor, FeatureExtractor, CryClassifier, AlertManager, FeedbackSystem
    - Update `detect()` method to use full pipeline: capture → preprocess → extract → classify → alert
    - Maintain backward compatibility with existing return format
    - Add error handling for each pipeline stage
    - Implement raw audio disposal after processing
    - _Requirements: 1.1, 1.3, 1.4, 2.4, 8.2, 11.1, 11.2, 11.3, 11.4_

  - [ ]* 9.2 Write property test for audio buffer segmentation
    - **Property 1: Audio Buffer Segmentation**
    - **Validates: Requirements 1.3**

  - [ ]* 9.3 Write property test for raw audio disposal
    - **Property 16: Raw Audio Disposal**
    - **Validates: Requirements 8.2**

  - [ ]* 9.4 Write integration tests for full pipeline
    - Test audio capture → preprocessing → feature extraction → classification → alert
    - Test integration with shared_data dashboard updates
    - Test error handling at each stage
    - Test that system continues operating after errors
    - _Requirements: 1.1, 1.3, 1.4, 2.4, 11.2, 11.4_

- [ ] 10. Add API endpoints for feedback collection
  - [x] 10.1 Add feedback endpoint to `main.py`
    - Create POST `/api/feedback` endpoint accepting predicted_type and actual_type
    - Call FeedbackSystem.record_feedback() with current features
    - Return success/error response
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ]* 10.2 Write unit tests for feedback API
    - Test successful feedback submission
    - Test feedback with invalid cry types
    - Test feedback storage failure handling
    - _Requirements: 6.3_

- [ ] 11. Implement privacy and performance features
  - [x] 11.1 Add privacy safeguards
    - Verify no raw audio is transmitted over network
    - Verify raw audio is cleared from memory after processing
    - Add logging to confirm audio disposal
    - _Requirements: 8.1, 8.2_

  - [x] 11.2 Add battery management (optional for MVP)
    - Detect battery level using platform-specific APIs
    - Reduce sampling frequency when battery < 15%
    - Enter low-power mode when battery < 5%
    - _Requirements: 9.2, 9.3_

  - [ ]* 11.3 Write property test for noise robustness
    - **Property 18: Noise Robustness**
    - **Validates: Requirements 10.4**

  - [ ]* 11.4 Write unit tests for privacy features
    - Test that no raw audio is in network requests
    - Test that raw audio is cleared after processing
    - _Requirements: 8.1, 8.2_

  - [ ]* 11.5 Write unit tests for battery management
    - Test battery threshold behaviors (15%, 5%)
    - Test battery detection failure handling
    - _Requirements: 9.2, 9.3_

- [ ] 12. Model training and validation
  - [x] 12.1 Prepare training data
    - Collect or download infant cry dataset (e.g., Baby Chillanto database)
    - Label samples into 5 categories
    - Split into train/validation/test sets
    - _Requirements: 10.1, 10.2_

  - [x] 12.2 Train cry type classifier
    - Extract features from training data using FeatureExtractor
    - Train Random Forest or small neural network on features
    - Tune hyperparameters for accuracy and performance
    - Save trained model to file
    - _Requirements: 4.1, 10.1_

  - [ ]* 12.3 Validate model performance
    - Test model accuracy on validation set (target: ≥ 75%)
    - Test pain/distress recall (target: ≥ 85%)
    - Test noise robustness at various SNR levels
    - _Requirements: 10.1, 10.2, 10.4_

- [ ] 13. Final integration and testing
  - [x] 13.1 Update `main.py` to use enhanced CryDetector
    - Verify `run_cry_detection()` thread works with new implementation
    - Verify dashboard updates with new alert structure
    - Verify alerts are added correctly
    - Test full system startup and shutdown
    - _Requirements: 11.1, 11.2, 11.4, 11.5_

  - [ ]* 13.2 Run full integration test suite
    - Test complete system with real audio samples
    - Test concurrent operation with motion detection
    - Test system behavior under various error conditions
    - Measure end-to-end latency (target: < 2 seconds)
    - _Requirements: 7.2, 11.1, 11.2, 11.4_

  - [ ]* 13.3 Performance and load testing
    - Test continuous operation for extended periods
    - Measure CPU and memory usage
    - Verify no memory leaks
    - Test battery consumption (if possible)
    - _Requirements: 7.3, 9.1, 9.4_

- [x] 14. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- The implementation extends existing code in `Hackthon/Hackthon/` folder
- Model training (task 12) can use pre-trained models initially and be refined later
- Battery management (task 11.2) is optional for desktop/server deployment
