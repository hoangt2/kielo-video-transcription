#!/usr/bin/env python3
"""
Increases video FPS to 60 using FFmpeg motion interpolation.
"""
import subprocess
from pathlib import Path


def increase_fps(input_video_path, output_video_path=None, target_fps=60):
    """
    Increases the video's FPS to the target FPS using motion interpolation.
    
    Args:
        input_video_path: Path to the input video (can be string or Path object)
        output_video_path: Path for the output video. If None, overwrites input file.
        target_fps: Target frames per second (default: 60)
    
    Returns:
        bool: True if successful, False otherwise
    """
    input_path = Path(input_video_path)
    
    if not input_path.exists():
        print(f"❌ Input video not found: {input_path}")
        return False
    
    # Determine if we need to overwrite the input file
    if output_video_path is None:
        final_output_path = input_path
        overwrite_input = True
    else:
        final_output_path = Path(output_video_path)
        # Check if input and output are the same
        overwrite_input = (input_path.resolve() == final_output_path.resolve())
    
    # Always use a temporary file to avoid FFmpeg's "cannot edit in-place" error
    temp_output_path = final_output_path.with_name(f"temp_fps_{final_output_path.name}")
    
    print(f"📹 Increasing FPS to {target_fps} fps for: {input_path.name}")
    
    # FFmpeg command with minterpolate filter for motion interpolation
    # Using mci (Motion Compensated Interpolation) mode for best quality
    command = [
        "ffmpeg",
        "-i", str(input_path),
        "-filter:v", f"minterpolate='fps={target_fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1'",
        "-c:a", "copy",  # Copy audio without re-encoding
        "-y",  # Overwrite output file if it exists
        str(temp_output_path)  # Always write to temp file first
    ]
    
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if temp_output_path.exists():
            # Move temp file to final destination
            import shutil
            shutil.move(str(temp_output_path), str(final_output_path))
            print(f"✅ FPS increased to {target_fps} fps: {final_output_path.name}")
            return True
        else:
            print(f"❌ Output file was not created: {temp_output_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error during FPS increase:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error during FPS increase: {e}")
        return False
    finally:
        # Clean up temp file if it still exists
        if temp_output_path.exists():
            import os
            os.remove(temp_output_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python increase_fps.py <input_video> [output_video] [target_fps]")
        print("Example: python increase_fps.py input.mp4")
        print("Example: python increase_fps.py input.mp4 output.mp4 60")
        sys.exit(1)
    
    input_video = sys.argv[1]
    output_video = sys.argv[2] if len(sys.argv) > 2 else None
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    
    success = increase_fps(input_video, output_video, fps)
    sys.exit(0 if success else 1)
