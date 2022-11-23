from sklearn.preprocessing import normalize
import numpy as np
import cv2
from itertools import chain
import csv
import re


def preprocess_landmarks(landmarks):
    tmp_marks = map(lambda l: (l.x, l.y, l.z), landmarks.landmark)
    tmp_marks = np.array(list(chain.from_iterable(tmp_marks)))
    bla = normalize(tmp_marks.reshape(1, -1)).flatten()
    return tmp_marks


def bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.empty((0, 2), int)
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv2.boundingRect(landmark_array)

    return (x, y, x + w, y + h)

def get_nearest_hand(landmarks_lst):
    mapped = list(map(lambda h: h.landmark[0].z, landmarks_lst))
    idx = np.argmax(mapped)
    return landmarks_lst[idx]


def read_labels(labels_path):
    with open(labels_path, 'r') as f:
        data = f.readlines()
        return np.array([re.findall(r'[a-z]+_?[a-z]+', line) for line in data]).flatten()


def write_csv(label, landmark_list, csv_path):
    if label == -1:
        return
    with open(csv_path, 'a', newline='') as f:
        tmp_marks = np.array(landmark_list).flatten()
        list_to_write = np.insert(tmp_marks, 0, label)
        writer = csv.writer(f)
        writer.writerow(list_to_write)
