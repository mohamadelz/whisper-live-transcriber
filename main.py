import threading
import tempfile
import tkinter as tk
from pynput import keyboard
import sounddevice as sd
import soundfile as sf
import whisper
import pyperclip
import pyautogui
import time
import sys
import os
import json
from queue import Queue
import numpy as np
import argparse

# Parameters
SAMPLERATE = 16000  # Sample rate for recording

# Config file path
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".whispertranscriber")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Global Whisper model
whisper_model = None
model_name = "base"  # Default model

# Default hotkey
hotkey_name = "alt"  # Default is alt/option key
hotkey = keyboard.Key.alt_l  # Default left alt key

# Recording control
is_recording = False
recording_data = []
recording_thread = None
stop_recording = threading.Event()


def load_config():
    """Load configuration from file."""
    global model_name, hotkey_name, hotkey

    # Create config directory if it doesn't exist
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    # Load config if it exists
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                model_name = config.get("model", model_name)
                hotkey_name = config.get("hotkey", hotkey_name)
                custom_hotkey_str = config.get("custom_hotkey")

                if custom_hotkey_str:
                    # Use custom hotkey string if available
                    try:
                        # Try to get the hotkey from the saved string representation
                        hotkey = eval(custom_hotkey_str)
                        hotkey_name = "custom"
                        print(f"Loaded custom hotkey from config file")
                    except Exception as e:
                        print(f"Error loading custom hotkey: {e}")
                        set_hotkey_from_name(hotkey_name)
                else:
                    # Set the correct hotkey object based on the name
                    set_hotkey_from_name(hotkey_name)

                print(
                    f"Loaded model '{model_name}' and hotkey '{hotkey_name}' from config file"
                )
        except Exception as e:
            print(f"Error loading config: {e}")


def get_hotkey_display_name(key):
    """Get a user-friendly display name for a hotkey."""
    try:
        if hasattr(key, "char") and key.char:
            return f"'{key.char}' key"

        # Remove the "Key." prefix for special keys
        if hasattr(key, "_name_") and key._name_:
            name = key._name_

            # Map some keys to more readable names
            key_mapping = {
                "alt_l": "left alt/option",
                "alt_r": "right alt/option",
                "ctrl_l": "left ctrl",
                "ctrl_r": "right ctrl",
                "shift_l": "left shift",
                "shift_r": "right shift",
                "cmd_l": "left command",
                "cmd_r": "right command",
                "alt": "alt/option",
                "ctrl": "ctrl",
                "shift": "shift",
                "cmd": "command",
            }

            if name in key_mapping:
                return key_mapping[name]
            return name

        return str(key)
    except:
        return str(key)


def set_hotkey_from_name(name):
    """Set the hotkey object based on its name."""
    global hotkey
    try:
        if name == "alt" or name == "option":
            hotkey = keyboard.Key.alt_l
        elif name == "alt_r" or name == "option_r":
            hotkey = keyboard.Key.alt_r
        elif name == "ctrl":
            hotkey = keyboard.Key.ctrl_l
        elif name == "ctrl_r":
            hotkey = keyboard.Key.ctrl_r
        elif name == "shift":
            hotkey = keyboard.Key.shift_l
        elif name == "shift_r":
            hotkey = keyboard.Key.shift_r
        elif name == "cmd" or name == "command":
            hotkey = keyboard.Key.cmd_l
        elif name == "cmd_r" or name == "command_r":
            hotkey = keyboard.Key.cmd_r
        elif name == "f12":
            hotkey = keyboard.Key.f12
        elif name == "f11":
            hotkey = keyboard.Key.f11
        else:
            # Default to alt if unknown
            hotkey = keyboard.Key.alt_l
    except Exception as e:
        print(f"Error setting hotkey: {e}")
        hotkey = keyboard.Key.alt_l  # Default fallback


def save_config():
    """Save configuration to file."""
    try:
        config_data = {"model": model_name, "hotkey": hotkey_name}

        # For custom hotkeys, save the string representation
        if hotkey_name == "custom":
            config_data["custom_hotkey"] = repr(hotkey)

        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f)

        print(f"Saved model '{model_name}' and hotkey '{hotkey_name}' to config file")
    except Exception as e:
        print(f"Error saving config: {e}")


def listen_for_hotkey():
    """Listen for a key press and set it as the hotkey."""
    print("\nPress the key you want to use as the hotkey...")

    # Event to signal when we've captured a key
    key_captured = threading.Event()
    captured_key = [None]  # Use a list to store the captured key (to make it mutable)

    def on_press(key):
        # Store the key and signal that we've captured it
        captured_key[0] = key
        key_captured.set()
        return False  # Stop listener

    # Start a keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Wait for key to be pressed (with a timeout)
    key_captured.wait(timeout=10)

    if captured_key[0]:
        global hotkey, hotkey_name
        hotkey = captured_key[0]
        hotkey_name = "custom"
        display_name = get_hotkey_display_name(hotkey)
        print(f"Hotkey set to: {display_name}")
        save_config()
        return True
    else:
        print("No key was pressed within the timeout period.")
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Whisper Transcriber - Press and hold the hotkey to record and transcribe speech"
    )

    # Get available models
    available_models = whisper.available_models()

    # Available hotkeys
    available_hotkeys = [
        "alt",
        "alt_r",
        "option",
        "option_r",
        "ctrl",
        "ctrl_r",
        "shift",
        "shift_r",
        "cmd",
        "cmd_r",
        "command",
        "command_r",
        "f11",
        "f12",
    ]

    parser.add_argument(
        "--model",
        type=str,
        choices=available_models,
        default=None,  # Default is None to allow loading from config
        help=f'Whisper model to use. Available models: {", ".join(available_models)}',
    )
    parser.add_argument(
        "--hotkey",
        type=str,
        choices=available_hotkeys,
        default=None,  # Default is None to allow loading from config
        help=f'Hotkey to use for recording. Available options: {", ".join(available_hotkeys)}',
    )
    parser.add_argument(
        "--set-hotkey",
        action="store_true",
        help="Interactively set a custom hotkey by pressing the desired key",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List all available Whisper models and exit",
    )
    parser.add_argument(
        "--list-hotkeys",
        action="store_true",
        help="List all available hotkeys and exit",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.list_models:
        print("Available Whisper models:")
        for model in available_models:
            print(f"- {model}")
        sys.exit(0)

    if args.list_hotkeys:
        print("Available hotkeys:")
        for h in available_hotkeys:
            print(f"- {h}")
        sys.exit(0)

    if args.set_hotkey:
        success = listen_for_hotkey()
        if success:
            print("Hotkey has been saved and will be used for future sessions.")
        sys.exit(0)

    return args


def load_whisper_model():
    """Load the Whisper model once at startup."""
    global whisper_model, model_name
    print(f"Loading Whisper model '{model_name}' at startup...")
    whisper_model = whisper.load_model(model_name)
    print("Whisper model loaded successfully!")


def check_audio_devices():
    """Check available audio devices and print their info."""
    print("\nAvailable audio devices:")
    print(sd.query_devices())
    print("\nDefault input device:")
    print(sd.query_devices(kind="input"))


def start_recording():
    """Start recording audio in a separate thread."""
    global is_recording, recording_data, recording_thread, stop_recording

    # Reset recording data and flags
    recording_data = []
    is_recording = True
    stop_recording.clear()

    def record_callback(indata, frames, time, status):
        """Callback function for the InputStream to collect audio data."""
        if status:
            print(f"Status: {status}")
        recording_data.append(indata.copy())

    def recording_monitor():
        """Monitor the recording process."""
        try:
            # Get default input device
            device_info = sd.query_devices(kind="input")
            print(f"Using input device: {device_info['name']}")

            print("Starting audio recording...")
            print("Hold the hotkey to continue recording, release to stop.")

            # Start an input stream to capture audio
            with sd.InputStream(
                samplerate=SAMPLERATE, channels=1, callback=record_callback
            ):
                # Keep recording until the stop event is set, with no max duration
                while not stop_recording.is_set():
                    time.sleep(0.1)

            print("Recording stopped")

            # Process the recorded audio
            if len(recording_data) > 0:
                # Combine all audio chunks
                audio = np.concatenate(recording_data)

                # Save to temporary file
                audio_path = save_audio_to_temp(audio, SAMPLERATE)
                if audio_path:
                    # Transcribe the audio
                    text = transcribe_audio(audio_path)
                    if text:
                        paste_text(text)

            # Reset recording flag
            global is_recording
            is_recording = False

        except Exception as e:
            print(f"Error in recording: {e}")
            import traceback

            print(traceback.format_exc())
            is_recording = False

    # Start the recording thread
    recording_thread = threading.Thread(target=recording_monitor)
    recording_thread.daemon = True
    recording_thread.start()


def stop_recording_process():
    """Stop the recording process."""
    global is_recording, stop_recording
    if is_recording:
        print("Stopping recording...")
        stop_recording.set()


def save_audio_to_temp(audio, samplerate):
    """Save the recorded audio to a temporary .wav file."""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sf.write(temp_file.name, audio, samplerate)
        return temp_file.name
    except Exception as e:
        print(f"Error saving audio: {e}")
        return None


def transcribe_audio(audio_path):
    """Transcribe the audio using the pre-loaded Whisper model."""
    try:
        global whisper_model
        print("Transcribing audio...")
        result = whisper_model.transcribe(audio_path)
        transcription = result["text"]
        print(f"Transcription: {transcription}")
        return transcription
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def paste_text(text):
    """Copy the transcribed text to the clipboard and attempt to paste it.
    If pasting fails, the text will still be available in the clipboard.
    """
    try:
        # Always copy to clipboard first
        pyperclip.copy(text)
        print("Copied transcription to clipboard")

        # Try to paste using pyautogui
        try:
            # Short pause to ensure the clipboard has been updated
            time.sleep(0.5)
            # For macOS, use command+v
            pyautogui.hotkey("command", "v")
            print("Pasted transcription into active application")
        except Exception as paste_error:
            # If pasting fails, let the user know the text is in the clipboard
            print(f"Could not paste text: {paste_error}")
            print(
                "Transcription is available in your clipboard - use Cmd+V to paste manually"
            )

    except Exception as e:
        print(f"Error handling transcription: {e}")
        print("Try to paste manually")


def show_recording_popup():
    """Show recording popup from the main thread."""
    popup = tk.Toplevel(app)
    popup.title("Recording...")
    popup.geometry("200x50+100+100")
    popup.attributes("-topmost", True)

    label = tk.Label(
        popup, text="Recording... (Release hotkey to stop)", font=("Helvetica", 12)
    )
    label.pack(expand=True)

    # Function to check if recording has stopped
    def check_recording_status():
        if not is_recording:
            popup.destroy()
        else:
            popup.after(100, check_recording_status)

    # Start checking recording status
    popup.after(100, check_recording_status)

    return popup


def on_key_press(key):
    """Callback when a key is pressed."""
    global hotkey
    if key == hotkey and not is_recording:
        display_name = get_hotkey_display_name(hotkey)
        print(f"{display_name} pressed - Starting recording")
        app.event_generate("<<StartRecording>>", when="tail")


def on_key_release(key):
    """Callback when a key is released."""
    global hotkey
    if key == hotkey and is_recording:
        display_name = get_hotkey_display_name(hotkey)
        print(f"{display_name} released - Stopping recording")
        stop_recording_process()


def process_recording():
    """Process recording in the main thread."""
    # Show the recording popup
    popup = show_recording_popup()

    # Start the recording process
    start_recording()


if __name__ == "__main__":
    try:
        # First load config from file
        load_config()

        # Parse command line arguments
        args = parse_arguments()

        # Override model name from arguments if provided
        if args.model:
            model_name = args.model
            # Save to config for persistence
            save_config()

        # Override hotkey from arguments if provided
        if args.hotkey:
            hotkey_name = args.hotkey
            set_hotkey_from_name(hotkey_name)
            # Save to config for persistence
            save_config()

        print(f"Initializing program with model: {model_name}")
        display_name = get_hotkey_display_name(hotkey)
        print(f"Using hotkey: {display_name}")

        # Load the Whisper model at startup
        load_whisper_model()

        # Check audio devices
        check_audio_devices()

        # Create the main application window
        app = tk.Tk()
        app.title(f"Whisper Transcriber ({model_name})")
        app.geometry("1x1+0+0")  # Make it tiny and position at top-left
        app.withdraw()  # Hide the window but keep it running

        # Bind the custom event to start recording
        app.bind("<<StartRecording>>", lambda e: process_recording())

        # Create the keyboard listener for both press and release
        keyboard_listener = keyboard.Listener(
            on_press=on_key_press, on_release=on_key_release
        )
        keyboard_listener.start()

        print(
            f"\nPress and hold {display_name} to record, release to stop recording..."
        )
        print("Press Ctrl+C to exit...")

        # Run the Tkinter main loop
        app.mainloop()

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        print(traceback.format_exc())
        sys.exit(1)
