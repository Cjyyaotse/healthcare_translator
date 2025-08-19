from services.speech_to_text import start_streaming
from services.translate import generate_translations
from services.text_to_speech import text_to_speech, play_audio


def main():
    source_lang = input("Enter the preferred input language: ")
    target_lang = input("Enter the preferred target language: ")

    # 1. Capture spoken input
    transcript = start_streaming()
    print("Transcript:", transcript)

    # 2. Translate transcript (example: native language → English)
    translation = generate_translations(transcript, source_lang, target_lang)
    print("Translation:", translation)

    # 3. Convert translation to speech
    audio_file = text_to_speech(translation)

    # 4. Play the generated audio
    play_audio(audio_file)


if __name__ == "__main__":
    main()
