# utils/detect/args_parser.py
import argparse
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run YOLO detection on video/camera sources",
        add_help=True
    )

    parser.add_argument("--test", action="store_true",
                        help="Use the test model directory (~/YOLO4r/runs/test).")
    parser.add_argument("--sources", nargs="*",
                        help="Source list (e.g. usb0 usb1 video.mp4). Default: usb0")
    if ("--help" in sys.argv) or ("-h" in sys.argv) or ("help" in sys.argv):
        parser.parse_args(["--help"])
        sys.exit(0)
    if len(sys.argv) > 1 and not any(arg.startswith("--") for arg in sys.argv[1:]):
        args = parser.parse_args(["--sources"] + sys.argv[1:])
    else:
        args = parser.parse_args()

    if not args.sources:
        args.sources = ["usb0"]

    return args


