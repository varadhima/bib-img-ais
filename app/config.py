import os

DATABASE_URL = os.getenv("DATABASE_URL")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
OCR_LANG = "eng"
OCR_LANG_2 = "ara"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

