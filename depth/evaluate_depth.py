import cv2


def evaluate(input, gt):
  errors = []
  for i, img_name in enumerate(input):
    disparity = cv2.resize(cv2.imread(f"./output/{img_name}.png", cv2.IMREAD_GRAYSCALE), (0, 0), fx=0.25, fy=0.25)
    bounding_box = cv2.selectROI('frame', disparity, fromCenter=False, showCrosshair=True)
    (x1, y1, w1, h1) = bounding_box
    bounding_box = cv2.selectROI('frame', disparity, fromCenter=False, showCrosshair=True)
    (x2, y2, w2, h2) = bounding_box
    depth_hoop = 13.1
    disparity_baller = disparity[y1 + h1 // 2, x1 + w1 // 2]
    disparity_hoop = disparity[y2 + h2 // 2, x2 + w2 // 2]
    predicted_depth = depth_hoop * disparity_hoop / disparity_baller
    abs_diff = abs(gt[i] - predicted_depth)
    errors.append(abs_diff)
    print(img_name, predicted_depth, gt[i], abs_diff)
  total_err = sum(errors)
  print('avg abs err', total_err / 10)
  print('avg percent err', total_err / sum(gt))

if __name__ == "__main__":
  images = ['PXL_20210418_183745902/0', 'PXL_20210418_183745902/7', # 13.1 m, 7.36 m
            'PXL_20210418_183828738/0', 'PXL_20210418_183828738/6', # 13.1 m, 7.36 m
            'PXL_20210418_184015422/0', 'PXL_20210418_184015422/6', # 13.1 m, 5.56 m
            'PXL_20210418_184519166/0', 'PXL_20210418_184519166/6', # 13.1 m, 7.36 m
            'PXL_20210418_184627351/0', 'PXL_20210418_184627351/3'] # 13.1 m, 7.36 m
  truths = [13.1, 7.36, 13.1, 7.36, 13.1, 5.56, 13.1, 7.36, 13.1, 7.36]
  evaluate(images, truths)
