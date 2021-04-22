from apriltags3 import Detector
from calibration import get_video_stream, compute_transformation
import cv2
import numpy as np


object_points = np.array([[0.2, 0.0254 / 2, 3 * 0.0254 / 2],
                           [0.2 + 0.0254, -0.0254 / 2, 3 * 0.0254 / 2],
                           [0.2, 0.0254 / 2, 0.0254 / 2],
                           [0.2 + 0.0254, -0.0254 / 2, 0.0254 / 2]])

def eval():
    camera_matrix = np.loadtxt('intrinsics.cfg')
    # [fx, fy, cx, cy]
    camera_param = np.array([camera_matrix[0, 0], camera_matrix[1, 1], camera_matrix[0, 2], camera_matrix[1, 2]])
    extrinsic_matrix = np.loadtxt('extrinsics.cfg')
    detector = Detector("tagStandard41h12", quad_decimate=2.0, quad_sigma=1.0, debug=False)
    ipcam = get_video_stream()
    errors = []
    lengths = []
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

            world_coord = compute_transformation(tag, extrinsic_matrix)
            # label the id of AprilTag on the image.
            cv2.putText(gray, str(world_coord),
                        org=(tag.corners[0, 0].astype(int) + 10, tag.corners[0, 1].astype(int) + 10),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.3,
                        color=(255, 0, 0))

        cv2.imshow('frame', gray)

        # space key
        if ch == 32:
            for i, tag in enumerate(tags):
              world_coord = compute_transformation(tag, extrinsic_matrix)
              dist = np.linalg.norm(object_points[i])
              lengths.append(dist)
              abs_diff = abs(np.linalg.norm(object_points[i] - world_coord))
              errors.append(abs_diff)
              percent_diff = abs_diff / np.linalg.norm(world_coord)
              print('tag', i)
              print('ground truth', object_points[i])
              print('estimated', world_coord)
              print('abs diff', abs_diff)
              print('percent diff', percent_diff)
              print('-------')
            avg_err = sum(errors) / 4
            print('avg abs err', avg_err)
            print('avg percent err', avg_err / sum(lengths))
        # continue until ESC
        if ch == 27:
            break

if __name__ == "__main__":
    # create main window
    cv2.namedWindow("frame", 1)
    eval()
    cv2.destroyAllWindows()
