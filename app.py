from collections import deque
import cv2
import mediapipe as mp
import itertools
import copy

from auxillary_functions import process_landmarks, write_csv
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# app constants ####################################################################################

# mediapipe
model_complexity = 0
max_num_hands = 2
min_detection_confidence = 0.5
min_tracking_confidence = 0.5

# model
model_confidence = 0.5
model_path = ''
data_path = 'data/data.csv'
dev_mode = True

# openCV
cap_flip = False
cap_source = 0  # 0 == default device


# video capture ####################################################################################

cap = cv2.VideoCapture(cap_source)

# mediapipe ########################################################################################

hands = mp_hands.Hands(
    model_complexity=model_complexity,
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence,
    max_num_hands=max_num_hands
)

# landmarks queue ##################################################################################

land_q = deque(maxlen=32)

# app ##############################################################################################

label = -1
label_count = 1

while cap.isOpened():
    # capture image process for mediapipe
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue
    if cap_flip:
        image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    # process with mediapipe
    results = hands.process(image)

    # revert image color back
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # capture key imput
    key = cv2.waitKey(10) & 0xFF
    if key == 27:  # esc
        break
    if 48 <= key <= 57:  # 0 - 9
        label = key - 48

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                              results.multi_handedness):

            # process landmarks and save to CSV when in dev_mode
            if dev_mode and label != -1:
                landmarks = process_landmarks(hand_landmarks)
                if len(land_q) == land_q.maxlen:
                    write_csv(label, list(land_q), data_path)
                    label_count += 1
                    label = -1
                    land_q.clear()
                    print(f'done_saving {label_count}st label with id {label}')
                else:
                    land_q.append(landmarks)

            # draw hands
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

    # show capture
    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))


cap.release()
