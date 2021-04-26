import cv2
import numpy as np


class ObjectTracker:
    def __init__(self, frame, name, color=(0, 255, 0)):
        self.tracker = cv2.TrackerCSRT_create()
        bounding_box = cv2.selectROI(f'Select bounding box for {name}', frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow(f'Select bounding box for {name}')
        self.tracker.init(frame, bounding_box)
        self.name = name
        self.color = color
        self.locations = np.array(
            [[[bounding_box[0] + bounding_box[2] // 2, bounding_box[1] + bounding_box[3] // 2]]])

    def track(self, frame):
        (success, box) = self.tracker.update(frame)
        if not success:
            raise RuntimeError("Object has been lost!")
        (x, y, w, h) = box
        center = (x + w // 2, y + h // 2)
        self.locations = np.append(self.locations, [[center]], axis=1)
        darker_color = tuple(np.maximum((0, 0, 0), np.subtract(self.color, (70, 70, 70))).tolist())
        cv2.polylines(frame, self.locations, False, darker_color, 2)
        cv2.putText(frame, self.name, (x, y - 5), cv2.FONT_HERSHEY_DUPLEX, 0.7, self.color)
        cv2.rectangle(frame, (x, y), (x + w, y + h), self.color, 2)
        return center


def track_bb(input_video):
    video_stream = cv2.VideoCapture(input_video)
    tracker = ObjectTracker(video_stream.read()[1])
    while True:
        frame = video_stream.read()[1]
        tracker.track(frame)


if __name__ == "__main__":
    # create main window
    track_bb("./depth/input/PXL_20210418_183745902.mp4")
    cv2.destroyAllWindows()
