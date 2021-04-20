import cv2
from depth import transform
import numpy as np
import os
import tracking


if __name__ == "__main__":
  # video_name = 'PXL_20210411_182507574'
  video_name = 'PXL_20210418_184103800'
  input_video = os.path.join('depth', 'input', video_name + '.mp4')
  cap = cv2.VideoCapture(input_video)
  fps = cap.get(cv2.CAP_PROP_FPS)
  currentFrame = 0
  objectTrackerFramerate = 3
  scaleFactor = 0.5
  tracker_person = tracking.CSRT_Tracker()
  tracker_landmark = tracking.CSRT_Tracker()

  intrinsic_matrix = np.loadtxt(os.path.join('camera_calibration', 'intrinsics.cfg'))
  depth_tracker = transform.DepthTracker(intrinsic_matrix, scale_factor=scaleFactor)
  dist_traveled = 0
  img_name = 0

  while cap.isOpened():
    ret, frame = cap.read()
    if ret:
      img = cv2.resize(frame, (0, 0), fx=scaleFactor, fy=scaleFactor)
      x1, y1 = tracker_person.track(img)
      x2, y2 = tracker_landmark.track(img)
      currentFrame += objectTrackerFramerate
      cap.set(1, currentFrame)
      if currentFrame >= img_name * fps:
        currentFrame = img_name * fps
        cap.set(1, currentFrame)
        if x1 is not None and x2 is not None:
          coords = depth_tracker.get_coordinates(str(img_name), x1, y1, x2, y2, video_name)
          dist = depth_tracker.compute_dist(coords)
          print(f"in image {img_name} richard is at {coords}")
          print('dist from prev frame', dist)
          dist_traveled += dist
        img_name += 1
    else:
      cap.release()
      break
  cv2.destroyAllWindows()
  print(dist_traveled)
