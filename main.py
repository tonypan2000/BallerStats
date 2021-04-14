import cv2
from depth import transform
import numpy as np
import os
import tracking


if __name__ == "__main__":
  video_name = 'PXL_20210411_182507574'
  input_video = os.path.join('depth', 'input', video_name + '.mp4')
  cap = cv2.VideoCapture(input_video)
  fps = cap.get(cv2.CAP_PROP_FPS)
  count = 0
  tracker_person = tracking.MIL_tracker()
  tracker_landmark = tracking.MIL_tracker()

  intrinsic_matrix = np.loadtxt(os.path.join('camera_calibration', 'intrinsics.cfg'))
  depth_tracker = transform.DepthTracker(intrinsic_matrix)
  dist_traveled = 0

  while cap.isOpened():
    img_name = 0
    ret, frame = cap.read()
    img = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    if ret:
      count += fps
      cap.set(1, count)
      x1, y1 = tracker_person.track(img)
      x2, y2 = tracker_landmark.track(img)
      if x1 is not None and x2 is not None:
        coords = depth_tracker.get_coordinates(str(img_name), x1, y1, x2, y2, video_name)
        dist = depth_tracker.compute_dist(coords)
        print(dist)
        dist_traveled += dist
      img_name += 1
    else:
      cap.release()
      break
