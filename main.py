import cv2
from depth.transform import DepthTracker
import numpy as np
import os
from tracking import ObjectTracker


if __name__ == "__main__":
    video_name = 'PXL_20210418_183745902'
    input_video = os.path.join('depth', 'input', video_name + '.mp4')
    cap = cv2.VideoCapture(input_video)
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    objectTrackerFPS = 10
    scaleFactor = 0.25

    intrinsic_matrix = np.loadtxt(os.path.join('camera_calibration', 'intrinsics.cfg'))
    depth_tracker = DepthTracker(intrinsic_matrix, scale_factor=scaleFactor)
    dist_traveled = 0
    seconds_elapsed = 0

    if not cap.isOpened():
        print("Cannot open video")
        exit()
    ret, frame = cap.read()
    img = cv2.resize(frame, (0, 0), fx=scaleFactor, fy=scaleFactor)
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        exit()
    print("Select bounding box for person, then hit enter")
    tracker_person = ObjectTracker(img, "Richard Guan, 20", color=(0, 255, 0))
    print("Select bounding box for landmark, then hit enter")
    tracker_landmark = ObjectTracker(img, "Landmark", color=(0, 0, 255))

    distances = []
    currentFrame = 0
    while cap.isOpened():
        # Run object tracker every few frames
        currentFrame += fps / objectTrackerFPS
        cap.set(cv2.CAP_PROP_POS_FRAMES, currentFrame)
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        img = cv2.resize(frame, (0, 0), fx=scaleFactor, fy=scaleFactor)
        x1, y1 = tracker_person.track(img)
        x2, y2 = tracker_landmark.track(img)
        # Compute movement every second (based on fps)
        if currentFrame % fps == 0:
            coords = depth_tracker.get_coordinates(str(seconds_elapsed), x1, y1, x2, y2, video_name)
            dist = depth_tracker.compute_dist(coords)
            print(f"at second {seconds_elapsed} richard is at {coords}")
            print('dist from prev frame', dist)
            dist_traveled += dist
            distances.append((x1, y1, dist_traveled))
            seconds_elapsed += 1

        for (x1, y1, dist_traveled) in distances:
            cv2.putText(img, f"{dist_traveled:.1f}m", (x1, y1 - 5), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))
        cv2.imshow('BallerStats', img)
        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()
    print(dist_traveled)
