FastAPI Speech and Translation API
This is a FastAPI-based API providing endpoints for Speech-to-Text (STT), Text Translation, and Text-to-Speech (TTS) functionalities. The API accepts audio or text inputs and returns streamed responses for transcriptions, translations, or generated speech audio.
Table of Contents

Features
Prerequisites
Installation
API Endpoints
Speech-to-Text Endpoint
Translation Endpoint
Text-to-Speech Endpoint


Usage Examples
Deployment Notes
Contributing
License

Features

Speech-to-Text (STT): Upload audio files to receive streamed transcription text chunks.
Translation: Translate text from an input language to an output language with streamed text chunks.
Text-to-Speech (TTS): Convert text to speech audio (MP3 stream) with customizable voice options.
Supports multipart form data for audio uploads and URL-encoded form data for text inputs.
Streamed responses for efficient handling of large or real-time data.

Prerequisites

Python 3.9+
FastAPI and Uvicorn (pip install fastapi uvicorn)
Additional dependencies (e.g., for audio processing or translation, specify in requirements.txt)
A deployed instance (e.g., on Render) or local server for testing
Tools for testing: curl, Postman, or a custom client

Installation

Clone the repository:git clone https://github.com/your-username/your-repo.git
cd your-repo


Install dependencies:pip install -r requirements.txt


Run the FastAPI server locally:uvicorn main:app --host 0.0.0.0 --port 8000 --reload


Access the API at http://localhost:8000 or your deployed URL (e.g., https://your-app.onrender.com).

API Endpoints
Speech-to-Text Endpoint

POST /stt/speech-to-text
Description: Accepts an audio file upload and returns streamed transcription text chunks.
Request Body (multipart/form-data):
audio (required, binary): Audio file to transcribe.


Responses:
200: Successful response with streamed text chunks.
422: Validation error (e.g., missing or invalid audio file).


Example Response (application/json):null



Translation Endpoint

POST /translate/translate
Description: Accepts text with input and output language codes, returns streamed translated text chunks.
Request Body (application/x-www-form-urlencoded):
text (required, string): Text to translate.
input_language (required, string): Source language code (e.g., "en" for English).
output_language (required, string): Target language code (e.g., "es" for Spanish).


Responses:
200: Successful response with streamed translated text chunks.
422: Validation error (e.g., missing fields or unsupported languages).


Example Response (application/json):null



Text-to-Speech Endpoint

POST /tts/text-to-speech
Description: Converts input text to speech, returning an MP3 audio stream. Supports optional voice customization.
Request Body (application/x-www-form-urlencoded):
text (required, string): Text to convert to speech.
voice (optional, string): Voice model to use (default: "coral").


Responses:
200: Successful response with MP3 audio stream.
422: Validation error (e.g., missing text or invalid voice).


Example Response (application/json):null



Usage Examples
Speech-to-Text
Upload an audio file using curl:
curl -X POST "https://your-app.onrender.com/stt/speech-to-text" \
  -F "audio=@/path/to/audio.wav"

Expected: Streamed text chunks of the transcription.
Translation
Translate text from English to Spanish:
curl -X POST "https://your-app.onrender.com/translate/translate" \
  -d "text=Hello, world!&input_language=en&output_language=es"

Expected: Streamed translated text chunks (e.g., "¡Hola, mundo!").
Text-to-Speech
Generate speech audio from text:
curl -X POST "https://your-app.onrender.com/tts/text-to-speech" \
  -d "text=Welcome to my app&voice=coral" \
  --output output.mp3

Expected: MP3 audio file stream saved as output.mp3.
Deployment Notes

Render Free Tier: Deployed on Render’s free tier, which may experience cold starts after ~15 minutes of inactivity. To mitigate, set up a health check endpoint (e.g., /health) and use UptimeRobot to ping it every 5 minutes:@app.get("/health")
async def health_check():
    return {"status": "ok"}

Configure UptimeRobot at https://uptimerobot.com with your /health URL (e.g., https://your-app.onrender.com/health).
**Vercel Frontend
