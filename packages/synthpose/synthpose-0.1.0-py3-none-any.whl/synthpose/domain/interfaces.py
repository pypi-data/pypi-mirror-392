from abc import ABC, abstractmethod
from typing import Iterator, List, Tuple
from pathlib import Path
import numpy as np

from synthpose.domain.entities import FrameData, BBox, PoseResult, Person

class IVideoSource(ABC):
    @abstractmethod
    def open(self) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass
    
    @abstractmethod
    def read(self) -> Iterator[FrameData]:
        pass
        
    @property
    @abstractmethod
    def meta(self) -> dict:
        """Return fps, width, height, total_frames"""
        pass

class IVideoSink(ABC):
    @abstractmethod
    def open(self, width: int, height: int, fps: float) -> None:
        pass
        
    @abstractmethod
    def write(self, frame_data: FrameData) -> None:
        pass
        
    @abstractmethod
    def close(self) -> None:
        pass

class IPersonDetector(ABC):
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[BBox]:
        """
        Detect people in the image.
        Returns a list of BBox objects.
        """
        pass

class IPoseEstimator(ABC):
    @abstractmethod
    def estimate(self, image: np.ndarray, bboxes: List[BBox]) -> List[PoseResult]:
        """
        Estimate pose for each person bounding box.
        Returns a list of PoseResult objects, corresponding to the input bboxes.
        """
        pass

class IResultWriter(ABC):
    @abstractmethod
    def save_frame_result(self, frame_id: int, persons: List[Person]) -> None:
        pass

