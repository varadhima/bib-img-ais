FROM python:3.11

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-ara \
        libtesseract-dev \
        poppler-utils \
        gcc \
        build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Create working directory
WORKDIR /app

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/


RUN tesseract --list-langs

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
