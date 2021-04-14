import cv2
from depth import transform
import numpy as np
import os
import tracking


if __name__ == "__main__":
  input_video = os.path.join('depth', 'input', 'PXL_20210411_182507574.mp4')
  cap = cv2.VideoCapture(input_video)
  fps = cap.get(cv2.CAP_PROP_FPS)
  count = 0
  tracker_person = tracking.MIL_tracker()
  tracker_landmark = tracking.MIL_tracker()

  intrinsic_matrix = np.loadtxt('../camera_calibration/intrinsics.cfg')
  depth_tracker = transform.DepthTracker(intrinsic_matrix, [], [])

  while cap.isOpened():
    ret, frame = cap.read()
    img = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    if ret:
      count += fps
      cap.set(1, count)
      x1, y1 = tracker_person.track(img)
      print(x1, y1)
      x2, y2 = tracker_landmark.track(img)
      print(x2, y2)
    else:
      cap.release()
      break
