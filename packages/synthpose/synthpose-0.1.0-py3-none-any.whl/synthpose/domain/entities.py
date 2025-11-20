from dataclasses import dataclass, field
from typing import List, Optional, Any
import numpy as np

@dataclass
class Keypoint:
    x: float
    y: float
    score: float
    id: int  # COCO id 0-16 or extended

@dataclass
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float
    score: float
    label: int = 0 # 0 for person

    def to_xywh(self) -> List[float]:
        return [self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1]

    def to_xyxy(self) -> List[float]:
        return [self.x1, self.y1, self.x2, self.y2]

@dataclass
class PoseResult:
    keypoints: List[Keypoint]
    score: float
    bbox: Optional[BBox] = None

@dataclass
class Person:
    id: int
    bbox: BBox
    pose: Optional[PoseResult] = None

@dataclass
class FrameData:
    frame_id: int
    image: Any # numpy array (H, W, C)
    metadata: dict = field(default_factory=dict)

