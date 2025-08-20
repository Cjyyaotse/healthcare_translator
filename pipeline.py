from services.speech_to_text import stream_audio_transcription_text
from services.translate import generate_translations
from services.text_to_speech import text_to_speech  # your TTS function
from pathlib import Path

def speech_translate_speech_pipeline(
    input_audio_path: str,
    output_audio_path: str,
    input_language: str = "english",
    output_language: str = "french",
    tts_voice: str = "coral",
    tts_model: str = "gpt-4o-mini-tts"
):
    """
    Complete speech-to-speech pipeline:
      1) Stream transcription from audio file,
      2) Accumulate full transcription text,
      3) Stream translation,
      4) Accumulate full translated text,
      5) Convert translated text to speech and save to file.

    Args:
        input_audio_path (str): Path to input audio file.
        output_audio_path (str): Path to save synthesized speech file.
        input_language (str): Language to assume for input (default "english").
        output_language (str): Language to translate to (default "french").
        tts_voice (str): Voice for TTS (default "coral").
        tts_model (str): TTS model to use (default "gpt-4o-mini-tts").
        tts_instructions (str): Instructions for speaking style.
    """

    print("Starting transcription...")
    transcription_chunks = []
    # Stream and print transcription chunks
    for chunk in stream_audio_transcription_text(input_audio_path):
        print(chunk, end="", flush=True)
        transcription_chunks.append(chunk)

    full_transcription = "".join(transcription_chunks)
    print("\n--- Transcription complete ---\n")

    print("Starting translation...")
    translation_chunks = []
    for chunk in generate_translations(full_transcription, input_language, output_language):
        print(chunk, end="", flush=True)
        translation_chunks.append(chunk)

    full_translation = "".join(translation_chunks)
    print("\n--- Translation complete ---\n")

    print("Starting text-to-speech synthesis...")
    text_to_speech(
        text=full_translation,
        output_file=output_audio_path,
        voice=tts_voice,
        model=tts_model
    )
    print(f"Speech synthesis complete. Output saved to {output_audio_path}")


# Example usage
if __name__ == "__main__":
    input_audio = "recordings/output.wav"
    output_audio = "recordings/translated_speech.mp3"
    speech_translate_speech_pipeline(input_audio, output_audio)
