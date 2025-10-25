import ffmpeg
from pathlib import Path
import shutil
import os

# Define the speed factor:
# 1.0 / (1.0 - 0.20) = 1.0 / 0.8 = 1.25. 
# This means every presentation timestamp will be 1.25 times its original value, 
# resulting in a video that is 1.25 times longer (20% slower).
SPEED_FACTOR = 1.25 

def slow_down_video(input_video_path: Path, output_video_path: Path):
    """
    Slows down the video and audio speed by 20% (to 80% of original speed).
    Writes the result to the specified output path.
    """
    
    # Check if input file exists
    if not input_video_path.exists():
        print(f"Error: Input video not found at {input_video_path}")
        return False

    print(f"Slowing down video {input_video_path.name} by 20%...")
    
    try:
        input_stream = ffmpeg.input(str(input_video_path))
        
        # 1. Video stream: Use setpts filter
        # The new presentation timestamp (PTS) is the original PTS multiplied by the speed factor.
        video_stream = input_stream.video.filter('setpts', f'{SPEED_FACTOR}*PTS')
        
        # 2. Audio stream: Use atempo filter
        # The atempo filter must be used to adjust audio speed without changing pitch.
        # It takes the inverse of the video factor: 1 / 1.25 = 0.8.
        audio_stream = input_stream.audio.filter('atempo', f'{1/SPEED_FACTOR}')
        
        # 3. Output
        (
            ffmpeg
            .output(
                video_stream,
                audio_stream,
                str(output_video_path),
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                strict='experimental',
            )
            .overwrite_output()
            .run(quiet=True)
        )
        print(f"✅ Slowdown complete. Temporary file created at {output_video_path.name}.")
        return True
        
    except ffmpeg.Error as e:
        print("FFmpeg Error during video slowdown:", e.stderr.decode() if e.stderr else str(e))
        return False
    except Exception as e:
        print("Unexpected error during video slowdown:", e)
        return False

if __name__ == "__main__":
    # Example usage for testing (assuming files are set up for batch processing)
    SOURCE_DIR = Path("source")
    TEMP_DIR = Path("temp") # Using a temp folder for testing
    TEMP_DIR.mkdir(exist_ok=True)
    
    video_to_process = "kahvila.mp4" 
    
    input_path = SOURCE_DIR / video_to_process
    output_path = TEMP_DIR / f"{Path(video_to_process).stem}_slow.mp4"

    if input_path.exists():
        slow_down_video(input_path, output_path)
    else:
        print(f"Please place {video_to_process} in the 'source' folder to test.")