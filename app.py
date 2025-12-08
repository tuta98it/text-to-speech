from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gtts import gTTS
from langdetect import detect
import uuid, re, os

app = FastAPI()

# Serve static files
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

SUPPORTED_LANGS = [
    'af','ar','bn','bs','ca','cs','cy','da','de','el','en','eo','es','et','fi',
    'fr','gu','hi','hr','hu','id','is','it','ja','jw','km','kn','ko','la','lv',
    'mk','ml','mr','my','ne','nl','no','pl','pt','ro','ru','si','sk','sq','sr',
    'su','sv','sw','ta','te','th','tl','tr','uk','ur','vi','zh-CN','zh-TW'
]


# -------- FIX REQUEST MODEL --------
class TextItem(BaseModel):
    text: str
    lang: str | None = None  # có thể null → auto detect


class TTSRequest(BaseModel):
    texts: list[TextItem]


# -------- FUNCTION TTS --------
def convert_text_to_speech(text: str, lang: str | None, base_url: str):
    
    # Auto detect language nếu lang = None hoặc chuỗi rỗng
    if not lang:
        try:
            lang = detect(text)
            if lang == "no" and re.fullmatch(r"[A-Za-z0-9 ,.!?']+", text):
                lang = "en"
        except:
            return {"error": "Không thể nhận diện ngôn ngữ."}

    if lang not in SUPPORTED_LANGS:
        lang = "en"

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join("audio", filename)

    tts = gTTS(text=text, lang=lang)
    tts.save(filepath)

    return {
        "detected_language": lang,
        "audio_url": f"{base_url}/audio/{filename}"
    }


# -------- ROUTE API --------
@app.post("/tts")
async def text_to_speech(req: TTSRequest, request: Request):

    if not os.path.exists("audio"):
        os.makedirs("audio")

    base_url = str(request.base_url).rstrip("/")

    results = []

    for item in req.texts:
        result = convert_text_to_speech(item.text, item.lang, base_url)
        results.append(result)

    return {"results": results}
