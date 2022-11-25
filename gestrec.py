import joblib
from collections import deque
import cv2
import mediapipe as mp
import numpy as np
from multiprocessing import Process, current_process, parent_process, Lock
from threading import Thread
import sys

from auxillary_funcs.ml import get_nearest_hand, preprocess_landmarks, write_csv, read_labels, bounding_rect
from auxillary_funcs.interprocess_comms import get_conn_listener, get_conn_client, MSG_GESTREC_OFF, MSG_GESTREC_ON, GESTREC_PORT
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


_GESTREC_ON = 'gestrecon'
_GESTREC_OFF = 'gestrecoff'

_procs = []


class Gestrec():

    def __init__(self) -> None:
        # mediapipe
        self.mediapipe_model_complexity = 1
        self.mediapipe_min_detection_confidence = 0.5
        self.mediapipe_min_tracking_confidence = 0.5

        # model
        self.model_min_confidence = 0.5
        self.model_path = './model/model.joblib'
        self.model_labels_path = './data/labels.txt'
        self.model_active = False

        # development mode
        self.dev_data_path = 'data/data.csv'
        self.dev_mode = True

        # openCV
        self.cv_cap_flip = True
        # self.cv_cap_source = 'http://192.168.123.12:8080/?action=stream'  # 0 == default device
        self.cv_cap_source = 0  # 0 == default device

    def __start_listener__(self):
        listener = get_conn_listener(GESTREC_PORT)
        while True:
            con = listener.accept()
            msg = con.recv()
            if msg == _GESTREC_OFF:
                self.model_active = False
            elif msg == _GESTREC_ON:
                self.model_active = True

    def __start_cap_listener__(self):
        Thread(target=self.__start_listener__).start()
        self.__run_gestrec__()

    def start(self):
        proc = Process(target=self.__start_cap_listener__)
        _procs.append(proc)
        proc.start()
        return proc

    def __run_gestrec__(self):
        # video capture ################################################################################################

        cap = cv2.VideoCapture(self.cv_cap_source)

        # mediapipe ####################################################################################################

        hands = mp_hands.Hands(
            model_complexity=self.mediapipe_model_complexity,
            min_detection_confidence=self.mediapipe_min_detection_confidence,
            min_tracking_confidence=self.mediapipe_min_tracking_confidence,
            max_num_hands=100,
        )

        # landmarks queue ##############################################################################################

        land_q = deque(maxlen=32)

        # ml model #####################################################################################################

        model = joblib.load(self.model_path) if not self.dev_mode else None
        labels = read_labels(self.model_labels_path) if not self.dev_mode else None

        # app ##########################################################################################################

        label = -1
        label_count = 1

        while cap.isOpened():
            # capture image
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue
            if self.cv_cap_flip:
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
                cv2.destroyAllWindows()
                cap.release()
                break
            if 48 <= key <= 57:  # 0 - 9
                label = key - 48

            if results.multi_hand_landmarks:

                # process hand landmarks
                hand_landmarks = get_nearest_hand(results.multi_hand_landmarks)
                landmarks = preprocess_landmarks(hand_landmarks)
                land_q.append(landmarks)

                # process landmarks and save to CSV when in dev_mode
                if self.dev_mode and label != -1:
                    if len(land_q) == land_q.maxlen:
                        write_csv(label, list(land_q), self.dev_data_path)
                        land_q.clear()
                        print(f'done_saving {label_count}st label with id {label}')
                        label_count += 1
                        label = -1

                # predict gesture using model
                if not self.dev_mode and self.model_active and len(land_q) == land_q.maxlen:
                    predict_result = np.squeeze(model.predict_proba(np.array(land_q).reshape(1, -1)))
                    idx = np.argmax(predict_result)
                    gesture, confidence = labels[idx], predict_result[idx]
                    if confidence >= self.model_min_confidence:
                        # print text to image
                        cv2.putText(
                            image, f'Gesture: {labels[idx]}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0),
                            4, cv2.LINE_AA)
                        cv2.putText(
                            image, f'Gesture: {labels[idx]}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255),
                            2, cv2.LINE_AA)
                        cv2.putText(image, f'Confidence: {confidence:.3f}', (10, 65),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv2.LINE_AA)
                        cv2.putText(image, f'Confidence: {confidence:.3f}', (10, 65),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

                # draw boundingbox
                x, y, w, h = bounding_rect(image, hand_landmarks)
                cv2.rectangle(image, (x, y), (w, h), (0, 0, 255), 1)
                cv2.rectangle(image, (x, y), (w, y-22), (0, 0, 255), -1)
                cv2.putText(image, 'Tracking', (x + 5, y - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

                # draw hands
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            # show capture

            cv2.imshow('MediaPipe Hands', image)


def __send_command__(command):
    con = get_conn_client(GESTREC_PORT)
    con.send(command)
    con.close()


def gestrec_stop():
    for proc in _procs:
        proc.terminate()


def gestrec_on():
    __send_command__(MSG_GESTREC_ON)


def gestrec_off():
    __send_command__(MSG_GESTREC_OFF)


if __name__ == '__main__':
    gestrec = Gestrec()
    gestrec.start()
