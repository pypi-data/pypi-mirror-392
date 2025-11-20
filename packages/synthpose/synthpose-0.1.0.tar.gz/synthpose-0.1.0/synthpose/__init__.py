__version__ = "0.1.0"

from synthpose.infrastructure.config import Settings
from synthpose.application.processor import VideoProcessor
from synthpose.domain.entities import Person, Keypoint, BBox, PoseResult

__all__ = [
    "Settings",
    "VideoProcessor",
    "Person",
    "Keypoint",
    "BBox",
    "PoseResult",
]

