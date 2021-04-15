import cv2


class MIL_tracker():
  def __init__(self):
    self.tracker = cv2.TrackerMIL_create()
    self.bounding_box = None

  def track(self, frame):
    x, y = None, None
    if self.bounding_box is not None:
      (success, box) = self.tracker.update(frame)
      if success:
        (x, y, w, h) = [int(v) for v in box]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
      cv2.imshow('frame', frame)
      cv2.waitKey(0)
    else:
      self.bounding_box = cv2.selectROI('frame', frame, fromCenter=False, showCrosshair=True)
      self.tracker.init(frame, self.bounding_box)
    return x, y

def track_bb(input_video):
  video_stream = cv2.VideoCapture(input_video)
  tracker = MIL_tracker()
  while True:
    frame = video_stream.read()[1]
    tracker.track(frame)


if __name__ == "__main__":
  # create main window
  track_bb("Venice-2-raw.webm")
  cv2.destroyAllWindows()
