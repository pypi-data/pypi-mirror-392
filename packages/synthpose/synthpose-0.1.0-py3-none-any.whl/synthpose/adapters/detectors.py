import torch
import numpy as np
from PIL import Image
from typing import List
from transformers import AutoProcessor, RTDetrForObjectDetection

from synthpose.domain.interfaces import IPersonDetector
from synthpose.domain.entities import BBox

class RTDetrPersonDetector(IPersonDetector):
    def __init__(self, model_name: str, device: str = "cuda", threshold: float = 0.3):
        self.device = device
        self.threshold = threshold
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = RTDetrForObjectDetection.from_pretrained(model_name).to(device)

    def detect(self, image: np.ndarray) -> List[BBox]:
        # image is RGB numpy array
        pil_image = Image.fromarray(image)
        
        inputs = self.processor(images=pil_image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        target_sizes = torch.tensor([pil_image.size[::-1]]) # (height, width)
        
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=self.threshold
        )
        result = results[0]
        
        # Label 0 is person in COCO
        mask = result["labels"] == 0
        boxes = result["boxes"][mask].cpu().numpy()
        scores = result["scores"][mask].cpu().numpy()
        
        bboxes = []
        for box, score in zip(boxes, scores):
            # RTDetr outputs [x1, y1, x2, y2]
            bboxes.append(BBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
                score=float(score),
                label=0
            ))
            
        return bboxes

