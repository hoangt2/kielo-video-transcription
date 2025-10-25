import os
import shutil
from pathlib import Path
import time

# ... (Imports for subtitle_generator, audio_mixer, slow_down_video remain) ...
from subtitle_generator import generate_subtitles, cleanup_temp_file
from audio_mixer import add_background_music 
from slow_down_video import slow_down_video 

# NEW IMPORT:
from add_outro import add_outro # IMPORT NEW FUNCTION HERE 

# --- Configuration ---
SOURCE_DIR = Path("source")
OUTPUT_DIR = Path("output")
SUBTITLES_DIR = Path("subtitles")
TEMP_DIR = Path("temp_processing") 
TRANSLATION_MODEL = "gpt-4o-mini" 
# --- End Configuration ---


def setup_directories():
    """Ensure all required directories exist."""
    SOURCE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    SUBTITLES_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True) # Create the new temporary folder
    print(f"Directories checked/created: {SOURCE_DIR.name}, {OUTPUT_DIR.name}, {SUBTITLES_DIR.name}, {TEMP_DIR.name}")


def batch_process_videos():
    """
    Loops through videos, performs subtitling, slows down video, adds background music,
    appends outro, and moves the .ass file.
    """
    setup_directories()
    
    video_extensions = ['*.mp4', '*.mov', '*.avi', '*.mkv']
    video_files = []
    for ext in video_extensions:
        video_files.extend(SOURCE_DIR.glob(ext))
        
    if not video_files:
        print(f"No video files found in the '{SOURCE_DIR.name}' folder.")
        return

    print(f"\nFound {len(video_files)} video(s) to process.")
    total_start_time = time.time()
    
    for i, video_file_path in enumerate(video_files):
        print("\n" + "="*50)
        print(f"Processing video {i+1}/{len(video_files)}: {video_file_path.name}")
        print("="*50)
        
        # Define paths
        subtitled_video_path = OUTPUT_DIR / video_file_path.name
        slowed_video_path = TEMP_DIR / video_file_path.name
        final_output_video_path = OUTPUT_DIR / video_file_path.name
        ass_file_in_source = video_file_path.with_suffix(".ass") # Re-added here for safety
        
        # --- STEP 1: Subtitling ---
        print("Subtitling Step...")
        # Reads from /source, writes subtitled video to /output (File A)
        generate_subtitles(
            str(video_file_path),        
            str(subtitled_video_path),   
            translation_model=TRANSLATION_MODEL,
            subtitle_folder=str(SUBTITLES_DIR)
        )
        print("Subtitling Step Complete.")
        
        # Check if the subtitled file exists to proceed
        if not subtitled_video_path.exists():
            print("🛑 Cannot proceed: Subtitled video not found after Step 1.")
            continue
        
        # --- STEP 2: Slow Down Video (20%) ---
        print("\nVideo Slowdown Step...")
        
        # Reads from /output (File A), writes slowed video to /temp_processing (File B)
        slowdown_success = slow_down_video(
            input_video_path=subtitled_video_path,
            output_video_path=slowed_video_path
        )
        
        if not slowdown_success or not slowed_video_path.exists():
            print("🛑 Video slowdown failed or output file not found. Using original subtitled file for next step.")
            video_input_for_mixing = subtitled_video_path
        else:
            video_input_for_mixing = slowed_video_path # Use the newly slowed video (File B)

        # --- STEP 3: Adding Background Music ---
        print("\nAudio Mixing Step...")
        
        # Reads from File B (or File A), writes final output to /output (File C - Overwrites File A)
        if video_input_for_mixing.exists():
             add_background_music(
                input_video_path=video_input_for_mixing, 
                final_output_path=final_output_video_path 
            )
        else:
             print("Skipping audio mixing: Input video for mixing not found.")

        # --- STEP 4: Add Outro (New Last Step) ---
        print("\nOutro Addition Step...")
        
        # Reads from /output (File C), writes back to /output (Overwrites File C)
        if final_output_video_path.exists():
            add_outro(
                input_video_path=final_output_video_path,
                final_output_path=final_output_video_path
            )
        else:
            print("Skipping outro addition: Mixed video not found in /output.")


        # --- STEP 5: Cleanup ASS file and Temp Video ---
        
        # Move the .ass file from /source to /subtitles
        if ass_file_in_source.exists():
            target_ass_path = SUBTITLES_DIR / ass_file_in_source.name
            shutil.move(str(ass_file_in_source), str(target_ass_path))
            print(f"-> Moved subtitle file to: {target_ass_path.name}")
        
        # Clean up the intermediate (slowed) video file
        cleanup_temp_file(slowed_video_path)
        print(f"-> Cleaned up temporary slowed video: {slowed_video_path.name}")


    # Clean up the entire temp directory at the end of the batch
    shutil.rmtree(TEMP_DIR)
    print(f"\n-> Removed temporary directory: {TEMP_DIR.name}")

    total_time = time.time() - total_start_time
    print("\n" + "*"*50)
    print(f"Batch processing complete! Processed {len(video_files)} video(s).")
    print(f"Total elapsed time: {total_time:.2f} seconds.")
    print("Final videos (subtitled, slowed, mixed, and with outro) are in the '/output' folder.")
    print("*"*50)


if __name__ == "__main__":
    batch_process_videos()