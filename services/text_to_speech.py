from pathlib import Path
from openai import OpenAI
from services.speech_to_text import stream_audio_transcription_text
from services.translate import generate_translations
from dotenv import load_dotenv

load_dotenv()

def text_to_speech(text: str, output_file: str, voice: str = "coral", model: str = "gpt-4o-mini-tts"):
    instructions = "Speak in a cheerful and positive tone."
    """
    Convert text to spoken audio and save as an MP3 file.

    Args:
        text (str): Text input to convert to speech.
        output_file (str): Path to save the generated audio file.
        voice (str): Voice name to use for TTS (default "coral").
        model (str): TTS model name (default "gpt-4o-mini-tts").
        instructions (str): Optional instructions to control speech style/tone.
    """
    client = OpenAI()
    output_path = Path(output_file)

    with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        input=text,
        instructions=instructions,
    ) as response:
        response.stream_to_file(output_path)
    print(f"Audio saved to {output_path}")

# Example usage
if __name__ == "__main__":
    text = "Today is a wonderful day to build something people love!"
    output_path = "recordings/output_speech.mp3"

    text_to_speech(text, output_path)
