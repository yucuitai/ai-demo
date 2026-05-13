"""
图片服务 - AI 图片生成（支持 DALL-E/OpenAI 兼容） & 本地上传
"""
import json
import os
import uuid
import time
import logging
from urllib import request, error

from services.config import get_image_config, is_image_configured

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _call_image_api(keyword, style, width, height, count):
    """调用 AI 图片生成 API"""
    cfg = get_image_config()
    base_url = cfg.get("base_url", "").rstrip("/")
    api_key = cfg.get("api_key", "")
    model = cfg.get("model", "dall-e-3")

    style_hints = {
        "realistic": "photorealistic, 4k, detailed",
        "illustration": "flat illustration, vector style, colorful",
        "minimal": "minimalist, clean, simple, white background",
        "tech": "futuristic, technology, digital, blue neon",
        "cyberpunk": "cyberpunk, dystopian, neon lights, night city",
        "watercolor": "watercolor painting, soft colors, artistic",
        "anime": "anime style, manga, Japanese art style",
        "vintage": "vintage, retro, film grain, warm tones",
        "neon": "neon lights, synthwave, vibrant, dark background",
        "nature": "nature photography, landscape, organic, green",
    }
    hint = style_hints.get(style, style_hints["realistic"])

    prompt = f"{keyword}, {hint}, high quality"

    if "dall-e" in model.lower():
        size_map = {
            (800, 450): "1792x1024",
            (800, 600): "1024x1024",
            (600, 600): "1024x1024",
        }
        for (w, h), s in size_map.items():
            if abs(width - w) < 100 and abs(height - h) < 100:
                size = s
                break
        else:
            size = "1024x1024"

        images = []
        for i in range(count):
            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "n": 1,
                "size": size,
                "quality": "standard"
            }).encode("utf-8")

            req = request.Request(f"{base_url}/images/generations", data=payload, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {api_key}")

            try:
                with request.urlopen(req, timeout=90) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    for img_data in result.get("data", []):
                        images.append({
                            "id": f"ai_img_{int(time.time())}_{len(images)}",
                            "url": img_data.get("url", ""),
                            "width": width,
                            "height": height,
                            "style": style,
                            "keyword": keyword,
                            "source": "ai"
                        })
            except error.HTTPError as e:
                logger.error(f"图片 API HTTP 错误: {e.code} - {e.read().decode('utf-8', errors='replace')[:300]}")
            except Exception as e:
                logger.error(f"图片 API 调用失败: {e}")

        return images if images else None

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "n": min(count, 4),
        "size": f"{width}x{height}" if width <= 1792 and height <= 1792 else "1024x1024"
    }).encode("utf-8")

    req = request.Request(f"{base_url}/images/generations", data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            images = []
            for i, img_data in enumerate(result.get("data", [])):
                images.append({
                    "id": f"ai_img_{int(time.time())}_{i}",
                    "url": img_data.get("url", ""),
                    "width": width,
                    "height": height,
                    "style": style,
                    "keyword": keyword,
                    "source": "ai"
                })
            return images
    except error.HTTPError as e:
        logger.error(f"图片 API HTTP 错误: {e.code} - {e.read().decode('utf-8', errors='replace')[:300]}")
    except Exception as e:
        logger.error(f"图片 API 调用失败: {e}")
    return None


def generate_images(keyword="blog", style="realistic", width=800, height=600, count=2):
    """生成图片 — AI API 优先，回退 placeholder"""
    if is_image_configured():
        logger.info(f"使用 AI API 生成图片: {keyword[:30]} ({style})")
        ai_result = _call_image_api(keyword, style, width, height, count)
        if ai_result:
            return ai_result

    logger.info("使用 placeholder 生成图片")

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
            "keyword": keyword,
            "source": "placeholder"
        })

    return images


def save_uploaded_file(file_storage):
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
