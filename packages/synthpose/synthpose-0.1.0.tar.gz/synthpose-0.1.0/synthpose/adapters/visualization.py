import cv2
import numpy as np
import math
from typing import List, Tuple

from synthpose.domain.entities import Person, Keypoint, BBox

# Constants adapted from original SynthPose.py
KEYPOINT_EDGES = [
    [15, 13], [13, 11], [16, 14], [14, 12], [11, 12],
    [5, 11], [6, 12], [5, 6], [5, 7], [6, 8],
    [7, 9], [8, 10], [1, 2], [0, 1], [0, 2],
    [1, 3], [2, 4], [3, 5], [4, 6]
]

# COCO17 skeleton map to match edges to colors
COCO17_SKELETON_MAP = {
    (15, 13): 0, (13, 11): 1, (16, 14): 2, (14, 12): 3, (11, 12): 4,
    (5, 11): 5, (6, 12): 6, (5, 6): 7, (5, 7): 8, (6, 8): 9,
    (7, 9): 10, (8, 10): 11, (1, 2): 12, (0, 1): 13, (0, 2): 14,
    (1, 3): 15, (2, 4): 16, (3, 5): 17, (4, 6): 18
}

# Colors (RGB format for entities, but OpenCV uses BGR? 
# Let's assume we work in RGB space as defined in adapters/video.py)
# Original PALETTE and colors seem to be defined as [R, G, B] or similar.
# rtmlib.visualization.skeleton.coco17 import coco17
# I will use hardcoded colors to avoid rtmlib dependency for just this.
# These are approximate standard COCO colors.
COCO_COLORS = [
    [51, 153, 255],   # 0: nose
    [51, 153, 255],   # 1: left_eye
    [51, 153, 255],   # 2: right_eye
    [51, 153, 255],   # 3: left_ear
    [51, 153, 255],   # 4: right_ear
    [0, 255, 0],      # 5: left_shoulder
    [255, 128, 0],    # 6: right_shoulder
    [0, 255, 0],      # 7: left_elbow
    [255, 128, 0],    # 8: right_elbow
    [0, 255, 0],      # 9: left_wrist
    [255, 128, 0],    # 10: right_wrist
    [0, 255, 0],      # 11: left_hip
    [255, 128, 0],    # 12: right_hip
    [0, 255, 0],      # 13: left_knee
    [255, 128, 0],    # 14: right_knee
    [0, 255, 0],      # 15: left_ankle
    [255, 128, 0]     # 16: right_ankle
]

# Colors for links
LINK_COLORS_PALETTE = [
    [0, 255, 0], [0, 255, 0], [255, 128, 0], [255, 128, 0],
    [51, 153, 255], [51, 153, 255], [0, 255, 0], [255, 128, 0],
    [0, 255, 0], [255, 128, 0], [0, 255, 0], [255, 128, 0],
    [51, 153, 255], [51, 153, 255], [51, 153, 255], [51, 153, 255],
    [51, 153, 255], [51, 153, 255], [51, 153, 255]
]

def get_link_color(edge_idx: int):
    # Simplified color mapping
    if edge_idx < len(LINK_COLORS_PALETTE):
        return LINK_COLORS_PALETTE[edge_idx]
    return [255, 255, 255]

class Visualizer:
    def __init__(
        self,
        radius: int = 4,
        stick_width: int = 2,
        kpt_threshold: float = 0.3,
        show_weight: bool = False
    ):
        self.radius = radius
        self.stick_width = stick_width
        self.kpt_threshold = kpt_threshold
        self.show_weight = show_weight

    def draw(self, image: np.ndarray, persons: List[Person]) -> np.ndarray:
        """
        Draws bounding boxes and skeletons on the image.
        Image is expected to be RGB.
        """
        img = image.copy()
        
        for person in persons:
            # Draw BBox
            self._draw_bbox(img, person.bbox)
            
            # Draw Pose
            if person.pose:
                self._draw_pose(img, person.pose.keypoints)
                
        return img

    def _draw_bbox(self, image: np.ndarray, bbox: BBox, color: Tuple[int, int, int] = (0, 255, 0)):
        cv2.rectangle(
            image,
            (int(bbox.x1), int(bbox.y1)),
            (int(bbox.x2), int(bbox.y2)),
            color,
            2
        )

    def _draw_pose(self, image: np.ndarray, keypoints: List[Keypoint]):
        # Separate drawing links and points
        # Need to map keypoints by ID for easy access
        kp_map = {kp.id: kp for kp in keypoints}
        
        # Draw Links
        for edge_idx, edge in enumerate(KEYPOINT_EDGES):
            id1, id2 = edge
            if id1 in kp_map and id2 in kp_map:
                kp1 = kp_map[id1]
                kp2 = kp_map[id2]
                
                if kp1.score > self.kpt_threshold and kp2.score > self.kpt_threshold:
                    color = get_link_color(edge_idx)
                    self._draw_link(image, kp1, kp2, color)

        # Draw Points
        for kp in keypoints:
            if kp.score > self.kpt_threshold:
                color = COCO_COLORS[kp.id] if kp.id < len(COCO_COLORS) else [255, 255, 255]
                self._draw_point(image, kp, color)

    def _draw_link(self, image: np.ndarray, kp1: Keypoint, kp2: Keypoint, color: List[int]):
        x1, y1 = int(kp1.x), int(kp1.y)
        x2, y2 = int(kp2.x), int(kp2.y)
        
        if self.show_weight:
            # Complex drawing with weights (simplified port)
             cv2.line(image, (x1, y1), (x2, y2), color, thickness=self.stick_width)
        else:
            cv2.line(image, (x1, y1), (x2, y2), color, thickness=self.stick_width)

    def _draw_point(self, image: np.ndarray, kp: Keypoint, color: List[int]):
        x, y = int(kp.x), int(kp.y)
        if kp.id < 17:
            cv2.circle(image, (x, y), self.radius, color, -1)
        else:
            # Diamond for extra points
            d = self.radius // 2
            pts = np.array([
                [x, y - d],
                [x + d, y],
                [x, y + d],
                [x - d, y]
            ], np.int32)
            cv2.fillPoly(image, [pts], color)

