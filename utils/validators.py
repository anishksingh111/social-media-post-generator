from PIL import Image, UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

def validate_image(uploaded_file, max_mb: int):
    if uploaded_file is None:
        return True, ""
    if uploaded_file.size > max_mb * 1024 * 1024:
        return False, f"Image is too large. Maximum size is {max_mb} MB."
    try:
        image = Image.open(uploaded_file)
        image.verify()
        if image.format not in ALLOWED_FORMATS:
            return False, "Unsupported image format. Use JPG, PNG or WEBP."
        uploaded_file.seek(0)
        return True, ""
    except (UnidentifiedImageError, OSError):
        uploaded_file.seek(0)
        return False, "The uploaded file is not a valid image."
