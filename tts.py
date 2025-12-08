from gtts import gTTS
from langdetect import detect
import uuid

# Danh sách ngôn ngữ gTTS hỗ trợ
SUPPORTED_LANGS = [
    'af','ar','bn','bs','ca','cs','cy','da','de','el','en','eo','es','et','fi',
    'fr','gu','hi','hr','hu','id','is','it','ja','jw','km','kn','ko','la','lv',
    'mk','ml','mr','my','ne','nl','no','pl','pt','ro','ru','si','sk','sq','sr',
    'su','sv','sw','ta','te','th','tl','tr','uk','ur','vi','zh-CN','zh-TW'
]

# ====== NHẬP TEXT ======
text = input("Nhập đoạn text cần đọc thành tiếng: ")

# ====== AUTO DETECT LANGUAGE ======
try:
    lang = detect(text)
    if lang == "no":
        if re.fullmatch(r"[A-Za-z0-9 ,.!?']+", text):
            lang = "en"
    print(f"Ngôn ngữ phát hiện: {lang}")
except:
    print("Không thể nhận diện ngôn ngữ.")
    exit()

# ====== CHECK NGÔN NGỮ HỖ TRỢ ======
if lang not in SUPPORTED_LANGS:
    print(f"⚠ gTTS không hỗ trợ ngôn ngữ '{lang}'. Tự chuyển sang tiếng Anh (en).")
    lang = "en"

# ====== TẠO AUDIO từ thư viện gTTS ======
filename = f"{uuid.uuid4()}.mp3"
tts = gTTS(text=text, lang=lang)
tts.save(filename)

print(f"Đã tạo file âm thanh: {filename}")
print("Mở file .mp3 để nghe.")
