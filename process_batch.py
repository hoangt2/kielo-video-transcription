import os
import shutil
from pathlib import Path
import time
import argparse

# ... (Imports for subtitle_generator, audio_mixer, slow_down_video remain) ...
from subtitle_generator import generate_subtitles, cleanup_temp_file
from audio_mixer import add_background_music 
from slow_down_video import slow_down_video 

# NEW IMPORTS:
from add_outro import add_outro # IMPORT NEW FUNCTION HERE
from increase_fps import increase_fps # Import FPS increase function 

# --- Configuration ---
SOURCE_DIR = Path("source")
OUTPUT_DIR = Path("output")
SUBTITLES_DIR = Path("subtitles")
TEMP_DIR = Path("temp_processing") 
TRANSLATION_MODEL = "gemini-2.5-flash"
# --- End Configuration ---


def setup_directories():
    """Ensure all required directories exist."""
    SOURCE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    SUBTITLES_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True) # Create the new temporary folder
    print(f"Directories checked/created: {SOURCE_DIR.name}, {OUTPUT_DIR.name}, {SUBTITLES_DIR.name}, {TEMP_DIR.name}")


def batch_process_videos(add_subtitles=True, add_slowdown=True, add_music=True, add_outro_step=True, add_fps=True):
    """
    Loops through videos and performs selected processing steps.
    
    Args:
        add_subtitles (bool): Whether to add Finnish/English subtitles. Default is True.
        add_slowdown (bool): Whether to slow down video by 20%. Default is True.
        add_music (bool): Whether to add background music. Default is True.
        add_outro_step (bool): Whether to add outro video. Default is True.
        add_fps (bool): Whether to increase FPS to60. Default is True.
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
        
        # Generate output filename with appropriate prefix
        base_name = video_file_path.stem  # Original filename without extension
        if add_outro_step:
            output_filename = f"social_media_daily_vocab_fi_{base_name}.mp4"
        else:
            output_filename = f"daily_vocab_fi_{base_name}.mp4"
        
        # Define paths
        subtitled_video_path = OUTPUT_DIR / video_file_path.name  # Temporary file, original name
        slowed_video_path = TEMP_DIR / video_file_path.name  # Temporary file
        final_output_video_path = OUTPUT_DIR / output_filename  # Final output with prefix
        ass_file_in_source = video_file_path.with_suffix(".ass")
        
        # --- STEP 1: Subtitling ---
        if add_subtitles:
            print("Subtitling Step...")
            # Reads from /source, writes subtitled video to /output (File A)
            generate_subtitles(
                str(video_file_path),        
                str(subtitled_video_path),   
                translation_model=TRANSLATION_MODEL,
                subtitle_folder=str(SUBTITLES_DIR)
            )
            print("Subtitling Step Complete.")
        else:
            print("⏭️  Skipping subtitling (--add-subtitles not specified)")
            # Copy original video to output for next steps
            shutil.copy(str(video_file_path), str(subtitled_video_path))
        
        # Check if the subtitled file exists to proceed
        if not subtitled_video_path.exists():
            print("🛑 Cannot proceed: Subtitled video not found after Step 1.")
            continue
        
        # --- STEP 2: Slow Down Video (20%) ---
        if add_slowdown:
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
        else:
            print("\n⏭️  Skipping video slowdown (--add-slowdown not specified)")
            video_input_for_mixing = subtitled_video_path

        # --- STEP 3: Adding Background Music ---
        if add_music:
            print("\nAudio Mixing Step...")
            
            # Reads from File B (or File A), writes final output to /output (File C)
            if video_input_for_mixing.exists():
                add_background_music(
                    input_video_path=video_input_for_mixing, 
                    final_output_path=final_output_video_path 
                )
            else:
                print("Skipping audio mixing: Input video for mixing not found.")
        else:
            print("\n⏭️  Skipping background music (--add-music not specified)")
            # Copy video to final output path for next steps
            if video_input_for_mixing.exists():
                shutil.copy(str(video_input_for_mixing), str(final_output_video_path))

        # --- STEP 4: Add Outro ---
        if add_outro_step:
            print("\nOutro Addition Step...")
            
            # Reads from /output (File C), writes back to /output (Overwrites File C)
            if final_output_video_path.exists():
                add_outro(
                    input_video_path=final_output_video_path,
                    final_output_path=final_output_video_path
                )
            else:
                print("Skipping outro addition: Mixed video not found in /output.")
        else:
            print("\n⏭️  Skipping outro addition (--add-outro not specified)")

        # --- STEP 5: Increase FPS to 60 ---
        if add_fps:
            print("\nFPS Enhancement Step...")
            
            # Reads from /output (File C), writes back to /output (Overwrites File C)
            if final_output_video_path.exists():
                increase_fps(
                    input_video_path=final_output_video_path,
                    output_video_path=final_output_video_path,
                    target_fps=60
                )
            else:
                print("Skipping FPS increase: Final video not found in /output.")
        else:
            print("\n⏭️  Skipping FPS enhancement (--add-fps not specified)")

        # --- STEP 6: Cleanup ASS file and Temp Video ---
        
        # Move the .ass file from /source to /subtitles
        if ass_file_in_source.exists():
            target_ass_path = SUBTITLES_DIR / ass_file_in_source.name
            shutil.move(str(ass_file_in_source), str(target_ass_path))
            print(f"-> Moved subtitle file to: {target_ass_path.name}")
        
        # Clean up the intermediate (slowed) video file
        cleanup_temp_file(slowed_video_path)
        print(f"-> Cleaned up temporary slowed video: {slowed_video_path.name}")
        
        # Clean up the original subtitled file if final output has different name
        if subtitled_video_path != final_output_video_path and subtitled_video_path.exists():
            cleanup_temp_file(subtitled_video_path)
            print(f"-> Cleaned up temporary subtitled video: {subtitled_video_path.name}")


    # Clean up the entire temp directory at the end of the batch
    shutil.rmtree(TEMP_DIR)
    print(f"\n-> Removed temporary directory: {TEMP_DIR.name}")

    total_time = time.time() - total_start_time
    print("\n" + "*"*50)
    print(f"Batch processing complete! Processed {len(video_files)} video(s).")
    print(f"Total elapsed time: {total_time:.2f} seconds.")
    print(f"Final videos are in the '/output' folder.")
    print("*"*50)


def main():
    """Parse command-line arguments and run batch processing."""
    parser = argparse.ArgumentParser(
        description="Batch process videos with subtitles, slowdown, music, outro, and FPS enhancement.",
        epilog="If no --add-* flags are specified, all steps are enabled by default."
    )
    parser.add_argument(
        "--add-subtitles",
        action="store_true",
        help="Add Finnish/English subtitles to videos"
    )
    parser.add_argument(
        "--add-slowdown",
        action="store_true",
        help="Slow down video by 20%%"
    )
    parser.add_argument(
        "--add-music",
        action="store_true",
        help="Add random background music from /presets"
    )
    parser.add_argument(
        "--add-outro",
        action="store_true",
        help="Append outro video (uses 'social_media_daily_vocab_fi_' prefix)"
    )
    parser.add_argument(
        "--add-fps",
        action="store_true",
        help="Increase FPS to 60using motion interpolation"
    )
    
    args = parser.parse_args()
    
    # If no flags specified, enable all steps (default behavior)
    any_flag_set = any([args.add_subtitles, args.add_slowdown, args.add_music, args.add_outro, args.add_fps])
    
    if any_flag_set:
        # Use specified flags
        batch_process_videos(
            add_subtitles=args.add_subtitles,
            add_slowdown=args.add_slowdown,
            add_music=args.add_music,
            add_outro_step=args.add_outro,
            add_fps=args.add_fps
        )
    else:
        # No flags = all steps enabled (original behavior)
        batch_process_videos(
            add_subtitles=True,
            add_slowdown=True,
            add_music=True,
            add_outro_step=True,
            add_fps=True
        )


if __name__ == "__main__":
    main()