import os.path

import cv2
import numpy as np


class DepthTracker:
    def __init__(self, intrinsic_matrix, coordinate=None):
        intrinsic_matrix /= 1000
        intrinsic_matrix[2, 2] = 1
        self.intrinsic_matrix = np.linalg.inv(intrinsic_matrix)
        self.coordinate = coordinate

    def compute_dist(self, new_coord):
        if self.coordinate is None:
            self.coordinate = new_coord
            return 0
        dist = np.linalg.norm(new_coord - self.coordinate)
        self.coordinate = new_coord
        return dist

    def get_coordinates(self, img_name, x1, y1, x2, y2, vid_name=None):
        if vid_name is not None:
            filename = os.path.join('depth', 'output', vid_name, img_name + '.png')
            disparity = cv2.resize(cv2.imread(filename, cv2.IMREAD_GRAYSCALE), (0, 0), fx=0.5, fy=0.5)
        else:
            disparity = cv2.resize(cv2.imread(f'./output/{img_name}.png', cv2.IMREAD_GRAYSCALE), (0, 0), fx=0.5, fy=0.5)

        dist_to_point = 2
        inverted_disparity = np.float64(1.0) / disparity
        scaling_constant = dist_to_point / inverted_disparity[y2, x2]

        depth_map = inverted_disparity * scaling_constant
        depth = depth_map[y1, x1]
        print(f"depth at center: {depth}")
        camera_coords = np.array([[x1], [y1], [1]])

        world_pose = np.matmul(self.intrinsic_matrix, camera_coords)
        result = np.array([world_pose[0, 0] / 100, world_pose[1, 0] / 100, depth])
        return result

    def get_coords_bb(self, img_name):
        input_img = cv2.resize(cv2.imread(f"./input/{img_name}.jpg"), (0, 0), fx=0.5, fy=0.5)
        bounding_box = cv2.selectROI('frame', input_img, fromCenter=False, showCrosshair=True)
        center_x, center_y = bounding_box[0], bounding_box[1]

        # depth value * scaling_constant = real_world depth
        bounding_box = cv2.selectROI('frame', input_img, fromCenter=False, showCrosshair=True)
        x1, y1 = bounding_box[0], bounding_box[1]
        return self.get_coordinates(img_name, center_x, center_y, x1, y1)


if __name__ == "__main__":
    intrinsic_matrix = np.loadtxt('../camera_calibration/intrinsics.cfg')
    depth_tracker = DepthTracker(intrinsic_matrix)

    prev_coords = None
    for image in ["PXL_20210411_182359897", "PXL_20210411_182404641"]:
        coords = depth_tracker.get_coords_bb(image)  # 6.63
        print(f"in image {image} richard is at {coords}")
        if prev_coords is not None:
            dist = np.linalg.norm(prev_coords - coords)
            print(f"Richard moved {dist} m")
        prev_coords = coords
