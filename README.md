# Whisper Transcriber

A lightweight open-source app to transcribe audio using OpenAI's Whisper model. This Python application listens for a customizable hotkey, records audio while the key is held down, transcribes it using Whisper, and automatically pastes the transcription into your active text field.

## Features

- **Customizable Hotkey:** Choose from predefined hotkeys or set your own custom key.
- **Press-and-Hold Recording:** Simply hold down your selected hotkey to record, and release to stop recording.
- **Model Selection:** Choose from any of Whisper's available models (tiny, base, small, medium, large).
- **Persistent Settings:** Your chosen model and hotkey are remembered between sessions.
- **Recording Indicator:** A small popup window notifies you when recording is active.
- **Auto Paste:** The transcription is copied to the clipboard and automatically pasted into the active application.
- **Clipboard Fallback:** If automatic pasting fails, the text remains in your clipboard for manual pasting.

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

1. **Basic Usage:**

   ```bash
   python main.py
   ```

   Hold down the configured hotkey (default is the Alt/Option key) to record audio. Release the key to stop recording and initiate transcription.

2. **Command Line Options:**

   ```bash
   # List all available Whisper models
   python main.py --list-models

   # Use a specific Whisper model
   python main.py --model medium

   # List all predefined hotkeys
   python main.py --list-hotkeys

   # Use a specific predefined hotkey
   python main.py --hotkey f12

   # Interactively set a custom hotkey
   python main.py --set-hotkey

   # Enable debug logging
   python main.py --debug
   ```

## Whisper Models

The application supports all Whisper models with varying capabilities:

- **tiny**: Very small and fast, basic accuracy
- **base**: Good balance of speed and accuracy (default)
- **small**: Better accuracy than base, still reasonably fast
- **medium**: High accuracy, slower loading
- **large**: Best accuracy, requires more memory

## Hotkey Options

- Use predefined hotkeys: Alt, Ctrl, Shift, Command, function keys (F11, F12)
- Set a custom hotkey with the `--set-hotkey` option

## Configuration

Your settings are automatically saved to `~/.whispertranscriber/config.json` and will persist across sessions.

## Future Enhancements

- **Improved Error Handling:** Better manage exceptions (e.g., microphone errors or transcription failures).
- **Enhanced UI:** Refine the popup window with additional information or progress indicators.
- **Custom User Settings:** Add a graphical settings interface.
- **Packaging:** Bundle the application as an executable for easier distribution.

## Contributing

Contributions are welcome! Please fork the repository, make improvements, and submit a pull request with your changes.

## License

This project is licensed under the MIT License.