from pathlib import Path
from openai import OpenAI
import pygame
from dotenv import load_dotenv

from services.speech_to_text import start_streaming
from services.translate import generate_translations

load_dotenv()

def text_to_speech(text: str, output_file: str = "speech.mp3") -> str:
    """
    Convert text into speech using OpenAI TTS
    and save it to a file.
    """
    client = OpenAI()
    speech_file_path = Path(__file__).parent / output_file

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        instructions="""Read the text below in a cheerful and positive tone.
        Preserve the original language of the text.
        Deliver it smoothly, as if reading a natural essay or sentence, not word by word.
        """,
    ) as response:
        response.stream_to_file(speech_file_path)

    return str(speech_file_path)


def play_audio(file_path: str):
    """Play audio using pygame (works on Linux, Mac, Windows)."""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        print(f"✅ Played audio: {file_path}")
    except Exception as e:
        print("❌ Audio playback error:", e)


if __name__ == "__main__":
    # Example: Test TTS directly
    text = start_streaming()
    translation = generate_translations(text, "english", "french")
    audio_file = text_to_speech(translation)
    play_audio(audio_file)
