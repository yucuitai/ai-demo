"""
图片服务 - AI 图片生成 & 本地上传
"""
import os
import uuid
import time
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_images(keyword="blog", style="realistic", width=800, height=600, count=2):
    """生成模拟 AI 图片，支持多种风格和自定义描述"""
    import time as time_module
    timestamp = int(time_module.time())
    images = []

    style_colors = {
        "realistic":      ["2c3e50", "34495e", "7f8c8d", "4a5568"],
        "illustration":   ["e74c3c", "3498db", "f39c12", "2ecc71"],
        "minimal":        ["ecf0f1", "bdc3c7", "95a5a6", "dfe6e9"],
        "tech":           ["1a1a2e", "16213e", "0f3460", "0a1628"],
        "cyberpunk":      ["ff006e", "8338ec", "3a86ff", "ffbe0b"],
        "watercolor":     ["ffc8dd", "bde0fe", "a2d2ff", "cdb4db"],
        "anime":          ["ff70a6", "ff9770", "ffd670", "e9ff70"],
        "vintage":        ["d4a373", "faedcd", "ccd5ae", "e9edc9"],
        "neon":           ["ff006e", "8338ec", "00f5d4", "fee440"],
        "nature":         ["2d6a4f", "40916c", "52b788", "95d5b2"],
    }
    colors = style_colors.get(style, style_colors["realistic"])

    for i in range(count):
        seed = timestamp + i
        bg = colors[i % len(colors)]

        encoded_keyword = keyword.replace(" ", "-")[:20] if keyword else "blog"
        if not encoded_keyword.strip():
            encoded_keyword = "blog"

        img_id = f"img_{timestamp}_{i}"

        images.append({
            "id": img_id,
            "url": f"https://picsum.photos/seed/{seed}/{width}/{height}",
            "placeholder": f"https://via.placeholder.com/{width}x{height}/{bg}/ffffff?text={encoded_keyword[:8]}",
            "width": width,
            "height": height,
            "style": style,
            "keyword": keyword
        })

    return images


def save_uploaded_file(file_storage):
    """保存上传的文件并返回URL"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        file_storage.save(filepath)
    except Exception:
        return None

    return {
        "filename": filename,
        "originalName": file_storage.filename,
        "url": f"/api/uploads/{filename}",
        "size": os.path.getsize(filepath)
    }
