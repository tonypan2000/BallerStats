import cv2
import numpy as np


input_img = cv2.resize(cv2.imread('./input/PXL_20210411_182359897.jpg'), (0, 0), fx=0.5, fy=0.5)
bounding_box = cv2.selectROI('frame', input_img, fromCenter=False, showCrosshair=True)
center_x, center_y = input_img.shape[1] - bounding_box[0], input_img.shape[1] - bounding_box[1]
print(center_x, center_y)
depth_map = cv2.resize(cv2.imread('./output/PXL_20210411_182359897.png'), (0, 0), fx=0.5, fy=0.5)
depth = depth_map[center_y, center_x, 0]
print(depth)

camera_coords = np.array([[depth], [center_x], [center_y], [1]])

extrinsic_matrix = np.loadtxt('../camera_calibration/extrinsics.cfg')
world_pose = np.matmul(extrinsic_matrix, camera_coords)

print(world_pose)
