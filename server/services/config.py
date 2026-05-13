"""
API 配置服务 — 读取/写入 server/config.json
支持前端配置面板动态修改
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

DEFAULT_CONFIG = {
    "ai": {
        "provider": "",
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    },
    "image": {
        "provider": "",
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "dall-e-3"
    }
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("API 配置已更新")


def get_ai_config():
    cfg = load_config()
    return cfg.get("ai", DEFAULT_CONFIG["ai"])


def get_image_config():
    cfg = load_config()
    return cfg.get("image", DEFAULT_CONFIG["image"])


def update_ai_config(ai_cfg):
    cfg = load_config()
    current = cfg.get("ai", {})
    current.update(ai_cfg)
    cfg["ai"] = current
    save_config(cfg)
    return cfg


def update_image_config(img_cfg):
    cfg = load_config()
    current = cfg.get("image", {})
    current.update(img_cfg)
    cfg["image"] = current
    save_config(cfg)
    return cfg


def is_ai_configured():
    ai_cfg = get_ai_config()
    return bool(ai_cfg.get("api_key") and ai_cfg.get("model"))


def is_image_configured():
    img_cfg = get_image_config()
    return bool(img_cfg.get("api_key"))
