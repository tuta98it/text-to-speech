from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gtts import gTTS
from langdetect import detect
import uuid, re, os

app = FastAPI()

# Serve folder /audio như static files
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

SUPPORTED_LANGS = [
    'af','ar','bn','bs','ca','cs','cy','da','de','el','en','eo','es','et','fi',
    'fr','gu','hi','hr','hu','id','is','it','ja','jw','km','kn','ko','la','lv',
    'mk','ml','mr','my','ne','nl','no','pl','pt','ro','ru','si','sk','sq','sr',
    'su','sv','sw','ta','te','th','tl','tr','uk','ur','vi','zh-CN','zh-TW'
]

class TTSRequest(BaseModel):
    text: str
    lang: str | None = None

@app.post("/tts")
async def text_to_speech(req: TTSRequest, request: Request):
    text = req.text

    # Auto detect
    if req.lang:
        lang = req.lang
    else:
        try:
            lang = detect(text)
            if lang == "no":
                if re.fullmatch(r"[A-Za-z0-9 ,.!?']+", text):
                    lang = "en"
        except:
            return {"error": "Không thể nhận diện ngôn ngữ."}

    if lang not in SUPPORTED_LANGS:
        lang = "en"

    # Tạo file mp3
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join("audio", filename)

    tts = gTTS(text=text, lang=lang)
    tts.save(filepath)

    # Lấy URL base (http://localhost:8000)
    base_url = str(request.base_url).rstrip("/")

    # Trả FULL URL
    return {
        "detected_language": lang,
        "audio_url": f"{base_url}/audio/{filename}"
    }
