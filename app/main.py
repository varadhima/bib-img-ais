"""
from fastapi import FastAPI
from app.routes.upload import router as upload_router

app = FastAPI(title="OCR Service API")

app.include_router(upload_router)

@app.get("/")
def root():
    return {"message": "OCR Service is running"}
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.services.ocr_service import extract_text
from app.services.compare import compare_data
from app.services.utils import allowed_file
import json
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/validate-document")
async def validate_document(
    file: UploadFile = File(...),
    actual_data: str = Form(...)
):
    if not allowed_file(file.content_type):
        return JSONResponse(status_code=400, content={"error": "Unsupported file type."})

    try:
        file_bytes = await file.read()
        extracted_text = extract_text(file_bytes, file.content_type)
        if not actual_data:
            return JSONResponse(status_code=400, content={"error": "actual_data form field is empty."})
        try:
            actual_data_dict = json.loads(actual_data)
        except json.JSONDecodeError as jde:
            logger.error(f"JSON decode error: {jde}")
            return JSONResponse(status_code=400, content={"error": "actual_data is not valid JSON."})

        result = compare_data(extracted_text, actual_data_dict)

        return {
            "filename": file.filename,
            "extracted_text": extracted_text,
            "comparison_result": result
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
