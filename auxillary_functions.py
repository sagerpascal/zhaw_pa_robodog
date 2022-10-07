from sklearn.preprocessing import normalize
import numpy as np
from itertools import chain
import csv


def process_landmarks(landmarks):
    tmp_marks = map(lambda l: (l.x, l.y, l.z), landmarks.landmark)
    tmp_marks = np.array(list(chain.from_iterable(tmp_marks)))
    tmp_marks = normalize(tmp_marks.reshape(1, -1)).flatten()
    return tmp_marks


def write_csv(label, landmark_list, csv_path):
    if label == -1:
        return
    with open(csv_path, 'a', newline='') as f:
        tmp_marks = np.array(landmark_list).flatten()
        list_to_write = np.insert(tmp_marks, 0, label)
        writer = csv.writer(f)
        writer.writerow(list_to_write)