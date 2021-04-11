import cv2


def MIL_tracker(input_video):
  video_stream = cv2.VideoCapture(input_video)
  tracker = cv2.TrackerMIL_create()
  bounding_box = None

  while True:
    frame = video_stream.read()[1]
    ch = 0xFF & cv2.waitKey(1)
    if bounding_box is not None:
      # space key
      if ch == 32:
        (success, box) = tracker.update(frame)
        if success:
          (x, y, w, h) = [int(v) for v in box]
          cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow('frame', frame)
    else:
      cv2.imshow('frame', frame)
      bounding_box = cv2.selectROI('frame', frame, fromCenter=False, showCrosshair=True)
      tracker.init(frame, bounding_box)
    # continue until ESC
    if ch == 27:
      break


if __name__ == "__main__":
  # create main window
  cv2.namedWindow("frame", 1)
  MIL_tracker("Venice-2-raw.webm")
  cv2.destroyAllWindows()
