# Camera Calibration

## Requirements

* An Android device with a camera

* Download [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam&hl=en_US&gl=US) from the Google Play Store

* Linux to process April Tags

* Install [April Tags 3](https://github.com/AprilRobotics/apriltag) by following their instructions

* Add a folder to your library path: Run

```bash
sudo vi ~/.bashrc
```

and add the following (click i to insert in vim)

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
```

Then click ECS and :wq to save and quit. Restart your terminal.

* [Generate](https://github.com/AprilRobotics/apriltag-generation) and print at least 4 different varieties of April Tags of the tag family tagStandard41h12 with width 0.0127 m.

## Usage

1. Get the IP Address of IP Webcam from your Android device and write it down in [url.txt](url.txt) without any prefixes. i.e. 10.0.1.1:8080

2. Calibrate the intrinsic camera matrix by running intrinsic_calibration() in [calibration.py](calibration.py)

```bash
python calibration.py
```

Point your Android device at a checkerboard and gather images by pressing a space key. Take at least 20 photos, and then hit ECS. It will take a while to compute the intrinsic matrix if your phone has a high resolution camera. The calibration data is stored in [intrinsics.cfg](intrinsics.cfg).

3. Calibrate the extrinsic matrix by running extrinsic_calibration() in [calibration.py](calibration.py). Arrange at least 4 different April Tags in various poses and record their coordinates as objectPoints. When the camera can see all the April Tags, press ESC to calibrate. It saves the matrix to [extrinsics.cfg](extrinsics.cfg).

4. Test your calibration by running [eval_calibration.py](eval_calibration.py) and point your phone at an arbitrary April Tag. It will annotate the world coordinate of the tag and calculate the different with respect to the ground truth values.

## References

* We used OpenCV for checkerboard camera calibration

* We used [April Tags](https://april.eecs.umich.edu/papers/details.php?name=wang2016iros) for extrinsic calibration and evaluation of our camera parameters. [apriltags3.py](apriltags3.py) in this directory is obtained from the library, while everything else is authored by us.
