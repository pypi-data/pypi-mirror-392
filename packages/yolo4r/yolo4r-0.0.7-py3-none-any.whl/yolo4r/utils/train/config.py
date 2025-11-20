# utils/train/config.py
from pathlib import Path
from importlib.resources import files
import os, argparse, sys, json, shutil
from datetime import datetime
from .io import (
    ensure_weights,
    ensure_yolo_yaml,
    normalize_model_name,
    FAMILY_TO_WEIGHTS,
    FAMILY_TO_YAML,
)
from .val_split import process_labelstudio_project

# ---- Base Paths ----
BASE_DIR = Path("/data") / os.environ.get("USER", "unknown") / "YOLO4r"
BASE_DIR.mkdir(parents=True, exist_ok=True)

LS_ROOT = BASE_DIR / "labelstudio-projects"
DATA_ROOT = BASE_DIR / "data"
RUNS_ROOT = BASE_DIR / "runs"
LOGS_ROOT = BASE_DIR / "logs"
MODELS_ROOT = BASE_DIR / "models"
WEIGHTS_ROOT = BASE_DIR / "weights"

# Ensure directories exist
for d in [LS_ROOT, DATA_ROOT, RUNS_ROOT, LOGS_ROOT, MODELS_ROOT, WEIGHTS_ROOT]:
    d.mkdir(parents=True, exist_ok=True)

# -------- Example Project + Model Installation --------
def _install_examples():
    try:
        # ----------- Example Label Studio Project -----------
        pkg_example_ls = files("yolo4r") / "labelstudio-projects" / "example"
        target_ls = LS_ROOT / "example"

        if pkg_example_ls.is_dir() and not target_ls.exists():
            shutil.copytree(pkg_example_ls, target_ls, dirs_exist_ok=True)

        # ----------- Example Model Run -----------
        pkg_example_run = files("yolo4r") / "runs" / "sparrows"
        target_run = RUNS_ROOT / "sparrows"

        if pkg_example_run.is_dir() and not target_run.exists():
            shutil.copytree(pkg_example_run, target_run, dirs_exist_ok=True)

        # ----------- MODELS (architecture YAMLs) -----------
        pkg_models = files("yolo4r") / "models"
        target_models = MODELS_ROOT

        # Only copy if no user models exist yet
        if pkg_models.is_dir() and not any(target_models.iterdir()):
            shutil.copytree(pkg_models, target_models, dirs_exist_ok=True)

    except Exception as e:
        print(f"[WARN] Example installation failed: {e}")

_install_examples()

def is_custom_yaml(arch: str, models_dir: Path) -> bool:
    arch = arch.lower()

    # Case 1 — user provided direct path
    if arch.endswith(".yaml") and Path(arch).exists():
        return True

    # Case 2 — user provided a YAML name inside the models folder
    if arch.endswith(".yaml") and (models_dir / arch).exists():
        return True

    # Case 3 — not a known family => treat as custom architecture
    if arch not in FAMILY_TO_YAML:
        return True

    return False

def get_training_paths(dataset_folder: Path, test=False):
    """Return key directory paths for training and logging based on dataset folder."""
    return {
        "runs_root": BASE_DIR / "runs" / "test" if test else BASE_DIR / "runs",
        "logs_root": BASE_DIR / "logs" / "test" if test else BASE_DIR / "logs",
        "train_folder": dataset_folder / "train/images",
        "val_folder": dataset_folder / "val/images",
        "weights_folder": BASE_DIR / "weights",
        "models_folder": BASE_DIR / "models",
        "dataset_folder": dataset_folder,
    }


def _find_labelstudio_projects(ls_root: Path):
    """Return list of candidate Label Studio project folders under ls_root."""
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


def _get_dataset_label_mode(dataset_folder: Path) -> str | None:
    """Read label_mode from metadata.json if available."""
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
    """Return True if the given model/arch family is an OBB variant."""
    return bool(family and family.endswith("-obb"))


def get_args():
    """Parse and return command-line arguments for YOLO training."""
    parser = argparse.ArgumentParser(description="YOLO Training Script")

    # ------------- CORE TRAINING MODE FLAGS -------------
    mode_group = parser.add_mutually_exclusive_group(required=False)

    mode_group.add_argument(
        "--train",
        "--transfer-learning",
        "-t",
        action="store_true",
        help="Force transfer-learning mode.",
    )

    parser.add_argument(
        "--update",
        "--upgrade",
        "-u",
        type=str,
        nargs="?",
        const=True,
        help="Update an existing model run by folder name.",
    )

    mode_group.add_argument(
        "--scratch",
        "-s",
        action="store_true",
        help="Force scratch training from architecture.",
    )

    # ------------- MODEL + ARCHITECTURE SELECTION -------------
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        help="Pretrained weights (.pt) or family name for transfer learning.",
    )

    parser.add_argument(
        "--arch",
        "--architecture",
        "--backbone",
        "-a",
        "-b",
        type=str,
        help="YOLO architecture YAML (or family) for training from scratch.",
    )

    # ------------- ADDITIONAL FLAGS -------------
    parser.add_argument(
        "--resume",
        "-r",
        action="store_true",
        help="Resume training from latest last.pt",
    )

    parser.add_argument(
        "--test",
        "-T",
        action="store_true",
        help="Debug/testing mode (fast settings)",
    )

    parser.add_argument(
        "--dataset",
        "--data",
        "-d",
        type=str,
        default=None,
        help="Dataset folder inside ./data/",
    )

    parser.add_argument(
        "--name",
        "-n",
        type=str,
        default=None,
        help="Custom run name (defaults to timestamp)",
    )

    parser.add_argument(
        "--labelstudio",
        "--labelstudio-project",
        "--project",
        "-ls",
        type=str,
        default=None,
        help="Specify a Label Studio project folder inside ~/.yolo4r/labelstudio-projects to process.",
    )       

    args = parser.parse_args()

    if not hasattr(args, "weights"):
        args.weights = None

    # ------------- DETERMINE TRAINING MODE (INITIAL) -------------
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

    # ------------- VALIDATION -------------
    custom_arch = args.arch and is_custom_yaml(args.arch, MODELS_ROOT)

    if args.model and args.arch and not custom_arch:
        # Normalize & compare official families only
        model_family, _ = normalize_model_name(args.model)
        arch_family, _ = normalize_model_name(args.arch)

        if arch_family != model_family:
            print(f"[ERROR] Cannot mix model family '{model_family}' with architecture family '{arch_family}'.")
            print("        Use a custom YAML if you want to override architectures.")
            sys.exit(1)

    # ------------- MODEL / ARCH NAME VALIDATION -------------
    if args.model:
        m = args.model.lower()
        if not (m.endswith(".pt") or m in FAMILY_TO_WEIGHTS or m in FAMILY_TO_YAML):
            print(f"[ERROR] Unknown model name '{args.model}'.")
            print("[ERROR] Valid examples include:")
            print("       - yolov8, yolov8n.pt")
            print("       - yolo11, yolo11n.pt")
            print("       - yolo12, yolo12n.pt")
            print("       - yolo11-obb, yolov8-obb")
            sys.exit(1)
   
    if args.arch and not is_custom_yaml(args.arch, MODELS_ROOT):
        if args.arch:
            a = args.arch.lower()
            if not (a.endswith(".yaml") or a in FAMILY_TO_YAML):
                print(f"[ERROR] Unknown architecture '{args.arch}'.")
                print("[ERROR] Valid architectures include:")
                print("       - yolov8, yolov8-obb")
                print("       - yolo11, yolo11-obb")
                print("       - yolo12, yolo12-obb")
                sys.exit(1)

    if args.update and args.arch:
        print("[ERROR] --update cannot be used with architecture selection.")
        sys.exit(1)

    # ---- Determine unified name for model + dataset ----
    if args.name:
        base_name = args.name.strip()
    else:
        base_name = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Safe-increment function
    def _increment_name(root: Path, name: str) -> str:
        proposed = name
        i = 1
        while (root / proposed).exists():
            proposed = f"{name}{i}"
            i += 1
        return proposed

    # Compute final resolved name
    final_name = _increment_name(BASE_DIR / "data", base_name)
    args.final_name = final_name
    args.name = final_name

        # ------------- DATASET HANDLING -------------
    data_root = BASE_DIR / "data"
    data_root.mkdir(exist_ok=True)

    # Ensure Label Studio root exists
    LS_ROOT.mkdir(exist_ok=True)

    # ------ CASE 1: USER SUPPLIED DATASET DIRECTLY ------
    if args.dataset:
        dataset_folder = data_root / args.dataset
        if not dataset_folder.exists():
            print(f"[ERROR] Dataset folder not found: {dataset_folder}")
            sys.exit(1)

        DATA_YAML = dataset_folder / "data.yaml"
        if not DATA_YAML.exists():
            print(f"[ERROR] data.yaml not found in dataset folder: {DATA_YAML}")
            sys.exit(1)

    # ------ CASE 2: USER EXPLICITLY REQUESTED LABEL STUDIO PROJECT ------
    elif args.labelstudio is not None:

        # If user passed -ls with no name → use newest LS project
        if args.labelstudio is True or args.labelstudio == "":
            ls_projects = _find_labelstudio_projects(LS_ROOT)
            if not ls_projects:
                print("[ERROR] No Label Studio projects found in labelstudio-projects/")
                sys.exit(1)

            newest = sorted(ls_projects, key=lambda x: x.stat().st_mtime, reverse=True)[0]
            print(f"[DATA] Using newest Label Studio project: {newest}")
            dataset_folder, DATA_YAML = process_labelstudio_project(
                newest, data_root, dataset_name=args.final_name
            )

        # -ls somefolder
        else:
            specific = LS_ROOT / args.labelstudio
            if not specific.exists():
                print(f"[ERROR] Specified Label Studio project not found: {specific}")
                sys.exit(1)

            print(f"[DATA] Processing specified Label Studio project: {specific}")
            dataset_folder, DATA_YAML = process_labelstudio_project(
                specific, data_root, dataset_name=args.final_name
            )

    # ------ CASE 3: NO LS REQUEST — USE LOCAL DATASETS ONLY -----
    else:
        all_datasets = [d for d in data_root.iterdir() if d.is_dir()]

        if len(all_datasets) == 0:
            print("[ERROR] No datasets exist. Provide --dataset or use --labelstudio to process a project.")
            sys.exit(1)

        elif len(all_datasets) == 1:
            dataset_folder = all_datasets[0]
            DATA_YAML = dataset_folder / "data.yaml"
            print(f"[DATA] Auto-selected dataset: {dataset_folder.name}")

        else:
            print("[ERROR] Multiple datasets detected; specify with --dataset or --data.")
            print("Available datasets:", [d.name for d in all_datasets])
            sys.exit(1)

    # Final validation
    if not DATA_YAML.exists():
        print(f"[ERROR] data.yaml not found in: {DATA_YAML}")
        sys.exit(1)

    # ---- Dataset label mode (HBB vs OBB) ----
    label_mode = _get_dataset_label_mode(dataset_folder)
    dataset_is_obb = (label_mode == "obb") if label_mode is not None else None

    # ------------- PATH SETUP -------------
    paths = get_training_paths(dataset_folder, test=args.test)
    paths["weights_folder"].mkdir(parents=True, exist_ok=True)
    paths["models_folder"].mkdir(parents=True, exist_ok=True)

    # ------------- REQUESTED FAMILIES (MODEL / ARCH) -------------
    requested_model_family = None
    if args.model:
        requested_model_family, _ = normalize_model_name(args.model)

    if args.arch:
        if custom_arch:
            # Custom YAML: treat architecture family as the raw filename (for logging only)
            requested_arch_family = None
        else:
            requested_arch_family, _ = normalize_model_name(args.arch)
    elif requested_model_family:
        requested_arch_family = requested_model_family
    else:
        requested_arch_family = "yolo11"

    # ---- Special case: yolo12-obb has no pretrained weights ----
    if not custom_arch:
        if args.model and requested_arch_family:
            special_y12obb = (requested_model_family == "yolo12-obb")
            if requested_arch_family != requested_model_family and not special_y12obb:
                print(f"[ERROR] Architecture '{requested_arch_family}' does not match model family '{requested_model_family}'.")
                sys.exit(1)

    # ------------- STRICT MODEL/ARCH PAIRING (before fallback) -------------
    if args.model and requested_arch_family:
        special_y12obb = (requested_model_family == "yolo12-obb")
        if requested_arch_family != requested_model_family and not special_y12obb:
            print(f"[ERROR] Architecture '{requested_arch_family}' does not match model family '{requested_model_family}'.")
            sys.exit(1)

    # ------------- INITIAL EFFECTIVE FAMILIES -------------
    # Architecture family always comes from requested arch (or default yolo11)
    arch_family = requested_arch_family

    # Weight family is only used when not training from scratch
    weight_family = None
    if mode != "scratch":
        if requested_model_family:
            weight_family = requested_model_family
        else:
            # Default transfer-learning family when none specified
            weight_family = "yolo11"

    # --------- OBB/HBB DATASET ENFORCEMENT (works for custom YAMLs) ---------
    if dataset_is_obb is not None:
        if not custom_arch:
            # Official families → can fallback automatically
            arch_is_obb = _family_is_obb(arch_family)
            weight_is_obb = _family_is_obb(weight_family) if weight_family else None

            fallback_family = None

            if dataset_is_obb:
                if (arch_family and not arch_is_obb) or (weight_family and weight_is_obb is False):
                    fallback_family = "yolo11-obb"
            else:
                if (arch_family and arch_is_obb) or (weight_family and weight_is_obb):
                    fallback_family = "yolo11"

            if fallback_family:
                if arch_family != fallback_family:
                    print(f"[WARN] Dataset is {label_mode.upper()}. Overriding architecture family → {fallback_family}.")
                    arch_family = fallback_family

                if mode != "scratch" and weight_family != fallback_family:
                    print(f"[WARN] Dataset is {label_mode.upper()}. Overriding weight family → {fallback_family}.")
                    weight_family = fallback_family

        else:
            # Custom YAML: we cannot fallback, but we MUST enforce compatibility
            if dataset_is_obb and args.arch and not args.arch.endswith("-obb.yaml"):
                print("[ERROR] OBB dataset requires an OBB-capable architecture.")
                sys.exit(1)

            if not dataset_is_obb and args.arch and args.arch.endswith("-obb.yaml"):
                print("[ERROR] HBB dataset cannot be trained with an OBB architecture.")
                sys.exit(1)

    # ----------- ARCHITECTURE RESOLUTION (supports custom YAML) -----------
    if custom_arch:
        # Custom YAML path resolution
        arch_lower = args.arch.lower()

        # Case 1: direct path
        if Path(arch_lower).exists():
            model_yaml = Path(arch_lower)

        # Case 2: inside models folder
        elif (paths["models_folder"] / arch_lower).exists():
            model_yaml = paths["models_folder"] / arch_lower

        else:
            print(f"[ERROR] Custom architecture YAML not found:")
            print(f"       - {arch_lower}")
            print(f"       - {paths['models_folder'] / arch_lower}")
            sys.exit(1)

    else:
        # Official YOLO family architecture
        yaml_name = FAMILY_TO_YAML.get(arch_family)
        if yaml_name is None:
            print(f"[ERROR] No architecture YAML registered for family '{arch_family}'.")
            sys.exit(1)

        model_yaml = ensure_yolo_yaml(
            paths["models_folder"] / yaml_name,
            model_type=arch_family,
        )

        if model_yaml is None:
            print(f"[ERROR] Failed to resolve architecture YAML for '{arch_family}'.")
            sys.exit(1)

    # ------------- WEIGHTS RESOLUTION (AFTER FALLBACK) -------------
    if mode != "scratch":
        if weight_family not in FAMILY_TO_WEIGHTS:
            print(f"[ERROR] No default weights registered for model family '{weight_family}'.")
            sys.exit(1)

        weight_name = FAMILY_TO_WEIGHTS[weight_family]
        args.weights = ensure_weights(
            paths["weights_folder"] / weight_name,
            model_type=weight_family,
        )
    else:
        args.weights = None

    args.model_yaml = model_yaml
    if isinstance(args.weights, str) and args.weights.endswith(".pt"):
        args.weights = Path(args.weights)

    # ------------- ATTACH RESOLVED PATHS -------------
    args.DATA_YAML = DATA_YAML
    args.train_folder = paths["train_folder"]
    args.val_folder = paths["val_folder"]
    args.dataset_folder = dataset_folder

    return args, mode
