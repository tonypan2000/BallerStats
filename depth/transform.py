import cv2
import numpy as np


class DepthTracker:
    def __init__(self, intrinsic_matrix, coordinates, depths):
        self.intrinsic_matrix = np.linalg.inv(intrinsic_matrix)
        self.coordinates = coordinates
        self.depths = depths

    def get_coordinates(self, img_name):
        input_img = cv2.resize(cv2.imread(f"./input/{img_name}.jpg"), (0, 0), fx=0.5, fy=0.5)
        bounding_box = cv2.selectROI('frame', input_img, fromCenter=False, showCrosshair=True)
        center_x, center_y = bounding_box[0], bounding_box[1]
        disparity = cv2.resize(cv2.imread(f'./output/{img_name}.png', cv2.IMREAD_GRAYSCALE), (0, 0), fx=0.5, fy=0.5)

        # depth value * scaling_constant = real_world depth
        bounding_box = cv2.selectROI('frame', input_img, fromCenter=False, showCrosshair=True)
        x1, y1 = bounding_box[0], bounding_box[1]
        dist_to_point = 2
        inverted_disparity = np.float64(1.0) / disparity
        scaling_constant = dist_to_point / inverted_disparity[y1, x1] # 417.69

        depth_map = inverted_disparity * scaling_constant
        depth = depth_map[center_y, center_x]
        print(f"depth at center: {depth}")
        camera_coords = np.array([[center_x], [center_y], [1]])

        world_pose = np.matmul(self.intrinsic_matrix, camera_coords)
        return np.array([world_pose[0, 0] / 100, world_pose[1, 0] / 100, depth])


if __name__ == "__main__":
    intrinsic_matrix = np.loadtxt('../camera_calibration/intrinsics.cfg') / 1000
    intrinsic_matrix[2, 2] = 1
    depth_tracker = DepthTracker(intrinsic_matrix, [], [])

    prev_coords = None
    for image in ["PXL_20210411_182359897", "PXL_20210411_182404641"]:
        coords = depth_tracker.get_coordinates(image)  # 6.63
        print(f"in image {image} richard is at {coords}")
        if prev_coords is not None:
            dist = np.linalg.norm(prev_coords - coords)
            print(f"Richard moved {dist} m")
        prev_coords = coords
