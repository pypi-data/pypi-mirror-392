# cli.py
import argparse
import sys

def print_global_help():
    print("""
YOLO4R - You Only Look Once for Research
==============================================

Available Commands:
  yolo4r train      Train, update, or resume a YOLO model.
  yolo4r detect     Run YOLO detection on one or more video/camera sources.
  yolo4r version    Show the YOLO4r version.
  yolo4r help       Show this help menu.

----------------------------------------------
Command-Specific Help:
  yolo4r train --help
  yolo4r detect --help

Examples:
  yolo4r train -m yolo11n.pt -a custom_arch.yaml --dataset birds
  yolo4r train --scratch -a bird_model.yaml
  yolo4r detect --sources usb0 usb1 trailcam.mp4
  yolo4r detect trailcam.mp4

YOLO4r Documentation & Support:
  https://github.com/yourproject/yolo4r
""")

def main():
    parser = argparse.ArgumentParser(
        prog="yolo4r",
        description="You Only Look Once for Research",
        add_help=True
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- TRAIN ----
    train_parser = subparsers.add_parser("train", help="Train or update a model.")
    train_parser.set_defaults(func="train")

    # ---- DETECT ----
    detect_parser = subparsers.add_parser("detect", help="Run YOLO detection.")
    detect_parser.set_defaults(func="detect")

    # ---- VERSION ----
    version_parser = subparsers.add_parser("version", help="Show YOLO4R version.")
    version_parser.set_defaults(func="version")

    # ---- HELP ----
    help_parser = subparsers.add_parser("help", help="Show all YOLO4R commands.")
    help_parser.set_defaults(func="help")

    # ---- Parse command (not sub-arguments) ----
    args, unknown = parser.parse_known_args()

    # ROUTING
    if args.func == "train":
        from .train import main as train_main
        sys.argv = ["yolo4r-train"] + unknown
        return train_main()

    elif args.func == "detect":
      if "--help" in unknown or "-h" in unknown:
          from .utils.detect.arg_parser import parse_arguments
          sys.argv = ["yolo4r-detect", "--help"]
          parse_arguments()
          return

      from .detect import main as detect_main
      sys.argv = ["yolo4r-detect"] + unknown
      return detect_main()

    elif args.func == "version":
        from .version import YOLO4R_VERSION
        print(f"YOLO4R {YOLO4R_VERSION}")
        return

    elif args.func == "help":
        return print_global_help()

    else:
        parser.print_help()
