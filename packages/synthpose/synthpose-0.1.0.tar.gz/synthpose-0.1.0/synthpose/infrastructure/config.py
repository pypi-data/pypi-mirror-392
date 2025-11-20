from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

class Settings(BaseSettings):
    # Hardware
    device: str = "cuda"

    # Paths
    input_video: Path = Field(..., description="Path to the input video file")
    output_video: Optional[Path] = Field(None, description="Path to the output video file. If None, derived from input.")
    json_output_dir: Optional[Path] = Field(None, description="Path to the output JSON directory. If None, derived from input.")

    # Models
    mode: str = Field("huge", pattern="^(huge|base)$")
    det_model_name: str = "PekingU/rtdetr_r50vd_coco_o365"
    pose_model_huge_name: str = "stanfordmimi/synthpose-vitpose-huge-hf"
    pose_model_base_name: str = "stanfordmimi/synthpose-vitpose-base-hf"

    # Inference Parameters
    det_threshold: float = 0.3
    kpt_threshold: float = 0.3

    # Visualization
    vis_radius: int = 4
    vis_stick_width: int = 2
    vis_show_weight: bool = False

    model_config = SettingsConfigDict(env_prefix="SYNTHPOSE_")

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)

def load_config(config_path: Optional[Path] = None, **overrides) -> Settings:
    """
    Load configuration from YAML file (optional) and override with CLI arguments.
    """
    config_data = {}
    if config_path and config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
    
    # Filter out None values from overrides
    valid_overrides = {k: v for k, v in overrides.items() if v is not None}
    config_data.update(valid_overrides)
    
    return Settings(**config_data)

