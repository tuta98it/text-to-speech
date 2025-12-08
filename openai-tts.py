from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os, uuid

# Load biến môi trường từ .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Tạo thư mục audio nếu chưa có
if not os.path.exists("audio"):
    os.makedirs("audio")

# Serve static files
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# Các giọng đọc có sẵn của OpenAI
VOICES = ["alloy", "verse", "flux", "coral", "pebble", "oak", "rose", "ash"]

class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"

@app.post("/tts")
async def text_to_speech(req: TTSRequest, request: Request):
    text = req.text
    voice = req.voice

    if voice not in VOICES:
        return {"error": f"Voice '{voice}' không hợp lệ. Các voice hợp lệ: {VOICES}"}

    # Tạo tên file
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join("audio", filename)

    # Gọi OpenAI API TTS
    with open(filepath, "wb") as f:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text
        )
        f.write(response.read())

    # URL base (local)
    base_url = str(request.base_url).rstrip("/")

    return {
        "voice_used": voice,
        "audio_url": f"{base_url}/audio/{filename}"
    }
