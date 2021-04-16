import numpy as np
import cv2

class BallerDetector:
    def __init__(self, scale_factor=1.0):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.scale_factor = scale_factor
    def detect(self, fname):
        img = cv2.resize(cv2.imread(fname, cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        boxes, weights = self.hog.detectMultiScale(img, winStride=(8, 8), padding=(16, 16))
        boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
        for (xA, yA, xB, yB) in boxes:
            cv2.rectangle(img, (xA, yA), (xB, yB),
                          (0, 255, 0), 2)
        cv2.imshow('frame', img)
        cv2.waitKey(0)

if __name__ == "__main__":
    bd = BallerDetector(scale_factor=.25)
    bd.detect("depth/input/PXL_20210411_182740594.jpg")


