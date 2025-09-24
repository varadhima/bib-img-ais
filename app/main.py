from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import torch
import clip
from PIL import Image
import io
import json
import logging
import numpy as np
import cv2
import base64
from deepface import DeepFace
from app.services.ocr_service import extract_text
from app.services.compare import compare_data
from app.services.utils import allowed_file

app = FastAPI(title="OCR & Image/Video Verification Service API")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up device for CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)

# Helper Functions
def get_clip_embedding(img: Image.Image) -> torch.Tensor:
    img_tensor = clip_preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = clip_model.encode_image(img_tensor)
        emb /= emb.norm(dim=-1, keepdim=True)
    return emb

def get_face_embedding(img: Image.Image) -> np.ndarray:
    img_array = np.array(img)
    emb = DeepFace.represent(img_array, model_name="Facenet")[0]["embedding"]
    return emb / np.linalg.norm(emb)

def cosine_similarity(emb1, emb2):
    if isinstance(emb1, torch.Tensor):
        return float((emb1 @ emb2.T).item())
    else:
        return float(np.dot(emb1, emb2))

def encode_frame_base64(frame: np.ndarray) -> str:
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

# Routes

@app.get("/")
def root():
    return {"message": "OCR & Image/Video Verification Service is running"}

@app.post("/validate-document")
async def validate_document(file: UploadFile = File(...), actual_data: str = Form(...)):
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


@app.post("/verify")
async def verify(
    source_file: UploadFile = File(...),
    reference_file: UploadFile = File(...),
    mode: str = Form("general")
):
    try:
        # Process the reference image or video
        ref_img = Image.open(io.BytesIO(await reference_file.read())).convert("RGB")
        ref_emb = get_clip_embedding(ref_img) if mode == "general" else get_face_embedding(ref_img)

        # Check if source file is image or video
        if source_file.content_type.startswith("image/"):
            src_img = Image.open(io.BytesIO(await source_file.read())).convert("RGB")
            src_emb = get_clip_embedding(src_img) if mode == "general" else get_face_embedding(src_img)
            score = cosine_similarity(src_emb, ref_emb)
            return {
                "type": "image",
                "mode": mode,
                "similarity_score": score,
                "match": score > 0.8
            }

        elif source_file.content_type.startswith("video/"):
            tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            with open(tmp_path, "wb") as f:
                f.write(await source_file.read())
            cap = cv2.VideoCapture(tmp_path)
            best_score, frame_count, best_frame = 0, 0, None

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                if frame_count % 10 == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_emb = get_clip_embedding(frame_pil) if mode == "general" else get_face_embedding(frame_pil)
                    score = cosine_similarity(frame_emb, ref_emb)
                    if score > best_score:
                        best_score = score
                        best_frame = frame.copy()

            cap.release()

            return {
                "type": "video",
                "mode": mode,
                "frames_checked": frame_count,
                "best_similarity_score": best_score,
                "match": best_score > 0.8,
                "best_frame_base64": encode_frame_base64(best_frame) if best_frame is not None else None
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

