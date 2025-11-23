# Video Transcription and Processing Pipeline

This project automates the processing of Finnish videos by generating bilingual subtitles (Finnish/English), slowing down the playback, adding background music, and appending an outro.

## Features

- **Automatic Subtitling**: Transcribes Finnish audio using `faster-whisper` and translates it to English using Google Gemini (`gemini-2.5-flash`).
- **Video Slowdown**: Slows down the video and audio by 20% to make it easier for learners to follow.
- **Audio Mixing**: Adds background music with automatic volume ducking.
- **Outro Addition**: Appends a standard outro video to the end.
- **Batch Processing**: Processes all videos in the `source` directory automatically.

## Prerequisites

- **Python 3.8+**
- **FFmpeg**: Must be installed and available in your system PATH.
- **Google Gemini API Key**: Required for translation. Set the `GEMINI_API_KEY` environment variable.

## Setup

1.  **Create and Activate Virtual Environment**:

    **PowerShell**:
    ```powershell
    python -m venv .venv
    . .\.venv\Scripts\Activate.ps1
    ```

    **Command Prompt**:
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
    - `background_music.mp3`: Background music file.
    - `outro.mp4`: Outro video file.

## Usage

1.  **Place Videos**: Put your source video files (`.mp4`, `.mov`, `.avi`, `.mkv`) in the `source` directory.
2.  **Run the Batch Processor**:
    ```bash
    python process_batch.py
    ```
3.  **Output**: Processed videos will be saved in the `output` directory. Subtitle files (`.ass`) are saved in the `subtitles` directory.

## Scripts Overview

-   **`process_batch.py`**: The main orchestrator script. It finds videos in `source`, runs them through the pipeline, and manages temporary files.
-   **`subtitle_generator.py`**: Handles audio extraction, transcription (Whisper), translation (Gemini), and subtitle embedding.
-   **`slow_down_video.py`**: Slows down video and audio by 20%.
-   **`audio_mixer.py`**: Mixes background music with the video's audio.
-   **`add_outro.py`**: Appends the outro video.
