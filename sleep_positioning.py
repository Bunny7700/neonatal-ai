import cv2
import numpy as np
import time
import winsound  # ✅ Windows buzzer

# ---------------- CONFIG ----------------
CAMERA_INDEX = 0
FRAME_SIZE = (64, 64)
MOVEMENT_THRESHOLD = 5000      # adjust during demo
MAX_STILL_TIME = 15            # seconds (hackathon demo)
BEEP_FREQ = 1000               # Hz
BEEP_DURATION = 700            # ms
# ----------------------------------------

cap = cv2.VideoCapture(CAMERA_INDEX)

prev_frame = None
still_start_time = None
alert_triggered = False

print("👶 Smart Neonatal Sleep Monitoring Started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Step 1: Preprocessing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, FRAME_SIZE)

    movement_score = 0
    movement_detected = False

    # Step 2: Movement detection
    if prev_frame is not None:
        diff = cv2.absdiff(gray, prev_frame)
        movement_score = int(diff.sum())

        if movement_score > MOVEMENT_THRESHOLD:
            movement_detected = True

    prev_frame = gray.copy()

    # Step 3: Stillness tracking
    if not movement_detected:
        if still_start_time is None:
            still_start_time = time.time()
    else:
        still_start_time = None
        alert_triggered = False  # ✅ reset alert when motion resumes

    still_duration = 0
    if still_start_time is not None:
        still_duration = time.time() - still_start_time

    # Step 4: Status logic + BEEP
    if still_duration >= MAX_STILL_TIME:
        status = "🚨 ALERT: Prolonged Stillness"
        color = (0, 0, 255)

        if not alert_triggered:
            print("🚨 ALERT TRIGGERED: Baby still for > 15 seconds")
            winsound.Beep(BEEP_FREQ, BEEP_DURATION)  # 🔔 BUZZER
            alert_triggered = True
    else:
        status = "🟢 SAFE: Normal Monitoring"
        color = (0, 255, 0)

    motion_text = "Motion Detected" if movement_detected else "No Motion"

    # Step 5: Display information
    cv2.putText(frame, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.putText(frame, f"Still Time: {int(still_duration)} sec",
                (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (255, 255, 255), 2)

    cv2.putText(frame, f"Motion Score: {movement_score}",
                (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (255, 255, 0), 2)

    cv2.putText(frame, motion_text,
                (10, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 255) if movement_detected else (200, 200, 200), 2)

    cv2.imshow("Smart Neonatal Sleep Monitoring", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
