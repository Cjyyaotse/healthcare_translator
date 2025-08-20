import pyaudio
import io
import threading
import wave
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Globals to manage recording
p = None
stream = None
frames = []
recording_flag = [False]
recording_thread = None

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024


def start_recording():
    global p, stream, frames, recording_flag, recording_thread
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    frames = []
    recording_flag[0] = True

    def _record():
        while recording_flag[0]:
            data = stream.read(CHUNK)
            frames.append(data)

    recording_thread = threading.Thread(target=_record)
    recording_thread.start()
    print("🎙️ Recording started...")


def stop_recording():
    global p, stream, frames, recording_flag, recording_thread
    if not recording_flag[0]:
        return ""

    print("🛑 Stopping recording...")
    recording_flag[0] = False
    recording_thread.join()

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("⏳ Transcribing...")

    # Wrap audio into WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    wav_buffer.seek(0)
    wav_buffer.name = "speech.wav"

    transcript = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=wav_buffer
    )

    print("✅ Transcript:", transcript.text)
    return transcript.text
