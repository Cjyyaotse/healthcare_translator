from pathlib import Path
from openai import OpenAI
import pygame
from dotenv import load_dotenv
import io

from services.translate import generate_translations

load_dotenv()


def text_to_speech(text: str):
    """
    Convert text into speech using OpenAI TTS
    and return raw audio bytes (no file saved).
    """
    client = OpenAI()

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        instructions="""Read the text below in a cheerful and positive tone.
        Preserve the original language of the text.
        Deliver it smoothly, as if reading a natural essay or sentence, not word by word.
        """,
    ) as response:
        audio_bytes = response.read()  # Get raw audio bytes
        return audio_bytes


def play_audio_bytes(audio_bytes: bytes):
    """
    Play audio from raw bytes in memory using pygame.
    """
    try:
        pygame.mixer.init()
        audio_buffer = io.BytesIO(audio_bytes)
        pygame.mixer.music.load(audio_buffer, "mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        print("✅ Played audio from memory")
    except Exception as e:
        print("❌ Audio playback error:", e)


if __name__ == "__main__":
    # Example: Translate and play without saving
    text = start_streaming()
    translation = generate_translations(text, "english", "french")
    audio_bytes = text_to_speech(translation)
    play_audio_bytes(audio_bytes)
