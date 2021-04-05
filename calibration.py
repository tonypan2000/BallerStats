from apriltags3 import Detector
import cv2
from ipwebcam import *
import numpy as np


def get_video_stream():
  with open("url.txt", 'r') as file:
    url = file.read()
  ipcam = IPWEBCAM(url)
  return ipcam

def intrinsic_calibration():
  font = cv2.FONT_HERSHEY_SIMPLEX
  h = 480
  w = 640
  # size of each checker square [mm]
  square_size = 25.4
  # pattern of corners on checker board
  pattern_size = (8, 6)
  # termination criteria for finding fit
  criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

  # builds array of reference corner locations
  pattern_points = np.zeros((pattern_size[0]*pattern_size[1], 3), np.float32)
  pattern_points[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
  pattern_points *= square_size

  # stores the locations of corners on the checkerboard
  obj_points = []
  # stores the pixel locations of corners for all frames
  img_points = []
  frame_count = 0
  ipcam = get_video_stream()

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
  np.savetxt('intrinsics.cfg', camera_matrix)

def extrinsic_calibration():
  camera_matrix = np.loadtxt('intrinsics.cfg')
  # [fx, fy, cx, cy]
  camera_param = np.array([camera_matrix[0, 0], camera_matrix[1, 1], camera_matrix[0, 2], camera_matrix[1, 2]])
  # 3D coordinates of the center of AprilTags in the arm frame in meters.
  #                         x         y           z (meters in Cozmo camera coordinate frame)
  objectPoints = np.array([[0.15, 0.0254 / 2, 3 * 0.0254 / 2],
                           [0.15 + 0.0254, -0.0254 / 2, 3 * 0.0254 / 2],
                           [0.15, 0.0254 / 2, 0.0254 / 2],
                           [0.15 + 0.0254, -0.0254 / 2, 0.0254 / 2]])
  detector = Detector("tagStandard41h12", quad_decimate=2.0, quad_sigma=1.0, debug=False)
  ipcam = get_video_stream()
  while True:
    ch = 0xFF & cv2.waitKey(1)
    frame = ipcam.get_image()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray, estimate_tag_pose=True, camera_params=camera_param, tag_size=0.0127)
    # visualize the detection
    for tag in tags:
      for idx in range(len(tag.corners)):
        cv2.line(gray, tuple(tag.corners[idx - 1, :].astype(int)),
                 tuple(tag.corners[idx, :].astype(int)), (255, 0, 0))

      # label the id of AprilTag on the image.
      cv2.putText(gray, str(tag.tag_id),
                  org=(tag.corners[0, 0].astype(int) + 10, tag.corners[0, 1].astype(int) + 10),
                  fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                  fontScale=1,
                  color=(255, 0, 0))
    cv2.imshow('AprilTags', gray)
    # continue until ESC
    if ch == 27:
      break

  # Use the center of the tags as image points. Make sure they correspond to the 3D points.
  imagePoints = np.array([tag.center for tag in tags])
  assert (len(tags) == 4)
  print("Image Points: ", imagePoints)
  success, rvec, tvec = cv2.solvePnP(objectPoints, np.array(imagePoints), camera_matrix, None)
  rotation_matrix, _ = cv2.Rodrigues(rvec)

  affine_transformation = np.array([[rotation_matrix[0][0], rotation_matrix[0][1], rotation_matrix[0][2], tvec[0]],
                                    [rotation_matrix[1][0], rotation_matrix[1][1], rotation_matrix[1][2], tvec[1]],
                                    [rotation_matrix[2][0], rotation_matrix[2][1], rotation_matrix[2][2], tvec[2]],
                                    [0.0, 0.0, 0.0, 1.0]], dtype='float')
  # homogeneous matrix from camera coordinates to camera coordinates
  extrinsic = np.linalg.inv(affine_transformation)
  print("extrinsic: ", extrinsic)

  for tag in tags:
    homo = np.array([[tag.pose_R[0][0], tag.pose_R[0][1], tag.pose_R[0][2], tag.pose_t[0]],
                     [tag.pose_R[1][0], tag.pose_R[1][1], tag.pose_R[1][2], tag.pose_t[1]],
                     [tag.pose_R[2][0], tag.pose_R[2][1], tag.pose_R[2][2], tag.pose_t[2]],
                     [0.0, 0.0, 0.0, 1.0]], dtype='float')
    tag_pose = np.matmul(homo, np.array([0, 0, 0.0125, 1]))
    arm_pose = np.matmul(extrinsic, tag_pose)
    print("true pose", arm_pose)
  np.savetxt("extrinsics.cfg", extrinsic)


if __name__ == "__main__":
  # create main window
  cv2.namedWindow("frame", 1)

  # intrinsic_calibration()
  extrinsic_calibration()

  cv2.destroyAllWindows()
