import cv2
from ipwebcam import *
import numpy as np


font = cv2.FONT_HERSHEY_SIMPLEX
h = 480
w = 640
# size of each checker square [mm]
square_size = 25.4
# pattern of corners on checker board
pattern_size = (8, 6)

# builds array of reference corner locations
pattern_points = np.zeros((pattern_size[0]*pattern_size[1], 3), np.float32)
pattern_points[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
pattern_points *= square_size

# stores the locations of corners on the checkerboard
obj_points = []

# stores the pixel locations of corners for all frames
img_points = []

# termination criteria for finding fit
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# create main window
cv2.namedWindow("frame", 1)

frame_count = 0

with open("url.txt") as file:
  url = file.read()

ipcam = IPWEBCAM(url)

while True:
  ch = 0xFF & cv2.waitKey(1)
  frame = ipcam.get_image()
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  frames_str = "Frames:" + str(frame_count)
  cv2.putText(frame, frames_str, (50, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
  # space key
  if ch == 32:
    print("searching... ")
    # find location of corners in image, this is really slow if no corners are seen.
    found, corners = cv2.findChessboardCorners(gray, pattern_size, None)
    if found:
      # find sub pixel estimate for corner location
      cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)
      # add detected corners to RGB image
      frame_count += 1
      img_points.append(corners.reshape(-1, 2))
      obj_points.append(pattern_points)
      cv2.drawChessboardCorners(frame, pattern_size, corners, found)
      cv2.imshow('frame', frame)
  else:
    cv2.imshow('frame', frame)
    # continue until ESC
  if ch == 27:
    break

# Perform actual calibration
rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h), None, None)
print("Performing calibration with", frame_count, "frames")
print("RMS Error:", rms)
print("camera matrix:\r\n", camera_matrix)
print("distortion coefficients:\r\n", dist_coefs.ravel())

f = open('calibration.cfg', 'w')
f.write("intrinsic matrix:\r\n")
f.write(str(camera_matrix))
f.write("\r\ndistortion coefficients:\r\n")
f.write(str(dist_coefs.ravel()))
f.close()

cv2.destroyAllWindows()
