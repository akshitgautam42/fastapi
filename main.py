import os
import soundfile as sf
import numpy as np
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from cartesia.tts import CartesiaTTS
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# API key for Cartesia TTS
api_key = os.getenv("TTS_API_KEY")#['TTS_API_KEY']
assert api_key is not None

# Create TTS client
client = CartesiaTTS(api_key=api_key)
voices = client.get_voices()
logger.info("Initialized TTS client and retrieved voices")

# Configuration
gen_cfg = dict(model_id="upbeat-moon", data_rtype="array", output_format="fp32")


class TTSRequest(BaseModel):
    voice: str
    transcript: str


@app.post("/tts/")
async def tts_endpoint(request: TTSRequest):
    voice_name = request.voice
    transcript = request.transcript
    logger.info(
        f"Received TTS request for voice: {voice_name}, transcript: {transcript}"
    )

    if voice_name not in voices:
        logger.error(f"Voice {voice_name} not found")
        raise HTTPException(status_code=400, detail="Voice not found")

    try:
        voice_id = voices[voice_name]["id"]
        voice = client.get_voice_embedding(voice_id=voice_id)
        output = client.generate(
            transcript=transcript, voice=voice, stream=False, **gen_cfg
        )

        buffer = output["audio"]
        rate = output["sampling_rate"]

        # Write audio to BytesIO using soundfile
        audio_stream = BytesIO()
        sf.write(audio_stream, buffer, rate, format="wav")
        audio_stream.seek(0)

        return StreamingResponse(audio_stream, media_type="audio/wav")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Run the application with: uvicorn main:app --reload
