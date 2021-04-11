from apriltags3 import Detector
from calibration import get_video_stream
import cv2
import numpy as np


def get_tag_pose():
    camera_matrix = np.loadtxt('intrinsics.cfg')
    # [fx, fy, cx, cy]
    camera_param = np.array([camera_matrix[0, 0], camera_matrix[1, 1], camera_matrix[0, 2], camera_matrix[1, 2]])
    extrinsic_matrix = np.loadtxt('extrinsics.cfg')
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

            rot_mat = np.array([[tag.pose_R[0][0], tag.pose_R[0][1], tag.pose_R[0][2], tag.pose_t[0]],
                                [tag.pose_R[1][0], tag.pose_R[1][1], tag.pose_R[1][2], tag.pose_t[1]],
                                [tag.pose_R[2][0], tag.pose_R[2][1], tag.pose_R[2][2], tag.pose_t[2]],
                                [0.0, 0.0, 0.0, 1.0]], dtype='float')
            world_pose = np.matmul(extrinsic_matrix, rot_mat)
            world_coord = np.array([world_pose[0, 3], world_pose[1, 3], world_pose[2, 3]])
            # label the id of AprilTag on the image.
            cv2.putText(gray, str(world_coord),
                        org=(tag.corners[0, 0].astype(int) + 10, tag.corners[0, 1].astype(int) + 10),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.3,
                        color=(255, 0, 0))

        cv2.imshow('frame', gray)
        # continue until ESC
        if ch == 27:
            break

if __name__ == "__main__":
    # create main window
    cv2.namedWindow("frame", 1)
    get_tag_pose()
    cv2.destroyAllWindows()
