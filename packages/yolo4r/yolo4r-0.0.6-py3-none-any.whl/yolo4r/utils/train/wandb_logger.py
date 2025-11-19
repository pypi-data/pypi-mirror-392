# utils/train/wandb_logger.py
import wandb, warnings, os
from pathlib import Path

def init_wandb(run_name: str, project: str = "yolo-train", entity: str = "trevelline-lab"):
    """Initialize W&B tracking for a given run name, forcing logs into ~/.yolo4r/logs/wandb."""
    warnings.filterwarnings("ignore", category=UserWarning, message=".*reinit.*")

    wandb_dir = Path("/data") / os.environ.get("USER", "unknown") / "YOLO4r" / "wandb"
    wandb_dir.mkdir(parents=True, exist_ok=True)

    run = wandb.init(
        project=project,
        entity=entity,
        name=run_name,
        dir=str(wandb_dir),
        reinit=True
    )

    print(f"[INFO] W&B logging enabled for run: {run_name}")
    print(f"[INFO] W&B directory: {wandb_dir}")

    return run
