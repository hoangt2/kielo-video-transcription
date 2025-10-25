import ffmpeg
from pathlib import Path
import os
import shutil

# --- Configuration ---
PRESETS_DIR = Path("presets")
OUTRO_FILE_NAME = "outro.mp4"
# --- End Configuration ---

def add_outro(input_video_path: Path, final_output_path: Path) -> bool:
    """
    Appends a fixed outro video (outro.mp4 from /presets) to the end of the input video.
    Writes the result to the specified final output path.
    """
    
    outro_path = PRESETS_DIR / OUTRO_FILE_NAME
    
    if not input_video_path.exists():
        print(f"Error: Input video not found at {input_video_path}")
        return False
    
    if not outro_path.exists():
        print(f"Error: Outro file not found at {outro_path}")
        print(f"Please place '{OUTRO_FILE_NAME}' in the '{PRESETS_DIR.name}' folder.")
        return False

    print(f"Appending outro to video: {input_video_path.name}...")
    
    # Use a temporary output path for FFmpeg to write to, avoiding "same as input" error
    temp_output_path = final_output_path.with_name(f"temp_final_{final_output_path.name}")
    
    try:
        # Define the two inputs
        main_input = ffmpeg.input(str(input_video_path))
        outro_input = ffmpeg.input(str(outro_path))

        # Concatenate both video and audio streams
        concatenated_streams = ffmpeg.concat(
            main_input.video, main_input.audio,
            outro_input.video, outro_input.audio,
            v=1, a=1
        ).node

        video_stream = concatenated_streams[0]
        audio_stream = concatenated_streams[1]

        # Output the concatenated result
        (
            ffmpeg
            .output(
                video_stream,
                audio_stream,
                str(temp_output_path),
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                strict='experimental',
            )
            .overwrite_output()
            .run(quiet=True)
        )

        # FINAL STEP: Move the temp file to the final destination, replacing the old file
        shutil.move(str(temp_output_path), str(final_output_path))

        print(f"✅ Outro appended successfully. Final video written to: {final_output_path.name}")
        return True
        
    except ffmpeg.Error as e:
        print("FFmpeg Error during outro addition:", e.stderr.decode() if e.stderr else str(e))
        return False
    except Exception as e:
        print("Unexpected error during outro addition:", e)
        return False
    finally:
        # Ensure the temp file is cleaned up if it failed before the move
        if temp_output_path.exists():
            os.remove(temp_output_path)


if __name__ == "__main__":
    # Example usage for testing...
    # (Requires presets/outro.mp4 and a video in output/hauska.mp4)
    OUTPUT_DIR = Path("output")
    PRESETS_DIR = Path("presets")
    PRESETS_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    test_video = "hauska.mp4" 
    
    input_path = OUTPUT_DIR / test_video
    final_path = OUTPUT_DIR / test_video 

    if input_path.exists():
        add_outro(input_path, final_path)
    else:
        print(f"Please ensure a video named {test_video} is in the 'output' folder to test.")
        print(f"And place 'outro.mp4' in the 'presets' folder.")