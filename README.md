# Video Transcription and Processing Pipeline

This project automates the processing of Finnish videos by generating bilingual subtitles (Finnish/English), slowing down the playback, adding background music, and appending an outro.

## Features

- **Automatic Subtitling**: Transcribes Finnish audio using `faster-whisper` and translates it to English using Google Gemini (`gemini-2.5-flash`).
- **Video Slowdown**: Slows down the video and audio by 20% to make it easier for learners to follow.
- **Audio Mixing**: Adds background music with automatic volume ducking. Randomly selects from available music files in `/presets`.
- **Outro Addition**: Appends a standard outro video to the end (optional, configurable).
- **FPS Enhancement**: Increases video frame rate to 60 fps using motion interpolation for smoother playback.
- **Batch Processing**: Processes all videos in the `source` directory automatically.
- **Custom Output Naming**: Automatically prefixes output files based on configuration.

## Prerequisites

- **Python 3.8 - 3.13** (Python 3.14 is not yet supported due to PyAV compatibility issues)
- **FFmpeg**: Must be installed and available in your system PATH.
- **pkg-config**: Required for building PyAV on macOS/Linux.
- **Google Gemini API Key**: Required for translation. Set the `GEMINI_API_KEY` environment variable.

### Installing System Dependencies

**macOS** (using Homebrew):
```bash
brew install pkg-config ffmpeg
```

**Linux** (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install pkg-config ffmpeg
```

## Setup

1.  **Create and Activate Virtual Environment**:

    **macOS/Linux**:
    ```bash
    python3.11 -m venv .venv
    source .venv/bin/activate
    ```
    
    > **Note**: If you have Python 3.14, use `python3.11` or `python3.12` instead, as PyAV doesn't yet support Python 3.14.

    **Windows PowerShell**:
    ```powershell
    python -m venv .venv
    . .\.venv\Scripts\Activate.ps1
    ```

    **Windows Command Prompt**:
    ```cmd
    python -m venv .venv
    .venv\Scripts\activate.bat
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Create a `.env` file in the root directory (or set system env vars) with your API key:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

4.  **Prepare Assets**:
    Ensure the `presets` folder contains:
    - `background_music*.mp3`: One or more background music files (e.g., `background_music.mp3`, `background_music_1.mp3`, etc.). The program will randomly select one.
    - `outro.mp4`: Outro video file (optional, only needed if `INCLUDE_OUTRO = True`).

5.  **Outro Configuration**:
    - By default, outro video is added to all processed videos
    - To skip outro, use the `--no-outro` flag when running the script (see Usage section below)
    - Output filenames change based on whether outro is included:
      - With outro: `social_media_daily_vocab_fi_<filename>.mp4`
      - Without outro: `daily_vocab_fi_<filename>.mp4`

## Usage

1.  **Place Videos**: Put your source video files (`.mp4`, `.mov`, `.avi`, `.mkv`) in the `source` directory.

2.  **Run the Batch Processor**:
    
    **Production mode** (recommended for final output):
    ```bash
    python process_batch.py --prod
    ```
    Enables: slowdown, music, and FPS enhancement (no subtitles or outro)  
    Output: `daily_vocab_fi_<filename>.mp4`
    
    **All steps enabled** (default - no flags needed):
    ```bash
    python process_batch.py
    ```
    Enables: subtitles, slowdown, music, outro, and FPS enhancement
    
    **Select specific steps** with `--add-*` flags:
    ```bash
    # Only add subtitles
    python process_batch.py --add-subtitles
    
    # Subtitles + music (no slowdown, outro, or FPS change)
    python process_batch.py --add-subtitles --add-music
    
    # All steps except slowdown
    python process_batch.py --add-subtitles --add-music --add-outro --add-fps
    ```
    
    **Available flags**:
    | Flag | Description |
    |------|-------------|
    | `--prod` | **Production mode**: enables slowdown, music, and FPS (no subtitles/outro) |
    | `--add-subtitles` | Add Finnish/English subtitles |
    | `--add-slowdown` | Slow down video by 20% |
    | `--add-music` | Add random background music |
    | `--add-outro` | Append outro video (changes filename prefix to `social_media_daily_vocab_fi_`) |
    | `--add-fps` | Increase FPS to 60 |

3.  **Output**: Processed videos will be saved in the `output` directory. Subtitle files (`.ass`) are saved in the `subtitles` directory.
    - With `--add-outro`: `social_media_daily_vocab_fi_<filename>.mp4`
    - Without `--add-outro`: `daily_vocab_fi_<filename>.mp4`

## Scripts Overview

-   **`process_batch.py`**: The main orchestrator script. It finds videos in `source`, runs them through the pipeline, and manages temporary files.
-   **`subtitle_generator.py`**: Handles audio extraction, transcription (Whisper), translation (Gemini), and subtitle embedding.
-   **`slow_down_video.py`**: Slows down video and audio by 20%.
-   **`audio_mixer.py`**: Mixes background music with the video's audio.
-   **`add_outro.py`**: Appends the outro video.
-   **`increase_fps.py`**: Increases video frame rate to 60 fps using motion interpolation.
