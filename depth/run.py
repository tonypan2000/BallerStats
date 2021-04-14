"""Compute depth maps for images in the input folder.
"""
import argparse
import cv2
import glob
import os
import torch
import utils

from torchvision.transforms import Compose
from midas.midas_net import MidasNet
from midas.midas_net_custom import MidasNet_small
from midas.transforms import Resize, NormalizeImage, PrepareForNet


class DepthPredictor:
    def __init__(self, model_type, model_path, optimize):
        print("initialize")

        # select device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("device: %s" % self.device)

        # load network
        if model_type == "large":
            self.model = MidasNet(model_path, non_negative=True)
            self.net_w, self.net_h = 384, 384
        elif model_type == "small":
            self.model = MidasNet_small(model_path, features=64, backbone="efficientnet_lite3", exportable=True,
                                   non_negative=True, blocks={'expand': True})
            self.net_w, self.net_h = 256, 256
        else:
            print(f"model_type '{model_type}' not implemented, use: --model_type large")
            assert False

        self.transform = Compose(
            [
                Resize(
                    self.net_w,
                    self.net_h,
                    resize_target=None,
                    keep_aspect_ratio=True,
                    ensure_multiple_of=32,
                    resize_method="upper_bound",
                    image_interpolation_method=cv2.INTER_CUBIC,
                ),
                NormalizeImage(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                PrepareForNet(),
            ]
        )

        self.model.eval()
        self.optimize = optimize
        if self.optimize:
            rand_example = torch.rand(1, 3, self.net_h, self.net_w)
            self.model(rand_example)
            traced_script_module = torch.jit.trace(self.model, rand_example)
            self.model = traced_script_module

            if self.device == torch.device("cuda"):
                self.model = self.model.to(memory_format=torch.channels_last)
                self.model = self.model.half()

        self.model.to(self.device)

    def process_video(self, filename, dir_name):
        cap = cv2.VideoCapture(filename)
        fps = cap.get(cv2.CAP_PROP_FPS)
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                if len(frame.shape) == 2:
                    img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) / 255.0
                prediction = self.process_images(img)
                # output
                out_filename = os.path.join(
                    dir_name, str(count / 30)[0]
                )
                utils.write_depth(out_filename, prediction, bits=2)

                count += fps
                cap.set(1, count)
            else:
                cap.release()
                break

    def process_images(self, img):
        img_input = self.transform({"image": img})["image"]

        # compute
        with torch.no_grad():
            sample = torch.from_numpy(img_input).to(self.device).unsqueeze(0)
            if self.optimize and self.device == torch.device("cuda"):
                sample = sample.to(memory_format=torch.channels_last)
                sample = sample.half()
            prediction = self.model.forward(sample)
            prediction = (
                torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                )
                    .squeeze()
                    .cpu()
                    .numpy()
            )

        return prediction

def run(input_path, output_path, model_path, model_type="large", optimize=True, input_video=True):
    """Run MonoDepthNN to compute depth maps.

    Args:
        input_path (str): path to input folder
        output_path (str): path to output folder
        model_path (str): path to saved model
    """
    predictor = DepthPredictor(model_type, model_path, optimize)

    # get input
    print("start processing")
    if input_video:
        vid_names = glob.glob(os.path.join(input_path, "*.mp4"))
        for ind, vid_name in enumerate(vid_names):
            dir_name = os.path.join(output_path, os.path.splitext(os.path.basename(vid_name))[0])
            os.makedirs(dir_name, exist_ok=True)
            predictor.process_video(vid_name, dir_name)
    else:
        img_names = glob.glob(os.path.join(input_path, "*"))
        num_images = len(img_names)
        # create output folder
        os.makedirs(output_path, exist_ok=True)

        for ind, img_name in enumerate(img_names):
            print("  processing {} ({}/{})".format(img_name, ind + 1, num_images))
            # input
            img = utils.read_image(img_name)
            prediction = predictor.process_images(img)

            # output
            filename = os.path.join(
                output_path, os.path.splitext(os.path.basename(img_name))[0]
            )
            utils.write_depth(filename, prediction, bits=2)

    print("finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input_path', 
        default='input',
        help='folder with input images'
    )

    parser.add_argument('-o', '--output_path', 
        default='output',
        help='folder for output images'
    )

    parser.add_argument('-m', '--model_weights', 
        default='model-f6b98070.pt',
        help='path to the trained weights of model'
    )

    parser.add_argument('-t', '--model_type', 
        default='large',
        help='model type: large or small'
    )

    parser.add_argument('-v', dest='input_type', action='store_true')
    parser.add_argument('-p', dest='input_type', action='store_false')
    parser.set_defaults(input_type=True)

    parser.add_argument('--optimize', dest='optimize', action='store_true')
    parser.add_argument('--no-optimize', dest='optimize', action='store_false')
    parser.set_defaults(optimize=True)

    args = parser.parse_args()

    # set torch options
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True

    # compute depth maps
    run(args.input_path, args.output_path, args.model_weights, args.model_type, args.optimize, args.input_type)
