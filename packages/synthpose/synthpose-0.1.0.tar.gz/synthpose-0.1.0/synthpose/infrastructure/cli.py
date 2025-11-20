import typer
from pathlib import Path
from typing import Optional
from synthpose.infrastructure.config import load_config

app = typer.Typer()

@app.command()
def process(
    input_video: Path = typer.Argument(..., help="Path to input video"),
    output_video: Optional[Path] = typer.Option(None, help="Path to output video"),
    config: Optional[Path] = typer.Option(None, help="Path to configuration YAML"),
    mode: str = typer.Option("huge", help="Model mode: huge or base"),
    device: str = typer.Option("cuda", help="Device to use: cuda or cpu"),
):
    """
    Process a video to extract pose keypoints and visualize them.
    """
    try:
        settings = load_config(
            config_path=config,
            input_video=input_video,
            output_video=output_video,
            mode=mode,
            device=device
        )
        
        typer.echo(f"Processing video: {settings.input_video}")
        typer.echo(f"Using model mode: {settings.mode} on {settings.device}")
        
        from synthpose.application.processor import VideoProcessor
        processor = VideoProcessor(settings)
        processor.run()
        
        typer.echo("Processing complete.")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

