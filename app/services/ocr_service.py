import pytesseract
from PIL import Image
import io
from pdf2image import convert_from_bytes
from app.config import OCR_LANG
from app.config import OCR_LANG_2

def extract_text(file_bytes: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        images = convert_from_bytes(file_bytes)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img, lang=OCR_LANG)
            text += pytesseract.image_to_string(img, lang=OCR_LANG_2)
        return text
    else:
        image = Image.open(io.BytesIO(file_bytes))
        text = ""
        text += pytesseract.image_to_string(image, lang=OCR_LANG)
        text += pytesseract.image_to_string(image, lang=OCR_LANG_2)
        return text
