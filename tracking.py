import cv2


video_stream = cv2.VideoCapture("Venice-2-raw.webm")
tracker = cv2.TrackerMIL_create()
bounding_box = None

while True:
  frame = video_stream.read()[1]

  if bounding_box is not None:
    (success, box) = tracker.update(frame)
    if success:
      (x, y, w, h) = [int(v) for v in box]
      cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)

  else:
    cv2.imshow('frame', frame)
    bounding_box = cv2.selectROI('frame', frame, fromCenter=False, showCrosshair=True)
    tracker.init(frame, bounding_box)
