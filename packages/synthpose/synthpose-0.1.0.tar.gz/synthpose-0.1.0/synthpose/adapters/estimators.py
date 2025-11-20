import torch
import numpy as np
from PIL import Image
from typing import List
from transformers import AutoProcessor, VitPoseForPoseEstimation

from synthpose.domain.interfaces import IPoseEstimator
from synthpose.domain.entities import BBox, PoseResult, Keypoint

class VitPoseEstimator(IPoseEstimator):
    def __init__(self, model_name: str, device: str = "cuda"):
        self.device = device
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = VitPoseForPoseEstimation.from_pretrained(model_name).to(device)

    def estimate(self, image: np.ndarray, bboxes: List[BBox]) -> List[PoseResult]:
        if not bboxes:
            return []
            
        pil_image = Image.fromarray(image)
        
        # Prepare boxes in COCO format [x, y, w, h]
        boxes_coco = [bbox.to_xywh() for bbox in bboxes]
        boxes_array = np.array(boxes_coco)
        
        # VitPose processor expects list of numpy arrays (one per image)
        inputs = self.processor(pil_image, boxes=[boxes_array], return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        pose_results = self.processor.post_process_pose_estimation(outputs, boxes=[boxes_array])
        image_pose_result = pose_results[0]
        
        results = []
        for i, pose_data in enumerate(image_pose_result):
            # pose_data has "keypoints" [17, 2] and "scores" [17] (or more keypoints)
            kpts_raw = pose_data["keypoints"]
            scores_raw = pose_data["scores"]
            
            # Ensure we work with numpy arrays (move from GPU if needed)
            if isinstance(kpts_raw, torch.Tensor):
                kpts_raw = kpts_raw.detach().cpu().numpy()
            if isinstance(scores_raw, torch.Tensor):
                scores_raw = scores_raw.detach().cpu().numpy()
            
            keypoints = []
            for kid, (kpt, score) in enumerate(zip(kpts_raw, scores_raw)):
                keypoints.append(Keypoint(
                    x=float(kpt[0]),
                    y=float(kpt[1]),
                    score=float(score),
                    id=kid
                ))
            
            # Calculate overall pose score (e.g., mean confidence)
            pose_score = float(np.mean(scores_raw))
            
            results.append(PoseResult(
                keypoints=keypoints,
                score=pose_score,
                bbox=bboxes[i]
            ))
            
        return results

