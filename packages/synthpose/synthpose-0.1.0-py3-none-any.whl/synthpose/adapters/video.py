import cv2
from pathlib import Path
from typing import Iterator
import numpy as np

from synthpose.domain.interfaces import IVideoSource, IVideoSink
from synthpose.domain.entities import FrameData

class OpenCVVideoSource(IVideoSource):
    def __init__(self, path: Path):
        self.path = path
        self.cap = None
        self._meta = {}

    def open(self) -> None:
        self.cap = cv2.VideoCapture(str(self.path))
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {self.path}")
        
        self._meta = {
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "total_frames": int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        }

    def close(self) -> None:
        if self.cap:
            self.cap.release()

    def read(self) -> Iterator[FrameData]:
        if not self.cap:
            self.open()
            
        frame_idx = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Original code did BGR -> RGB here, but it's better to do it in the detector/estimator adapter if needed
            # However, PIL usually wants RGB.
            # Let's convert to RGB here to standardize "Image" entity as RGB numpy array
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            yield FrameData(
                frame_id=frame_idx,
                image=frame_rgb,
                metadata={"original_bgr": frame} # Keep original for writing if needed to avoid double conversion loss
            )
            frame_idx += 1

    @property
    def meta(self) -> dict:
        return self._meta


class OpenCVVideoSink(IVideoSink):
    def __init__(self, path: Path):
        self.path = path
        self.writer = None

    def open(self, width: int, height: int, fps: float) -> None:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(str(self.path), fourcc, fps, (width, height))

    def write(self, frame_data: FrameData) -> None:
        if self.writer:
            # Expecting RGB image in frame_data.image, need to convert to BGR for OpenCV
            # Or check if original BGR is available
            if "original_bgr" in frame_data.metadata and frame_data.image is frame_data.metadata.get("visualization_result", None):
                 # If visualization result is stored in metadata? 
                 # No, usually visualization overwrites the image.
                 pass

            # Assume frame_data.image is the one we want to write (potentially visualized)
            # It is RGB (because our source produces RGB), so we must convert to BGR
            frame_bgr = cv2.cvtColor(frame_data.image, cv2.COLOR_RGB2BGR)
            self.writer.write(frame_bgr)

    def close(self) -> None:
        if self.writer:
            self.writer.release()

