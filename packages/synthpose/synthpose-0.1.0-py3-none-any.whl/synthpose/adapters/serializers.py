import json
from pathlib import Path
from typing import List
import numpy as np
import os

from synthpose.domain.interfaces import IResultWriter
from synthpose.domain.entities import Person

class OpenPoseResultWriter(IResultWriter):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_frame_result(self, frame_id: int, persons: List[Person]) -> None:
        detections = []
        for person in persons:
            if person.pose:
                # Flatten keypoints to [x, y, score, x, y, score...]
                # Sort by ID to ensure correct order 0-16
                # Assuming keypoints are populated for all 17 COCO points?
                # If some are missing, we might need to fill with 0.
                # The original code iterates zip(keypoints, scores).
                # VitPose output usually contains all defined keypoints.
                
                # We need to make sure they are sorted by ID
                sorted_kps = sorted(person.pose.keypoints, key=lambda kp: kp.id)
                
                pose_keypoints_2d = []
                for kp in sorted_kps:
                    pose_keypoints_2d.extend([kp.x, kp.y, kp.score])
                
                detections.append({
                    "person_id": [-1],
                    "pose_keypoints_2d": pose_keypoints_2d,
                    "face_keypoints_2d": [],
                    "hand_left_keypoints_2d": [],
                    "hand_right_keypoints_2d": [],
                    "pose_keypoints_3d": [],
                    "face_keypoints_3d": [],
                    "hand_left_keypoints_3d": [],
                    "hand_right_keypoints_3d": []
                })

        json_output = {"version": 1.3, "people": detections}
        
        # Filename format: {video_name}_{frame_idx:06d}.json
        # Since we don't have video name here easily unless passed, 
        # we'll assume output_dir contains the video name prefix or similar structure.
        # However, original code did: os.path.join(json_output_dir, f'{video_name_wo_ext}_{frame_idx:06d}.json')
        # The output_dir passed to this writer should be the specific directory for the video.
        # e.g. pose/cam02_json/
        # And filenames inside are cam02_000000.json?
        # Or maybe generic frame_000000.json if the dir is specific enough.
        # Let's stick to frame_{frame_id:06d}.json or rely on caller to configure naming?
        # The interface is save_frame_result(frame_id, persons).
        # We will use a generic prefix or the parent dir name.
        
        # Let's use the directory name as the prefix if possible, or just "frame".
        # Original: cam02_json -> cam02_000000.json
        prefix = self.output_dir.name.replace("_json", "")
        filename = f"{prefix}_{frame_id:06d}.json"
        
        file_path = self.output_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(json_output, f)

