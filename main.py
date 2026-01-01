import cv2
import mediapipe as mp
import serial
import time

# ---------- CONFIG ----------
COM_PORT = "COM5"      # change if needed
BAUD_RATE = 9600
CAM_INDEX = 0
# ----------------------------

# Serial connection
arduino = serial.Serial(COM_PORT, BAUD_RATE)
time.sleep(2)

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Camera
cap = cv2.VideoCapture(CAM_INDEX)

finger_tips = [4, 8, 12, 16, 20]

while True:
    success, img = cap.read()
    if not success:
        continue

    # IMPORTANT: flip image to fix right-hand thumb logic
    img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    # Default: all LEDs OFF
    fingers = [0, 0, 0, 0, 0]

    if results.multi_hand_landmarks and results.multi_handedness:
        hand = results.multi_hand_landmarks[0]
        lm = hand.landmark

        # Handedness
        hand_label = results.multi_handedness[0].classification[0].label

        # Thumb (x-axis, handedness aware)
        if hand_label == "Right":
            fingers[0] = 0 if lm[4].x > lm[3].x else 1
        else:  # Left hand
            fingers[0] = 0 if lm[4].x < lm[3].x else 1

        # Other fingers (y-axis)
        for i in range(1, 5):
            fingers[i] = 1 if lm[finger_tips[i]
                                 ].y < lm[finger_tips[i]-2].y else 0

        # Draw landmarks
        mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

    # ALWAYS send data to Arduino
    data = "".join(map(str, fingers))
    arduino.write((data + "\n").encode())

    # Display info
    cv2.putText(
        img,
        f"Finger pattern: {fingers}",
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    cv2.imshow("Hand Gesture Control", img)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
