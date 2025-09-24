# OCR Service API

A FastAPI-based OCR service using Tesseract OCR for extracting text from images and PDFs. Deployed with Docker and Azure.

# Image/Video Verification API
FastAPI service for verifying images or video frames against a reference image.

## Features
- Upload images and PDFs for text extraction
- FastAPI endpoints with Swagger UI
- Tesseract OCR integration
- Docker containerized for easy deployment
- Azure App Service and PostgreSQL support

## Setup Instructions

### Clone the repository
```bash
git clone https://github.com/<your-username>/ocr-service.git
cd ocr-service
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configure environment variables
```bash
cp .env.example .env
```

Fill in the correct values.

### Run the application
```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to test.

### Docker Setup
```bash
docker build -t ocr-service .
docker run -d -p 8000:8000 --env-file .env ocr-service
```

## Deployment

- Setup Azure App Service and PostgreSQL
- Add secrets to GitHub for CI/CD
- Push changes to `main` branch to trigger deployment
