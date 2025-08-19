import os
import pyaudio
import websocket
import json
import threading
import time
import wave
from urllib.parse import urlencode
from datetime import datetime
from dotenv import load_dotenv

# ----------------- CONFIG -----------------
load_dotenv()
VOICE_API_AUTH = os.getenv("ASSEMBLY_AI_AUTH")
if not VOICE_API_AUTH:
    raise EnvironmentError("ASSEMBLY_AI_AUTH missing in environment!")

headers = {"authorization": VOICE_API_AUTH}
CONNECTION_PARAMS = {
    "sample_rate": 16000,
    "format_turns": True
}
API_ENDPOINT_BASE_URL = "wss://streaming.assemblyai.com/v3/ws"
API_ENDPOINT = f"{API_ENDPOINT_BASE_URL}?{urlencode(CONNECTION_PARAMS)}"

FRAMES_PER_BUFFER = 800  # 50ms of audio
SAMPLE_RATE = CONNECTION_PARAMS["sample_rate"]
CHANNELS = 1
FORMAT = pyaudio.paInt16

# ----------------- STATE -----------------
audio = None
stream = None
ws_app = None
audio_thread = None
stop_event = threading.Event()

recorded_frames = []
recording_lock = threading.Lock()
all_transcripts = []   # 🟢 Store all text here

# ----------------- EVENT HANDLERS -----------------
def on_open(ws):
    """When WebSocket connects, start streaming audio in a thread."""
    print("WebSocket connected:", API_ENDPOINT)

    def stream_audio():
        while not stop_event.is_set():
            try:
                audio_data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                with recording_lock:
                    recorded_frames.append(audio_data)
                ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                print(f"Stream error: {e}")
                break
        print("Stopped streaming audio.")

    global audio_thread
    audio_thread = threading.Thread(target=stream_audio, daemon=True)
    audio_thread.start()


def on_message(ws, message):
    try:
        data = json.loads(message)
        msg_type = data.get("type")

        if msg_type == "Begin":
            print(f"Session started, id={data.get('id')}")

        elif msg_type == "Turn":
            transcript = data.get("transcript", "")
            if transcript:
                all_transcripts.append(transcript)   # 🟢 save transcript
                if data.get("turn_is_formatted", False):
                    print("\r" + " " * 80 + "\r", end="")
                    print(transcript)
                else:
                    print(f"\r{transcript}", end="")

        elif msg_type == "Termination":
            print("\nSession terminated.")
            save_text_file()

    except Exception as e:
        print("Message error:", e)


def on_error(ws, error):
    print("WebSocket error:", error)
    stop_event.set()


def on_close(ws, code, msg):
    print(f"WebSocket closed: {code}, {msg}")
    save_wav_file()
    save_text_file()
    cleanup()

# ----------------- HELPERS -----------------
def save_wav_file():
    if not recorded_frames:
        return

    filename = f"recorded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    try:
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            with recording_lock:
                wf.writeframes(b"".join(recorded_frames))
        print(f"Saved audio to {filename}")
    except Exception as e:
        print("WAV save error:", e)


def save_text_file():
    """Save collected transcript into a .txt file."""
    if not all_transcripts:
        return

    filename = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(all_transcripts))
        print(f"Saved transcript to {filename}")
    except Exception as e:
        print("Text save error:", e)

def cleanup():
    global audio, stream, audio_thread
    stop_event.set()
    if stream:
        if stream.is_active():
            stream.stop_stream()
        stream.close()
        stream = None
    if audio:
        audio.terminate()
        audio = None
    if audio_thread and audio_thread.is_alive():
        audio_thread.join(timeout=1.0)
    print("Resources cleaned up.")

# ----------------- MAIN -----------------
def start_streaming():
    """Start microphone streaming session with AssemblyAI."""
    global audio, stream, ws_app

    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
            channels=CHANNELS,
            format=FORMAT,
            rate=SAMPLE_RATE
        )
    except Exception as e:
        print("Microphone error:", e)
        audio.terminate()
        return

    ws_app = websocket.WebSocketApp(
        API_ENDPOINT,
        header=headers,
        on_open=on_open,         # 🟢 added on_open here
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws_thread = threading.Thread(target=ws_app.run_forever, daemon=True)
    ws_thread.start()

    try:
        while ws_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping stream...")
        stop_event.set()
        if ws_app and ws_app.sock and ws_app.sock.connected:
            try:
                ws_app.send(json.dumps({"type": "Terminate"}))
                time.sleep(1)
            except Exception as e:
                print("Terminate error:", e)
        ws_app.close()
        ws_thread.join(timeout=2.0)
        cleanup()

    return all_transcripts   # 🟢 Return transcript list

if __name__ == "__main__":
    transcripts = start_streaming()
    print("\nFinal transcript:")
    print(" ".join(transcripts))
