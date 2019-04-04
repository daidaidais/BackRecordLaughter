import numpy as np
import cv2

class CameraStream():
    def __init__(self):
        self._cap = cv2.VideoCapture(0)

    def __enter__(self):
        print('pre processing of CameraStream')
        return self

    def __exit__(self, type, value, traceback):
        print('post processing of CameraStream')
        self._cap.release()
        cv2.destroyAllWindows()

    def start(self):
            while True:
                try:
                    ret, frame = self._cap.read()
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    cv2.imshow('frame',gray)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                except:
                    print("CameraStream error")
                    break
# [END CameraStream]
