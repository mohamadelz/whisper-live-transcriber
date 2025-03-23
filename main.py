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
from queue import Queue

# Parameters
SAMPLERATE = 16000  # Sample rate for recording
DURATION = 5  # Recording duration in seconds

# Global Whisper model
whisper_model = None

# Event to trigger recording
recording_event = threading.Event()


def load_whisper_model():
    """Load the Whisper model once at startup."""
    global whisper_model
    print("Loading Whisper model at startup...")
    whisper_model = whisper.load_model("base")
    print("Whisper model loaded successfully!")


def check_audio_devices():
    """Check available audio devices and print their info."""
    print("\nAvailable audio devices:")
    print(sd.query_devices())
    print("\nDefault input device:")
    print(sd.query_devices(kind="input"))


def record_audio(duration, samplerate):
    """Record audio for a given duration and sample rate."""
    try:
        print("\nStarting audio recording...")
        print(f"Duration: {duration} seconds")
        print(f"Sample rate: {samplerate} Hz")

        # Get the default input device
        device_info = sd.query_devices(kind="input")
        print(f"Using input device: {device_info['name']}")

        # Start recording
        print("Initializing recording...")
        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="float32",
        )
        print("Recording in progress...")
        sd.wait()  # Wait until recording is finished
        print("Recording finished")
        return audio
    except Exception as e:
        print(f"Error recording audio: {e}")
        print(f"Error type: {type(e)}")
        import traceback

        print(f"Traceback: {traceback.format_exc()}")
        return None


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
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def paste_text(text):
    """Copy the transcribed text to the clipboard and simulate a paste."""
    try:
        pyperclip.copy(text)
        time.sleep(0.5)
        # For macOS, use command+v
        pyautogui.hotkey("command", "v")
        print("Transcription pasted.")
    except Exception as e:
        print(f"Error pasting text: {e}")


def show_recording_popup():
    """Show recording popup from the main thread."""
    popup = tk.Toplevel(app)
    popup.title("Recording...")
    popup.geometry("200x50+100+100")
    popup.attributes("-topmost", True)

    label = tk.Label(popup, text="Recording...", font=("Helvetica", 12))
    label.pack(expand=True)

    # Close the popup after the recording duration
    popup.after(DURATION * 1000, popup.destroy)


def on_hotkey_pressed():
    """Callback for when the hotkey is pressed."""
    print("Hotkey activated")
    # Signal the main thread to show the popup and start recording
    app.event_generate("<<StartRecording>>", when="tail")


def process_recording():
    """Process recording in the main thread."""
    # First, show the recording popup
    show_recording_popup()

    # Start a thread for recording audio to prevent UI freezing
    def record_thread():
        audio = record_audio(DURATION, SAMPLERATE)
        if audio is not None:
            audio_path = save_audio_to_temp(audio, SAMPLERATE)
            if audio_path is not None:
                text = transcribe_audio(audio_path)
                if text is not None:
                    print("Transcription:", text)
                    paste_text(text)

    threading.Thread(target=record_thread, daemon=True).start()


if __name__ == "__main__":
    print(whisper.available_models())
    try:
        print("Initializing program...")

        # Load the Whisper model at startup
        load_whisper_model()

        # Check audio devices
        check_audio_devices()

        # Create the main application window
        app = tk.Tk()
        app.title("Whisper Transcriber")
        app.geometry("1x1+0+0")  # Make it tiny and position at top-left
        app.withdraw()  # Hide the window but keep it running

        # Bind the custom event to start recording
        app.bind("<<StartRecording>>", lambda e: process_recording())

        # Set up the global hotkey listener in a separate thread
        listener = keyboard.GlobalHotKeys(
            {
                "<alt_r>": on_hotkey_pressed,
                "<alt>": on_hotkey_pressed,  # Also try regular alt key
            }
        )
        listener.start()

        print("\nPress Right Option key to start recording...")
        print("Press Ctrl+C to exit...")

        # Run the Tkinter main loop
        app.mainloop()

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        print(traceback.format_exc())
        sys.exit(1)
