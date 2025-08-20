from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def stream_audio_transcription_text(audio_file_path, model="gpt-4o-mini-transcribe"):
    """
    Stream transcription text content from an audio file using OpenAI API,
    yield chunks of transcription text, and finally return full text.

    Args:
        audio_file_path (str): Local path to audio file.
        model (str): Model name to use for transcription (default: gpt-4o-mini-transcribe).

    Yields:
        str: Streamed chunks of transcription text content only.

    Returns:
        str: Full concatenated transcription text after streaming completes.
    """
    client = OpenAI()

    full_text = ""
    with open(audio_file_path, "rb") as audio_file:
        stream = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="text",
            stream=True,
        )
        for event in stream:
            if hasattr(event, "type") and event.type == "transcript.text.delta":
                text_chunk = event.delta
                full_text += text_chunk
                yield text_chunk

    return full_text

# Example usage
if __name__ == "__main__":
    audio_path = "recordings/output.wav"
    
    # To both stream and get full text at the end:
    streamer = stream_audio_transcription_text(audio_path)
    
    full_transcription = []
    for chunk in stream_audio_transcription_text(audio_path):
        print(chunk, end="", flush=True)
        full_transcription.append(chunk)

    full_text = "".join(full_transcription)
    print(full_text)
