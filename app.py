from fastapi import FastAPI, UploadFile, File, Form, Response, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.routing import APIRouter
from typing import AsyncGenerator

from services.speech_to_text import stream_audio_transcription_text
from services.translate import generate_translations
from services.text_to_speech import text_to_speech

import tempfile
from pathlib import Path
import os

app = FastAPI()

# ------------- Router for Speech-to-Text -------------
stt_router = APIRouter()

@stt_router.post("/speech-to-text")
async def speech_to_text_endpoint(audio: UploadFile = File(...)) -> StreamingResponse:
    """
    Accept audio upload and stream transcription text chunks.
    """

    # Save uploaded file to a named temporary file that remains during function
    try:
        suffix = Path(audio.filename).suffix or ".wav"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file_path = temp_file.name

        # Save content asynchronously
        content = await audio.read()
        temp_file.write(content)
        temp_file.flush()
        temp_file.close()

        async def transcript_generator() -> AsyncGenerator[bytes, None]:
            for chunk in stream_audio_transcription_text(temp_file_path):
                yield chunk.encode("utf-8")

        response = StreamingResponse(transcript_generator(), media_type="text/plain")

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed processing audio: {exc}")

    finally:
        # Clean up the temp file after response is done sending
        def cleanup_tempfile():
            try:
                if Path(temp_file_path).exists():
                    os.remove(temp_file_path)
            except Exception:
                pass
            
        #response.call_on_close(cleanup_tempfile)

    return response

# ------------ Router for Translation ------------------
translate_router = APIRouter()

@translate_router.post("/translate")
async def translate_endpoint(
    text: str = Form(...),
    input_language: str = Form(...),
    output_language: str = Form(...)
) -> StreamingResponse:
    """
    Accepts form data with text, input_language, output_language,
    returns streamed translated text chunks.
    """
    async def translation_generator() -> AsyncGenerator[bytes, None]:
        for chunk in generate_translations(text, input_language, output_language):
            yield chunk.encode("utf-8")

    return StreamingResponse(translation_generator(), media_type="text/plain")


# ------------ Router for Text-to-Speech ----------------
tts_router = APIRouter()

@tts_router.post("/text-to-speech")
async def text_to_speech_endpoint(
    text: str = Form(...),
    voice: str = Form("coral")
):
    """
    Accepts translated text and optional voice/model/instructions,
    returns generated speech audio (mp3 file stream).
    """
    # Use a temporary file to save generated audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        text_to_speech(text, temp_audio_file.name, voice=voice)
        temp_audio_file_path = temp_audio_file.name

    # Return the mp3 file as streaming response
    return FileResponse(temp_audio_file_path, media_type="audio/mpeg", filename="output_speech.mp3")


# Include routers in main app
app.include_router(stt_router, prefix="/stt", tags=["Speech-to-Text"])
app.include_router(translate_router, prefix="/translate", tags=["Translation"])
app.include_router(tts_router, prefix="/tts", tags=["Text-to-Speech"])
