# utils/train/config.py
from pathlib import Path
from importlib.resources import files
import os, argparse, sys, json, shutil
from datetime import datetime

#  ---- UNIFIED YOLO4r ROOT PATHS ----
from ..paths import (
    BASE_DIR,
    DATA_DIR,
    RUNS_DIR,
    LOGS_DIR,
    MODELS_DIR,
    WEIGHTS_DIR,
    LS_ROOT,
)

# ---- TRAINING UTILITIES ----
from .io import (
    ensure_weights,
    ensure_yolo_yaml,
    normalize_model_name,
    FAMILY_TO_WEIGHTS,
    FAMILY_TO_YAML,
)

from .val_split import process_labelstudio_project

#  ---- INSTALL EXAMPLE FILES ----
def _install_examples():
    try:
        # ---- Example Label Studio project ----
        pkg_example_ls = files("yolo4r") / "labelstudio-projects" / "example"
        target_ls = LS_ROOT / "example"

        if pkg_example_ls.is_dir() and not target_ls.exists():
            shutil.copytree(pkg_example_ls, target_ls, dirs_exist_ok=True)

        # ---- Example Model Run ----
        pkg_example_run = files("yolo4r") / "runs" / "sparrows"
        target_run = RUNS_DIR / "sparrows"

        if pkg_example_run.is_dir() and not target_run.exists():
            shutil.copytree(pkg_example_run, target_run, dirs_exist_ok=True)

        # ---- Example Architecture YAMLs ----
        pkg_models = files("yolo4r") / "models"

        # only copy if user has no custom models yet
        if pkg_models.is_dir() and not any(MODELS_DIR.iterdir()):
            shutil.copytree(pkg_models, MODELS_DIR, dirs_exist_ok=True)

    except Exception as e:
        print(f"[WARN] Example installation failed: {e}")


_install_examples()


#  ---- TRAINING PATH RESOLUTION ----
def get_training_paths(dataset_folder: Path, test=False):
    """Return all core directories needed during training."""
    return {
        "runs_root":      RUNS_DIR / "test" if test else RUNS_DIR,
        "logs_root":      LOGS_DIR / "test" if test else LOGS_DIR,
        "train_folder":   dataset_folder / "train" / "images",
        "val_folder":     dataset_folder / "val" / "images",
        "weights_folder": WEIGHTS_DIR,
        "models_folder":  MODELS_DIR,
        "dataset_folder": dataset_folder,
    }


#  ---- LABEL STUDIO PROJECT SCANNING ----
def _find_labelstudio_projects(ls_root: Path):
    if not ls_root.exists():
        return []

    candidates = []
    for p in ls_root.iterdir():
        if not p.is_dir():
            continue

        img = p / "images"
        lbl = p / "labels"
        classes = p / "classes.txt"

        if img.is_dir() and lbl.is_dir() and classes.exists():
            candidates.append(p)

    return candidates


#  ---- DATASET METADATA HELPERS ----
def _get_dataset_label_mode(dataset_folder: Path) -> str | None:
    meta_path = dataset_folder / "metadata.json"
    if not meta_path.exists():
        return None

    try:
        with open(meta_path, "r") as f:
            meta = json.load(f)
        return meta.get("label_mode")
    except Exception:
        return None


def _family_is_obb(family: str | None) -> bool:
    return bool(family and family.endswith("-obb"))


#  ---- ARGUMENT PARSER ----
def get_args():
    """Parse and return command-line arguments for YOLO training."""
    parser = argparse.ArgumentParser(description="YOLO Training Script")

    # ---- CORE TRAINING MODES ----
    mode_group = parser.add_mutually_exclusive_group(required=False)

    mode_group.add_argument(
        "--train", "--transfer-learning", "-t",
        action="store_true",
        help="Force transfer-learning mode.",
    )

    mode_group.add_argument(
        "--scratch", "-s",
        action="store_true",
        help="Force training from scratch.",
    )

    parser.add_argument(
        "--update", "--upgrade", "-u",
        type=str, nargs="?", const=True,
        help="Update an existing model run by folder name.",
    )

    # ---- MODEL & ARCHITECTURE ----
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="Pretrained weights (.pt) or model family name.",
    )

    parser.add_argument(
        "--arch", "--architecture", "--backbone",
        "-a", "-b",
        type=str,
        help="Architecture YAML or family name.",
    )

    # ---- ADDITIONAL FLAGS ----
    parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="Resume training from last.pt",
    )

    parser.add_argument(
        "--test", "-T",
        action="store_true",
        help="Debug/testing mode (fast settings).",
    )

    parser.add_argument(
        "--dataset", "--data", "-d",
        type=str, default=None,
        help="Dataset folder inside ./data/.",
    )

    parser.add_argument(
        "--name", "-n",
        type=str, default=None,
        help="Custom run name.",
    )

    parser.add_argument(
        "--labelstudio", "--labelstudio-project", "--project",
        "-ls", type=str, default=None,
        help="Specify a Label Studio project inside ~/.YOLO4r/labelstudio-projects",
    )

    args = parser.parse_args()

    # default weights attribute
    if not hasattr(args, "weights"):
        args.weights = None

    # ---- DETERMINE MODE ----
    if args.update:
        mode = "update"
    elif args.arch and not args.model:
        mode = "scratch"
    elif args.model and not args.arch:
        mode = "train"
    elif args.scratch:
        mode = "scratch"
    elif args.train:
        mode = "train"
    else:
        mode = "train"

    # custom arch detection
    custom_arch = args.arch and args.arch.endswith(".yaml") and Path(args.arch).exists()

    # ---- RUN NAME RESOLUTION ----
    if args.name:
        base_name = args.name.strip()
    else:
        base_name = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ensure unique name
    def _increment_name(root: Path, name: str) -> str:
        proposed = name
        i = 1
        while (root / proposed).exists():
            proposed = f"{name}{i}"
            i += 1
        return proposed

    final_name = _increment_name(DATA_DIR, base_name)
    args.final_name = final_name
    args.name = final_name

    # ---- DATASET DETECTION ----
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LS_ROOT.mkdir(parents=True, exist_ok=True)

    if args.dataset:
        dataset_folder = DATA_DIR / args.dataset
        if not dataset_folder.exists():
            print(f"[ERROR] Dataset folder not found: {dataset_folder}")
            sys.exit(1)

        DATA_YAML = dataset_folder / "data.yaml"
        if not DATA_YAML.exists():
            print(f"[ERROR] data.yaml not found in dataset folder: {DATA_YAML}")
            sys.exit(1)

    else:
        ls_projects = _find_labelstudio_projects(LS_ROOT)

        if ls_projects:
            newest = sorted(ls_projects, key=lambda x: x.stat().st_mtime)[0]
            print(f"[DATA] Found Label Studio project: {newest}")
            dataset_folder, DATA_YAML = process_labelstudio_project(
                newest, DATA_DIR, dataset_name=args.final_name
            )
        else:
            all_datasets = [d for d in DATA_DIR.iterdir() if d.is_dir()]

            if len(all_datasets) == 0:
                print("[ERROR] No datasets found.")
                sys.exit(1)

            elif len(all_datasets) == 1:
                dataset_folder = all_datasets[0]
                DATA_YAML = dataset_folder / "data.yaml"
                print(f"[DATA] Auto-selected dataset: {dataset_folder.name}")

            else:
                print("[ERROR] Multiple datasets detected; specify with --dataset")
                print("Available:", [d.name for d in all_datasets])
                sys.exit(1)

    if not DATA_YAML.exists():
        print(f"[ERROR] Missing data.yaml: {DATA_YAML}")
        sys.exit(1)

    # ---- LABEL MODE HANDLING ----
    label_mode = _get_dataset_label_mode(dataset_folder)
    dataset_is_obb = (label_mode == "obb") if label_mode else None

    # ---- RESOLVE TRAINING PATHS ----
    paths = get_training_paths(dataset_folder, test=args.test)
    paths["weights_folder"].mkdir(parents=True, exist_ok=True)
    paths["models_folder"].mkdir(parents=True, exist_ok=True)

    # ---- ATTACH PATHS ----
    args.DATA_YAML = DATA_YAML
    args.train_folder = paths["train_folder"]
    args.val_folder = paths["val_folder"]
    args.dataset_folder = dataset_folder

    return args, mode
