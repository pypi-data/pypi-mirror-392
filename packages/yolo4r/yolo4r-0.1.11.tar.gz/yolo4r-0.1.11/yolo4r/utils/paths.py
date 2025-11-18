# utils/paths.py
from pathlib import Path
from datetime import datetime
import os, re

#  ---- UNIVERSAL YOLO4r ROOT DIRECTORY ----
BASE_DIR = Path.home() / "YOLO4r"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# ---- CORE SUBDIRECTORIES ----
DATA_DIR    = BASE_DIR / "data"
RUNS_DIR    = BASE_DIR / "runs"
LOGS_DIR    = BASE_DIR / "logs"
MODELS_DIR  = BASE_DIR / "models"
WEIGHTS_DIR = BASE_DIR / "weights"
CONFIGS_DIR = BASE_DIR / "configs"
LS_ROOT     = BASE_DIR / "labelstudio-projects"

# create directories on import
for d in [DATA_DIR, RUNS_DIR, LOGS_DIR, MODELS_DIR, WEIGHTS_DIR, CONFIGS_DIR, LS_ROOT]:
    d.mkdir(parents=True, exist_ok=True)

#  ---- RUNS DIRECTORY RESOLUTION ----
def get_runs_dir(test=False):
    if test:
        t = RUNS_DIR / "test"
        t.mkdir(exist_ok=True, parents=True)
        return t
    return RUNS_DIR

#  ---- MODEL DATA.YAML RESOLUTION ----
def get_model_data_yaml(model_folder: Path, printer=None):
    model_yaml = model_folder / "data.yaml"
    if model_yaml.exists():
        return model_yaml

    return get_latest_dataset_yaml(printer)

def get_latest_dataset_yaml(printer=None):
    if not DATA_DIR.exists():
        if printer:
            printer.warn(f"Data directory missing: {DATA_DIR}")
        return None

    dataset_dirs = [d for d in DATA_DIR.iterdir() if d.is_dir()]
    if not dataset_dirs:
        if printer:
            printer.warn(f"No datasets found in {DATA_DIR}")
        return None

    latest = max(dataset_dirs, key=lambda d: d.stat().st_mtime)
    yaml_path = latest / "data.yaml"
    if yaml_path.exists():
        return yaml_path

    if printer:
        printer.warn(f"Dataset folder missing data.yaml: {latest}")
    return None

#  ---- MODEL-SPECIFIC CONFIG ROOT ----
def get_model_config_dir(model_name: str) -> Path:
    model_name = str(model_name).strip()
    cfg = CONFIGS_DIR / model_name
    cfg.mkdir(parents=True, exist_ok=True)
    return cfg

#  ---- DETECTION OUTPUT FOLDERS ----
def get_output_folder(weights_path, source_type, source_name, test_detect=False, base_time=None):
    weights_path = Path(weights_path)

    # Parent of weights is: /runs/<run_name>/weights/
    model_folder = weights_path.parent.parent
    model_timestamp = model_folder.name

    logs_root = (LOGS_DIR / "test" if test_detect else LOGS_DIR) / model_timestamp / "measurements"

    folder_time = base_time or datetime.now()
    run_ts = folder_time.strftime("%m-%d-%Y_%H-%M-%S")

    # Clean source name
    safe_name = re.sub(r"[^\w\-\.]", "_",
                       Path(source_name).stem if source_type == "video" else source_name)

    if source_type == "video":
        base_folder = logs_root / "video-in" / safe_name / run_ts
    else:
        base_folder = logs_root / "camera-feeds" / safe_name / run_ts

    # Avoid overwriting
    original = base_folder
    suffix = 1
    while base_folder.exists():
        base_folder = original.parent / f"{run_ts}_{suffix}"
        suffix += 1

    # Subfolders
    video_folder         = base_folder / "recordings"
    scores_folder        = base_folder / "scores"
    counts_folder        = scores_folder / "counts"
    frame_counts_folder  = scores_folder / "frame-counts"
    interactions_folder  = scores_folder / "interactions"

    for d in [video_folder, scores_folder, counts_folder, frame_counts_folder, interactions_folder]:
        d.mkdir(parents=True, exist_ok=True)

    return {
        "video_folder": video_folder,
        "scores_folder": scores_folder,
        "counts": counts_folder,
        "frame-counts": frame_counts_folder,
        "interactions": interactions_folder,
        "metadata": scores_folder / f"{safe_name}_metadata.json",
        "safe_name": safe_name,
    }
