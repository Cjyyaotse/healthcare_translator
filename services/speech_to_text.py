import io
import threading
import sounddevice as sd
import numpy as np
import wavio
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
client = OpenAI()

# Globals
recording_flag = [False]
frames = []
stream = None
recording_thread = None

CHANNELS = 1
RATE = 44100
OUTPUT_DIR = "recordings"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def start_recording():
    global recording_flag, frames, stream
    frames = []
    recording_flag[0] = True

    def callback(indata, frames_count, time, status):
        if recording_flag[0]:
            frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=RATE,
        channels=CHANNELS,
        dtype='int16',
        callback=callback
    )
    stream.start()
    print("🎙️ Recording started...")


def stop_recording():
    global recording_flag, frames, stream
    if not recording_flag[0]:
        return ""

    print("🛑 Stopping recording...")
    recording_flag[0] = False
    stream.stop()
    stream.close()

    # Combine all frames
    audio_data = np.concatenate(frames, axis=0)

    # Save audio to disk
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.wav")
    wavio.write(filename, audio_data, RATE, sampwidth=2)
    print(f"💾 Audio saved to {filename}")

    # In-memory WAV buffer for OpenAI
    wav_buffer = io.BytesIO()
    wavio.write(wav_buffer, audio_data, RATE, sampwidth=2)
    wav_buffer.seek(0)
    wav_buffer.name = "speech.wav"

    print("⏳ Transcribing...")
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=wav_buffer,
        #language="en"
    )

    print("✅ Transcript:", transcript.text)
    return transcript.text
