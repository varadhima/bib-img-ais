def allowed_file(content_type: str) -> bool:
    return content_type.startswith("image/") or content_type == "application/pdf"
