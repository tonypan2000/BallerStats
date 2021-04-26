# BallerStats

This is the presentation for the final project of the course Intro to Computer Vision. Our program estimates the distance traveled by a basketball player based on video footage. We combined camera calibration, object tracking, depth estimation with deep learning, and image transformations in this project.

## Presentation

[![Our Presentation Video](https://img.youtube.com/vi/GaL21ADNyes/maxresdefault.jpg)](https://www.youtube.com/embed/GaL21ADNyes)

See more [demo videos](https://github.com/tonypan2000/BallerStats/releases/download/1.2/demo.zip) under Release

## Requirements

Python 3

```bash
pip install -r requirements.txt
```

For camera calibration, see the [README](./camera_calibration/readme.md) inside the `camera_calibration` folder

For depth prediction, see the [README](./depth/readme.md) inside the `depth` folder

## Usage

1. Download our [BallerSet](https://github.com/tonypan2000/BallerStats/releases) dataset from the release page.

2. Unzip BallerSet and place the contents in the `./depth` folder

3. Run our program with the command

```bash
python main.py
```

## Performance

The camera calibration has an average absolute percent error of 11.78%, 
the depth estimation has an average absolute percent error of 11.67%. 
Cumulatively, BallerStats has an average percent error of 46% with a 
standard deviation of 17% on our BallerSet dataset. The model always overestimates
the distance traveled.


## Authors

[Robert Buckley](https://github.com/robertbuckley), [Richard Guan](https://github.com/rguan72), [Jensen Hwa](https://github.com/jensenhwa), [Tony Pan](https://github.com/tonypan2000), [Calvin Zheng](https://github.com/calvin-zheng)

## Acknowledgements

* BallerStats used open-source code from [Robust Monocular Depth Estimation](https://github.com/intel-isl/MiDaS) to generate depth disparity maps. We modified some of their code in accordance with the MIT License agreement, and encapsulated everything related to depth prediction in the `./depth` folder of this repo. Citation for their paper:

```
@article{Ranftl2020,
	author    = {Ren\'{e} Ranftl and Katrin Lasinger and David Hafner and Konrad Schindler and Vladlen Koltun},
	title     = {Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-shot Cross-dataset Transfer},
	journal   = {IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)},
	year      = {2020},
}
```

* This is the final project for the course [EECS 442 Intro to Computer Vision](https://web.eecs.umich.edu/~justincj/teaching/eecs442/WI2021/) at the University of Michigan Winter 2021 semester taught by [Justin Johnson](https://web.eecs.umich.edu/~justincj/) and [David Fouhey](https://web.eecs.umich.edu/~fouhey/).

## License

We have listed our software under the [MIT License](LICENSE)
