from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_service import extract_text

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ["image/png", "image/jpeg", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    contents = await file.read()
    try:
        text = extract_text(contents, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    return {"filename": file.filename, "extracted_text": text}
