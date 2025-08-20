from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from typing import Text
from services.speech_to_text import stream_audio_transcription_text

load_dotenv()

def generate_translations(text, input_language, output_language):
    gpt_4o = init_chat_model("gpt-4o", model_provider="openai", temperature=0.3)
    prompt = f"""
    Translate the following text in {input_language} language into {output_language} language:
    text: {text}
    - Provide a natural, fluent sentence in {output_language}.
    - Do not translate word-for-word; combine single words into proper sentences.
    """


    response = gpt_4o.invoke(prompt).content +"\n"
    return response

# Example usage:
if __name__ == "__main__":
    full_transcription = []
    for chunk in stream_audio_transcription_text("recordings/output.wav"):
        #print(chunk, end="", flush=True)
        full_transcription.append(chunk)

    text= "".join(full_transcription)

    translation = generate_translations(text, "english", "fr")
    print("Transcript:", translation)
