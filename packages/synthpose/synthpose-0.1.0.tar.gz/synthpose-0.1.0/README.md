# SynthPose: Clean Architecture Implementation

A robust, modular Python package for human pose estimation using RT-DETR and VitPose. This project has been refactored to follow Clean Architecture principles, making it suitable for research, extension, and integration into larger systems (e.g., Avalonia/C# apps).

## Features

- **Clean Architecture**: Separation of concerns into Domain, Application, Adapters, and Infrastructure layers.
- **State-of-the-Art Models**: 
  - Detection: RT-DETR (`PekingU/rtdetr_r50vd_coco_o365`)
  - Pose Estimation: VitPose (`stanfordmimi/synthpose-vitpose-huge-hf` or `base`)
- **Standardized Output**: OpenPose-compatible JSON format.
- **Configurable**: Support for YAML configuration and CLI arguments.
- **Type Safe**: Fully typed codebase using Python type hints and Pydantic.

## Architecture

The project is organized as follows:

- **`domain/`**: Core business logic and entities (`FrameData`, `Person`, `Keypoint`). No external dependencies.
- **`application/`**: Use cases and orchestration (`VideoProcessor`). Depends only on Domain.
- **`adapters/`**: Implementations of interfaces (`OpenCVVideoSource`, `RTDetrPersonDetector`, `VitPoseEstimator`, `OpenPoseResultWriter`). Depends on external libraries (`torch`, `cv2`).
- **`infrastructure/`**: Configuration and Entry points (`CLI`, `Settings`).

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

```bash
# Install dependencies
poetry install
```

## Usage

### CLI

Run the processor via the `synthpose` command (defined in `pyproject.toml`):

```bash
# Basic usage
poetry run synthpose process path/to/video.mp4

# With options
poetry run synthpose process video.mp4 --mode base --device cpu

# Using a config file
poetry run synthpose process video.mp4 --config configs/default.yaml
```

### Configuration

You can use a YAML file to configure the pipeline:

```yaml
# configs/example.yaml
device: "cuda"
model_mode: "huge"
det_threshold: 0.3
vis_show_weight: true
```

## Output

- **Video**: `{input_name}_output.mp4` (Visualized result)
- **JSON**: `pose/{input_name}_json/{input_name}_{frame_id}.json` (Keypoints data)

## Testing

```bash
poetry run pytest
```

## License

MIT License

## References

- [VitPose Paper](https://arxiv.org/abs/2406.09788)
- [SynthPose Model](https://huggingface.co/stanfordmimi/synthpose-vitpose-huge-hf)
