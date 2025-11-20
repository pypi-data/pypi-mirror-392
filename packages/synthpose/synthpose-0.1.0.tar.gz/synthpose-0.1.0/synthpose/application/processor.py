import time
import cv2
from pathlib import Path
from typing import Optional
import numpy as np

from synthpose.infrastructure.config import Settings
from synthpose.domain.entities import Person, FrameData
from synthpose.adapters.video import OpenCVVideoSource, OpenCVVideoSink
from synthpose.adapters.detectors import RTDetrPersonDetector
from synthpose.adapters.estimators import VitPoseEstimator
from synthpose.adapters.visualization import Visualizer
from synthpose.adapters.serializers import OpenPoseResultWriter

class VideoProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        
        # Initialize Adapters
        self.video_source = OpenCVVideoSource(settings.input_video)
        
        # Detect output paths
        if settings.output_video is None:
            # input.mp4 -> input_output.mp4
            stem = settings.input_video.stem
            parent = settings.input_video.parent
            self.output_video_path = parent / f"{stem}_output.mp4"
        else:
            self.output_video_path = settings.output_video
            
        self.video_sink = OpenCVVideoSink(self.output_video_path)
        
        if settings.json_output_dir is None:
            # input.mp4 -> pose/input_json/
            # Following the original logic:
            # pose_dir = input/../../pose
            # json_output_dir = pose_dir/{stem}_json
            # This is a bit specific to the user's folder structure.
            # Let's try to recreate it or just use a sibling folder.
            # Original: os.path.abspath(os.path.join(INPUT_VIDEO, '..', '..', 'pose'))
            pose_dir = settings.input_video.parent.parent / "pose"
            stem = settings.input_video.stem
            self.json_output_dir = pose_dir / f"{stem}_json"
        else:
            self.json_output_dir = settings.json_output_dir
            
        self.result_writer = OpenPoseResultWriter(self.json_output_dir)
        
        # Models
        print(f"Loading models on {settings.device}...")
        self.detector = RTDetrPersonDetector(
            model_name=settings.det_model_name,
            device=settings.device,
            threshold=settings.det_threshold
        )
        
        pose_model_name = (
            settings.pose_model_huge_name 
            if settings.mode == "huge" 
            else settings.pose_model_base_name
        )
        self.estimator = VitPoseEstimator(
            model_name=pose_model_name,
            device=settings.device
        )
        
        self.visualizer = Visualizer(
            radius=settings.vis_radius,
            stick_width=settings.vis_stick_width,
            kpt_threshold=settings.kpt_threshold,
            show_weight=settings.vis_show_weight
        )
        print("Models loaded.")

    def run(self):
        self.video_source.open()
        meta = self.video_source.meta
        
        print(f"Processing {self.settings.input_video}")
        print(f"Video Info: {meta['width']}x{meta['height']} @ {meta['fps']} FPS")
        
        self.video_sink.open(
            width=meta['width'],
            height=meta['height'],
            fps=meta['fps']
        )
        
        inference_times = []
        
        try:
            for frame_data in self.video_source.read():
                start_time = time.time()
                
                # 1. Detect
                bboxes = self.detector.detect(frame_data.image)
                
                persons = []
                if not bboxes:
                    # Save empty result
                    self.result_writer.save_frame_result(frame_data.frame_id, [])
                    # Write original frame (or visualized with nothing)
                    self.video_sink.write(frame_data)
                    
                    # Display
                    frame_bgr = cv2.cvtColor(frame_data.image, cv2.COLOR_RGB2BGR)
                    cv2.imshow('SynthPose', frame_bgr)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue

                # 2. Estimate
                pose_results = self.estimator.estimate(frame_data.image, bboxes)
                
                # 3. Match pose results to persons
                # Estimator returns results corresponding to bboxes order
                for i, pose_result in enumerate(pose_results):
                    person = Person(
                        id=i, # Simple index ID for now
                        bbox=bboxes[i],
                        pose=pose_result
                    )
                    persons.append(person)
                
                inference_time = time.time() - start_time
                inference_times.append(inference_time)
                
                # 4. Save JSON
                self.result_writer.save_frame_result(frame_data.frame_id, persons)
                
                # 5. Visualize
                vis_image = self.visualizer.draw(frame_data.image, persons)
                
                # 6. Write Video
                # Create a new FrameData for the visualized frame
                vis_frame_data = FrameData(
                    frame_id=frame_data.frame_id,
                    image=vis_image
                )
                self.video_sink.write(vis_frame_data)
                
                # 7. Display (Real-time visualization)
                frame_bgr = cv2.cvtColor(vis_image, cv2.COLOR_RGB2BGR)
                cv2.imshow('SynthPose', frame_bgr)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
                if frame_data.frame_id % 10 == 0:
                    print(f"Frame {frame_data.frame_id}/{meta['total_frames']}")

        finally:
            self.video_source.close()
            self.video_sink.close()
            cv2.destroyAllWindows()
            
            if inference_times:
                avg_time = sum(inference_times) / len(inference_times)
                fps = 1.0 / avg_time
                print(f"Done. Avg FPS: {fps:.2f}")

