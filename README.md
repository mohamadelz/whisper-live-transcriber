# Whisper Transcriber

A lightweight open-source app to transcribe audio using OpenAI's Whisper model. This Python prototype listens for a global hotkey, records audio for a fixed duration, transcribes it, and automatically pastes the transcription into your active text field.

## Features

- **Global Hotkey:** Press `Ctrl+Shift+R` to start recording.
- **Recording Indicator:** A small popup window notifies you when recording is active.
- **Audio Capture:** Records a 5-second audio clip (configurable) using your microphone.
- **Whisper Transcription:** Utilizes the Whisper model to convert speech to text.
- **Auto Paste:** The transcription is copied to the clipboard and automatically pasted.

## Prerequisites

- Python 3.7 or later
- A working microphone
- Supported on Windows, macOS, and Linux (some dependencies might vary slightly by OS)

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd whisper-transcriber
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   # Activate the environment:
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application:**

   ```bash
   python main.py
   ```

2. **Trigger the Transcription:**

   Press `Ctrl+Shift+R` to start recording. A small popup window will display "Recording..." for 5 seconds (or your configured duration). Once the recording finishes, the audio is transcribed, and the resulting text is automatically copied to your clipboard and pasted into the active text field.

## Configuration

- **Recording Duration:**
  Change the `DURATION` variable in `main.py` to adjust how long the app records audio.

- **Sample Rate:**
  The `SAMPLERATE` variable sets the audio sampling rate (default is 16000 Hz).

- **Hotkey:**
  The hotkey is defined using `keyboard.add_hotkey('ctrl+shift+r', on_hotkey)`. Modify this line if you prefer a different key combination.

## Future Enhancements

- **Improved Error Handling:** Better manage exceptions (e.g., microphone errors or transcription failures).
- **Enhanced UI:** Refine the popup window with additional information or progress indicators.
- **Custom User Settings:** Allow customization via a configuration file or settings GUI.
- **Packaging:** Bundle the application as an executable using PyInstaller or a similar tool for easier distribution.

## Contributing

Contributions are welcome! Please fork the repository, make improvements, and submit a pull request with your changes.

## License

This project is licensed under the MIT License.