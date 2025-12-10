from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gtts import gTTS
from langdetect import detect
import uuid, re, os
from langdetect import detect
import subprocess
from datetime import datetime
import os

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
    speed: float | None = 1.0 # tốc độ phát âm (0.5 - 2.0)


class TTSRequest(BaseModel):
    texts: list[TextItem]

# -------- FUNCTION GENERATE AUDIO PATH --------
def generate_audio_path():
    now = datetime.now()

    # folder structure: audio/YYYY/MM/DD/
    folder = os.path.join(
        "audio",
        now.strftime("%Y"),
        now.strftime("%m"),
        now.strftime("%d")
    )

    # create folders if not exist
    os.makedirs(folder, exist_ok=True)

    filename = now.strftime("%Y%m%d_%H%M%S_%f") + ".mp3"
    full_path = os.path.join(folder, filename)

    return full_path
# -------- FUNCTION TTS --------
def convert_text_to_speech(text: str, lang: str | None, speed: float | None, base_url: str):
    # Auto-detect language nếu lang = None hoặc chuỗi rỗng
    if not lang:
        try:
            lang = detect(text)
            if lang == "no" and re.fullmatch(r"[A-Za-z0-9 ,.!?']+", text):
                lang = "en"
        except:
            return {"error": "Không thể nhận diện ngôn ngữ."}

    if lang not in SUPPORTED_LANGS:
        lang = "en"

    # Validate speed
    if speed is None:
        speed = 1.0
    if speed <= 0:
        speed = 1.0

    filepath = generate_audio_path(filename)

    # Tạo audio bằng gTTS (không có tham số speed)
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(filepath)

    # Nếu speed != 1 thì chỉnh tốc độ
    if speed != 1.0:
        temp_output = filepath.replace(".mp3", "_tmp.mp3")

        # Chạy ffmpeg filter: atempo = tốc độ
        subprocess.run([
            "ffmpeg", "-i", filepath,
            "-filter:a", f"atempo={speed}",
            "-vn",
            temp_output,
            "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Ghi đè file cũ bằng file đã chỉnh tốc độ
        os.replace(temp_output, filepath)

    return {
        "detected_language": lang,
        "audio_url": f"/audio/{filename}"
    }


# -------- ROUTE API --------
@app.post("/tts")
async def text_to_speech(req: TTSRequest, request: Request):

    if not os.path.exists("audio"):
        os.makedirs("audio")

    base_url = str(request.base_url).rstrip("/")

    results = []

    for item in req.texts:
        result = convert_text_to_speech(item.text, item.lang, item.speed, base_url)
        results.append(result)

    return {"results": results}
