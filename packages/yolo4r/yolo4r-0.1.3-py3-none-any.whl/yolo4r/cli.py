# yolo4r/cli.py
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        prog="yolo4r",
        description="YOLO4R - Unified training & detection command-line interface."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------------- TRAIN --------------------
    train_parser = subparsers.add_parser("train", help="Train or update a model.")
    train_parser.add_argument("train_args", nargs=argparse.REMAINDER)

    # ------------------- DETECT --------------------
    detect_parser = subparsers.add_parser("detect", help="Run YOLO detection.")
    detect_parser.add_argument("detect_args", nargs=argparse.REMAINDER)

    # ------------------- VERSION -------------------
    subparsers.add_parser("version", help="Show YOLO4R version.")

    args = parser.parse_args()

    # -------- ROUTING --------
    if args.command == "train":
        from .train import main as train_main

        # Correct sys.argv injection
        sys.argv = ["yolo4r-train"] + args.train_args
        return train_main()

    elif args.command == "detect":
        from .detect import main as detect_main

        sys.argv = ["yolo4r-detect"] + args.detect_args
        return detect_main()

    elif args.command == "version":
        from .version import YOLO4R_VERSION
        print(f"YOLO4R {YOLO4R_VERSION}")
        return

    else:
        parser.print_help()
