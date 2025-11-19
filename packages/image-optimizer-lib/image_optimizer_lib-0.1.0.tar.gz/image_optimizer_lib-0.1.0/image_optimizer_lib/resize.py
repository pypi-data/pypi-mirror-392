from io import BytesIO
from PIL import Image

def optimize_image(input_image, max_width=800, quality=75, output_format=None):
    """
    Optimize and resize an image.
    
    :param input_image: str (filepath), bytes, or Django UploadedFile
    :param max_width: Maximum width for resize
    :param quality: Compression quality (1-100)
    :param output_format: "JPEG" or "PNG" or "WEBP"
    :return: optimized image bytes
    """

    # Load image
    if isinstance(input_image, str):
        img = Image.open(input_image)
    elif hasattr(input_image, 'read'):
        img = Image.open(input_image)
    else:
        img = Image.open(BytesIO(input_image))

    img = img.convert("RGB")

    # Resize if needed
    width, height = img.size
    if width > max_width:
        new_height = int((max_width / width) * height)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Prepare output buffer
    buffer = BytesIO()

    if not output_format:
        output_format = img.format or "JPEG"

    img.save(buffer, format=output_format, quality=quality, optimize=True)
    buffer.seek(0)

    return buffer.getvalue()

# result = optimize_image("C:/Users/admin/Pictures/127.jpg")

# # Save optimized image to a new file
# with open("C:/Users/admin/Pictures/127_optimized.jpg", "wb") as f:
#     f.write(result)

# print("Optimized image saved successfully!")
