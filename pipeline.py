import os

from services.speech_to_text import transcribe_local_file
from services.translate import generate_translations
from services.text_to_speech import text_to_speech, play_audio_bytes
from services.record_audio import record_audio


def main():
    source_lang = input("Enter the preferred input language: ")
    target_lang = input("Enter the preferred target language: ")

    # 1. Record audio
    audio_path = record_audio()

    # 2. Speech to text
    # AUDIO_DIR = "temporary_audio"
    transcript = transcribe_local_file(audio_path)
    # 2. Translate transcript (example: native language → English)
    translation = generate_translations(transcript, source_lang, target_lang)
    print("Translation:", translation)

    # 3. Convert translation to speech
    audio_file = text_to_speech(translation)

    # 4. Play the generated audio
    play_audio_bytes(audio_file)


if __name__ == "__main__":
    main()
