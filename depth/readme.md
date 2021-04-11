# Depth Estimation

## Requirements

1. Conda

```bash
conda install -c pytorch torchvision
```

2. Download the model weights [model-f6b98070.pt](https://github.com/intel-isl/MiDaS/releases/download/v2_1/model-f6b98070.pt) and [model-small-70d6b9c8.pt](https://github.com/intel-isl/MiDaS/releases/download/v2_1/model-small-70d6b9c8.pt) and place the file in the `depth` folder.

## Usage

1. Place one or more input images in the folder `./depth/input`.

2. Run the model:

```bash
    python run.py
```

## References

This model is from the paper Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-shot Cross-dataset Transfer and their Github repo [MiDaS](https://github.com/intel-isl/MiDaS).

```
@article{Ranftl2020,
	author    = {Ren\'{e} Ranftl and Katrin Lasinger and David Hafner and Konrad Schindler and Vladlen Koltun},
	title     = {Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-shot Cross-dataset Transfer},
	journal   = {IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)},
	year      = {2020},
}
```
