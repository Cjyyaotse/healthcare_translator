import pyaudio
import wave
import threading

def record_audio():
    """Continuously record audio until user presses ENTER"""

    import os
    output_filename="output.wav"
    directory="temporary_audio"

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Recording parameters
    FORMAT = pyaudio.paInt16   # 16-bit resolution
    CHANNELS = 1               # mono
    RATE = 44100               # 44.1kHz sampling rate
    CHUNK = 1024               # frames per buffer

    # Globals for control
    recording = True
    frames = []

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("🎙️ Recording... Press ENTER to stop.")

    # Background thread to capture audio
    def _record():
        while recording_flag[0]:
            data = stream.read(CHUNK)
            frames.append(data)

    # Use a list as a mutable flag
    recording_flag = [True]
    recording_thread = threading.Thread(target=_record)
    recording_thread.start()

    # Wait for user input
    input()
    recording_flag[0] = False
    recording_thread.join()

    # Stop and close stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save audio
    output_path = os.path.join(directory, output_filename)
    wf = wave.open(output_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"✅ Recording stopped. Saved to {output_path}")
    return output_path
