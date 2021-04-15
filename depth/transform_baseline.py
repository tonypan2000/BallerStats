import os.path

import cv2
import numpy as np


class DepthTracker:
    def __init__(self, intrinsic_matrix, scale_factor=1.0, coordinate=None):
        self.scale_factor = scale_factor
        self.fx = intrinsic_matrix[0, 0] * scale_factor
        self.fy = intrinsic_matrix[1, 1] * scale_factor
        self.cx = intrinsic_matrix[0, 2] * scale_factor
        self.cy = intrinsic_matrix[1, 2] * scale_factor
        self.coordinate = coordinate

    def compute_dist(self, new_coord):
        if self.coordinate is None:
            self.coordinate = new_coord
            return 0
        dist = np.linalg.norm(new_coord - self.coordinate)
        self.coordinate = new_coord
        return dist

    def get_coordinates(self, img_name, x1, y1, height_pixels, vid_name=None):
        if vid_name is not None:
            filename = os.path.join('depth', 'output', vid_name, img_name + '.png')
            disparity = cv2.resize(cv2.imread(filename, cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        else:
            disparity = cv2.resize(cv2.imread(f'./output/{img_name}.png', cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.scale_factor, fy=self.scale_factor)

        depth = 2.0 / height_pixels * self.fy
        print(f"depth at center: {depth}")

        x = (x1 - self.cx) * depth / self.fx
        y = (y1 - self.cy) * depth / self.fy
        result = np.array([x, y, depth])
        return result

    def get_coords_bb(self, img_name):
        input_img = cv2.resize(cv2.imread(f"./input/{img_name}.jpg"), (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        bounding_box = cv2.selectROI('frame', input_img, fromCenter=False, showCrosshair=True)
        center_x, center_y, height_pixels = bounding_box[0], bounding_box[1], bounding_box[3]
        return self.get_coordinates(img_name, center_x, center_y, height_pixels)


if __name__ == "__main__":
    intrinsic_matrix = np.loadtxt('../camera_calibration/intrinsics.cfg')
    depth_tracker = DepthTracker(intrinsic_matrix, scale_factor=0.25)

    prev_coords = None
    for image in ["PXL_20210411_182359897", "PXL_20210411_182404641"]:
        coords = depth_tracker.get_coords_bb(image)  # 6.63
        print(f"in image {image} richard is at {coords}")
        if prev_coords is not None:
            dist = np.linalg.norm(prev_coords - coords)
            print(f"Richard moved {dist} m")
        prev_coords = coords
