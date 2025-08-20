import requests
import time
import os

BASE_URL = "https://api.assemblyai.com"
API_KEY = "251c609affe74af09cfb6c18ba0b2d99"

HEADERS = {
    "authorization": API_KEY
}


def upload_audio(file_path: str) -> str:
    """Uploads a local audio file to AssemblyAI and returns the file URL."""
    print("📤 Uploading audio file...")
    with open(file_path, "rb") as f:
        response = requests.post(f"{BASE_URL}/v2/upload", headers=HEADERS, data=f)

    response.raise_for_status()
    audio_url = response.json()["upload_url"]
    print(f"✅ File uploaded. URL: {audio_url}")
    return audio_url


def request_transcription(audio_url: str, model: str = "universal") -> str:
    """Sends transcription request and returns the transcript ID."""
    data = {"audio_url": audio_url, "speech_model": model}
    response = requests.post(f"{BASE_URL}/v2/transcript", json=data, headers=HEADERS)
    response.raise_for_status()
    transcript_id = response.json()["id"]
    print(f"📄 Transcription requested. ID: {transcript_id}")
    return transcript_id


def poll_transcription(transcript_id: str, interval: int = 3) -> str:
    """Polls AssemblyAI until transcription is completed, then returns the text."""
    polling_endpoint = f"{BASE_URL}/v2/transcript/{transcript_id}"
    print("⏳ Waiting for transcription...")

    while True:
        transcription_result = requests.get(polling_endpoint, headers=HEADERS).json()
        status = transcription_result.get("status")

        if status == "completed":
            transcript_text = transcription_result["text"]
            print("✅ Transcript completed!\n")
            return transcript_text

        elif status == "error":
            raise RuntimeError(f"❌ Transcription failed: {transcription_result['error']}")

        else:
            time.sleep(interval)


def transcribe_local_file(file_path: str) -> str:
    """Convenience function: Upload -> Request -> Poll -> Return transcript text"""
    audio_url = upload_audio(file_path)
    transcript_id = request_transcription(audio_url)
    transcript_text = poll_transcription(transcript_id)
    return transcript_text


if __name__ == "__main__":
    AUDIO_DIR = "temporary_audio"
    AUDIO_FILENAME = "output.wav"
    file_path = os.path.join(AUDIO_DIR, AUDIO_FILENAME)

    transcript = transcribe_local_file(file_path)
    print("Transcript Text:", transcript)
